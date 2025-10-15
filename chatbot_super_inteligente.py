#!/usr/bin/env python3
"""
Chatbot Financiero Súper Inteligente - Maneja TODAS las combinaciones posibles del CSV
"""

import streamlit as st
import pandas as pd
import openai
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import re

# Configuración de la página
st.set_page_config(
    page_title="🤖 Chatbot Financiero Súper Inteligente",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

class SuperIntelligentFinancialChatbot:
    def __init__(self):
        self.df = None
        self.load_data()
        self.setup_openai()
        
        # Patrones de reconocimiento
        self.patterns = {
            'fechas': r'\b(0[7-9]|10)-01-2025\b',
            'periodos': r'\b(0[1-9]|1[0-2])-01-2025\b',
            'negocios': r'\b(PYME|CORP|Brokers|WK)\b',
            'conceptos': r'\b(Originacion|Resultado Comercial|Churn|Clientes|AD Rate|AD Revenue|Cost of Fund|Cost of Risk|Fund Rate|Gross Revenue|Int Rate|Interest Revenue|Margen Financiero|NTR|Originacion Prom|Rate All In|Risk Rate|Spread|Term)\b',
            'clasificaciones': r'\b(Active|New Active|Old Active|Old Operados|Total Operados|Churn Bruto|Churn Bruto Acum|Churn Bruto Act|Churn Bruto Rec|Churn Neto|Activacion|Recurrencia)\b',
            'cohortes': r'\b(2024|2025|<2024)\b',
            'escenarios': r'\b(Moderado|Ambicion)\b',
            'paises': r'\b(CL|Chile)\b'
        }
    
    def load_data(self):
        """Cargar datos del CSV"""
        try:
            self.df = pd.read_csv("dataset/Prueba-Chatbot - BBDD.csv", encoding='utf-8')
            self.df.columns = self.df.columns.str.strip()
            
            # Limpiar datos
            self.df['Valor'] = self.df['Valor'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            self.df['Valor'] = pd.to_numeric(self.df['Valor'], errors='coerce')
            self.df.dropna(subset=['Valor'], inplace=True)
            
            st.success(f"✅ Datos cargados: {len(self.df):,} registros")
            
        except Exception as e:
            st.error(f"❌ Error al cargar datos: {e}")
    
    def setup_openai(self):
        """Configurar OpenAI"""
        api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.warning("⚠️ OpenAI API Key no configurada. Solo análisis de datos disponible.")
            return
        
        openai.api_key = api_key
        self.openai_available = True
    
    def extract_filters(self, query):
        """Extraer filtros de la consulta usando patrones regex"""
        query_lower = query.lower()
        filters = {}
        
        # Extraer fechas
        fechas = re.findall(self.patterns['fechas'], query)
        if fechas:
            filters['Elaboracion'] = fechas[0]
        
        # Extraer períodos
        periodos = re.findall(self.patterns['periodos'], query)
        if periodos:
            filters['Periodo'] = periodos[0]
        
        # Extraer negocios
        negocios = re.findall(self.patterns['negocios'], query, re.IGNORECASE)
        if negocios:
            filters['Negocio'] = negocios[0]
        
        # Extraer conceptos
        conceptos = re.findall(self.patterns['conceptos'], query, re.IGNORECASE)
        if conceptos:
            filters['Concepto'] = conceptos[0]
        
        # Extraer clasificaciones
        clasificaciones = re.findall(self.patterns['clasificaciones'], query, re.IGNORECASE)
        if clasificaciones:
            filters['Clasificación'] = clasificaciones[0]
        
        # Extraer cohortes
        cohortes = re.findall(self.patterns['cohortes'], query)
        if cohortes:
            filters['Cohort_Act'] = cohortes[0]
        
        # Extraer escenarios
        escenarios = re.findall(self.patterns['escenarios'], query, re.IGNORECASE)
        if escenarios:
            filters['Escenario'] = escenarios[0]
        
        # Extraer países
        paises = re.findall(self.patterns['paises'], query, re.IGNORECASE)
        if paises:
            filters['Pais'] = 'CL'
        
        return filters
    
    def apply_filters(self, filters):
        """Aplicar filtros al DataFrame"""
        if not filters:
            return self.df
        
        filtered_df = self.df.copy()
        
        for column, value in filters.items():
            if column in filtered_df.columns:
                if column == 'Cohort_Act' and value == '<2024':
                    filtered_df = filtered_df[filtered_df[column] == '<2024']
                else:
                    filtered_df = filtered_df[filtered_df[column] == value]
        
        return filtered_df
    
    def analyze_data(self, query):
        """Análisis inteligente de datos"""
        if self.df is None:
            return "No hay datos disponibles para analizar."
        
        # Extraer filtros de la consulta
        filters = self.extract_filters(query)
        
        # Aplicar filtros
        filtered_df = self.apply_filters(filters)
        
        if len(filtered_df) == 0:
            return "No se encontraron datos con los filtros especificados."
        
        # Generar análisis
        analysis = self.generate_analysis(query, filtered_df, filters)
        
        return analysis
    
    def generate_analysis(self, query, df, filters):
        """Generar análisis basado en la consulta y filtros"""
        query_lower = query.lower()
        
        # Análisis básico
        total_value = df['Valor'].sum()
        total_records = len(df)
        
        analysis = f"📊 **Análisis de Datos:**\n"
        analysis += f"💰 Valor total: ${total_value:,.2f}\n"
        analysis += f"📊 Registros: {total_records:,}\n\n"
        
        # Mostrar filtros aplicados
        if filters:
            analysis += "🔍 **Filtros aplicados:**\n"
            for col, val in filters.items():
                analysis += f"  - {col}: {val}\n"
            analysis += "\n"
        
        # Análisis por negocio
        if 'Negocio' in df.columns and 'Valor' in df.columns:
            negocio_analysis = df.groupby('Negocio')['Valor'].sum().sort_values(ascending=False)
            analysis += "🏢 **Por Negocio:**\n"
            for negocio, valor in negocio_analysis.items():
                porcentaje = (valor / total_value) * 100 if total_value > 0 else 0
                analysis += f"  - {negocio}: ${valor:,.2f} ({porcentaje:.1f}%)\n"
            analysis += "\n"
        
        # Análisis por concepto
        if 'Concepto' in df.columns and 'Valor' in df.columns:
            concepto_analysis = df.groupby('Concepto')['Valor'].sum().sort_values(ascending=False)
            analysis += "📋 **Por Concepto:**\n"
            for concepto, valor in concepto_analysis.items():
                porcentaje = (valor / total_value) * 100 if total_value > 0 else 0
                analysis += f"  - {concepto}: ${valor:,.2f} ({porcentaje:.1f}%)\n"
            analysis += "\n"
        
        # Análisis por cohorte
        if 'Cohort_Act' in df.columns and 'Valor' in df.columns:
            cohorte_analysis = df.groupby('Cohort_Act')['Valor'].sum().sort_values(ascending=False)
            analysis += "📈 **Por Cohorte:**\n"
            for cohorte, valor in cohorte_analysis.items():
                porcentaje = (valor / total_value) * 100 if total_value > 0 else 0
                analysis += f"  - {cohorte}: ${valor:,.2f} ({porcentaje:.1f}%)\n"
            analysis += "\n"
        
        # Análisis por clasificación
        if 'Clasificación' in df.columns and 'Valor' in df.columns:
            clasif_analysis = df.groupby('Clasificación')['Valor'].sum().sort_values(ascending=False)
            analysis += "🏷️ **Por Clasificación:**\n"
            for clasif, valor in clasif_analysis.items():
                porcentaje = (valor / total_value) * 100 if total_value > 0 else 0
                analysis += f"  - {clasif}: ${valor:,.2f} ({porcentaje:.1f}%)\n"
            analysis += "\n"
        
        # Análisis por escenario
        if 'Escenario' in df.columns and 'Valor' in df.columns:
            escenario_analysis = df.groupby('Escenario')['Valor'].sum().sort_values(ascending=False)
            analysis += "🎯 **Por Escenario:**\n"
            for escenario, valor in escenario_analysis.items():
                porcentaje = (valor / total_value) * 100 if total_value > 0 else 0
                analysis += f"  - {escenario}: ${valor:,.2f} ({porcentaje:.1f}%)\n"
            analysis += "\n"
        
        # Análisis por período
        if 'Periodo' in df.columns and 'Valor' in df.columns:
            periodo_analysis = df.groupby('Periodo')['Valor'].sum().sort_values(ascending=False)
            analysis += "📅 **Por Período:**\n"
            for periodo, valor in periodo_analysis.items():
                porcentaje = (valor / total_value) * 100 if total_value > 0 else 0
                analysis += f"  - {periodo}: ${valor:,.2f} ({porcentaje:.1f}%)\n"
            analysis += "\n"
        
        return analysis
    
    def get_chat_response(self, user_message):
        """Obtener respuesta del chatbot"""
        # Primero intentar análisis de datos
        data_analysis = self.analyze_data(user_message)
        if data_analysis:
            return data_analysis
        
        # Si no hay análisis de datos, usar OpenAI
        if not hasattr(self, 'openai_available') or not self.openai_available:
            return "Solo análisis de datos disponible. Configura OpenAI API Key para consultas generales."
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente financiero experto. Ayudas con consultas sobre finanzas, inversiones y análisis de datos financieros."},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1000,
                temperature=0.5
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error al comunicarse con OpenAI: {e}"

def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 Chatbot Financiero Súper Inteligente</h1>', unsafe_allow_html=True)
    
    # Inicializar chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = SuperIntelligentFinancialChatbot()
        st.session_state.messages = []
    
    chatbot = st.session_state.chatbot
    
    # Sidebar con información
    with st.sidebar:
        st.header("📊 Información de Datos")
        
        if chatbot.df is not None:
            st.metric("Total Registros", f"{len(chatbot.df):,}")
            st.metric("Valor Total", f"${chatbot.df['Valor'].sum():,.0f}")
            
            if 'Pais' in chatbot.df.columns:
                st.write("**Países:**")
                st.write(chatbot.df['Pais'].unique())
            
            if 'Negocio' in chatbot.df.columns:
                st.write("**Negocios:**")
                st.write(chatbot.df['Negocio'].unique())
        
        st.header("💡 Consultas Sugeridas")
        st.write("• 'Originacion PYME 08-01-2025'")
        st.write("• 'Resultado Comercial CORP 2024'")
        st.write("• 'Churn WK Moderado'")
        st.write("• 'Clientes por cohorte'")
        st.write("• 'Análisis por escenario'")
        st.write("• 'Valor total por concepto'")
        st.write("• 'Distribución por negocio'")
        st.write("• 'Tendencia por período'")
    
    # Chat interface
    st.header("💬 Chat")
    
    # Mostrar mensajes anteriores
    for message in st.session_state.messages:
        with st.container():
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message">👤 **Tú:** {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message bot-message">🤖 **Bot:** {message["content"]}</div>', unsafe_allow_html=True)
    
    # Input de usuario
    user_input = st.text_input("Escribe tu consulta:", key="user_input")
    
    if st.button("Enviar") and user_input:
        # Agregar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Obtener respuesta
        with st.spinner("Procesando..."):
            response = chatbot.get_chat_response(user_input)
        
        # Agregar respuesta del bot
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Recargar la página para mostrar la respuesta
        st.rerun()
    
    # Visualizaciones
    if chatbot.df is not None:
        st.header("📊 Visualizaciones")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'Negocio' in chatbot.df.columns and 'Valor' in chatbot.df.columns:
                negocio_data = chatbot.df.groupby('Negocio')['Valor'].sum().sort_values(ascending=False)
                fig = px.pie(values=negocio_data.values, names=negocio_data.index, title="Distribución por Negocio")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'Cohort_Act' in chatbot.df.columns and 'Valor' in chatbot.df.columns:
                cohorte_data = chatbot.df.groupby('Cohort_Act')['Valor'].sum().sort_values(ascending=False)
                fig = px.bar(x=cohorte_data.index, y=cohorte_data.values, title="Valor por Cohorte")
                st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
