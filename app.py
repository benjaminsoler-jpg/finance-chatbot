#!/usr/bin/env python3
"""
Chatbot Financiero con Análisis de CSV - Streamlit App
Optimizado para deployment online
"""

import streamlit as st
import pandas as pd
import openai
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(
    page_title="🤖 Chatbot Financiero",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .bot-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
</style>
""", unsafe_allow_html=True)

class FinancialChatbot:
    def __init__(self):
        self.df = None
        self.load_data()
        self.setup_openai()
    
    def load_data(self):
        """Cargar datos del CSV"""
        try:
            # Intentar cargar desde diferentes ubicaciones
            csv_paths = [
                "dataset/Prueba-Chatbot - BBDD.csv",
                "Prueba-Chatbot - BBDD.csv",
                "data.csv"
            ]
            
            for path in csv_paths:
                try:
                    self.df = pd.read_csv(path, encoding='utf-8')
                    break
                except FileNotFoundError:
                    continue
            
            if self.df is None:
                st.error("❌ No se pudo cargar el archivo CSV")
                return
            
            # Limpiar datos
            self.df.columns = self.df.columns.str.strip()
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
    
    def analyze_data(self, query: str) -> str:
        """Análisis de datos del CSV"""
        if self.df is None:
            return "No hay datos disponibles para analizar."
        
        query_lower = query.lower()
        
        # Análisis por negocio
        if "negocio" in query_lower or "business" in query_lower:
            if 'Negocio' in self.df.columns and 'Valor' in self.df.columns:
                negocio_analysis = self.df.groupby('Negocio')['Valor'].sum().sort_values(ascending=False)
                return f"📊 **Análisis por Negocio:**\n{negocio_analysis.to_string()}"
        
        # Análisis por país
        elif "país" in query_lower or "pais" in query_lower or "country" in query_lower:
            if 'Pais' in self.df.columns and 'Valor' in self.df.columns:
                pais_analysis = self.df.groupby('Pais')['Valor'].sum().sort_values(ascending=False)
                return f"🌍 **Análisis por País:**\n{pais_analysis.to_string()}"
        
        # Análisis por concepto
        elif "concepto" in query_lower or "concept" in query_lower:
            if 'Concepto' in self.df.columns and 'Valor' in self.df.columns:
                concepto_analysis = self.df.groupby('Concepto')['Valor'].sum().sort_values(ascending=False)
                return f"📋 **Análisis por Concepto:**\n{concepto_analysis.to_string()}"
        
        # Análisis por cohorte
        elif "cohorte" in query_lower or "cohort" in query_lower:
            if 'Cohort_Act' in self.df.columns and 'Valor' in self.df.columns:
                cohorte_analysis = self.df.groupby('Cohort_Act')['Valor'].sum().sort_values(ascending=False)
                return f"📈 **Análisis por Cohorte:**\n{cohorte_analysis.to_string()}"
        
        # Análisis específico por fecha
        elif "08-01-2025" in query_lower or "elaboración" in query_lower:
            return self.analyze_specific_date()
        
        # Resumen general
        elif "resumen" in query_lower or "summary" in query_lower or "total" in query_lower:
            return self.get_summary()
        
        return ""
    
    def analyze_specific_date(self) -> str:
        """Análisis específico para 08-01-2025"""
        if self.df is None:
            return "No hay datos disponibles."
        
        # Filtrar datos específicos
        filtro = (
            (self.df['Elaboracion'] == '08-01-2025') &
            (self.df['Periodo'] == '08-01-2025') &
            (self.df['Pais'] == 'CL') &
            (self.df['Escenario'] == 'Moderado')
        )
        
        datos = self.df[filtro]
        
        if len(datos) == 0:
            return "No se encontraron datos para los filtros especificados."
        
        # Análisis por negocio y cohorte
        resultado = datos.groupby(['Negocio', 'Cohort_Act'])['Valor'].sum().reset_index()
        total = datos['Valor'].sum()
        
        analysis = f"📊 **Resultado Comercial 08-01-2025:**\n"
        analysis += f"💰 Valor total: ${total:,.2f}\n"
        analysis += f"📊 Registros: {len(datos):,}\n\n"
        
        for negocio in resultado['Negocio'].unique():
            negocio_data = resultado[resultado['Negocio'] == negocio]
            total_negocio = negocio_data['Valor'].sum()
            analysis += f"🏢 **{negocio}:** ${total_negocio:,.2f}\n"
            
            for _, row in negocio_data.iterrows():
                cohorte = row['Cohort_Act'] if pd.notna(row['Cohort_Act']) else 'Sin cohorte'
                valor = row['Valor']
                porcentaje = (valor / total_negocio) * 100 if total_negocio > 0 else 0
                analysis += f"  📈 {cohorte}: ${valor:,.2f} ({porcentaje:.1f}%)\n"
            analysis += "\n"
        
        return analysis
    
    def get_summary(self) -> str:
        """Resumen general de los datos"""
        if self.df is None:
            return "No hay datos disponibles."
        
        total_value = self.df['Valor'].sum()
        total_records = len(self.df)
        
        summary = f"📊 **Resumen General:**\n"
        summary += f"💰 Valor total: ${total_value:,.2f}\n"
        summary += f"📊 Total registros: {total_records:,}\n"
        
        if 'Pais' in self.df.columns:
            countries = self.df['Pais'].nunique()
            summary += f"🌍 Países: {countries}\n"
        
        if 'Negocio' in self.df.columns:
            businesses = self.df['Negocio'].nunique()
            summary += f"🏢 Negocios: {businesses}\n"
        
        if 'Concepto' in self.df.columns:
            concepts = self.df['Concepto'].nunique()
            summary += f"📋 Conceptos: {concepts}\n"
        
        return summary
    
    def get_chat_response(self, user_message: str) -> str:
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
    st.markdown('<h1 class="main-header">🤖 Chatbot Financiero con Análisis de Datos</h1>', unsafe_allow_html=True)
    
    # Inicializar chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = FinancialChatbot()
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
        st.write("• 'Análisis por negocio'")
        st.write("• 'Resumen general'")
        st.write("• 'Análisis por país'")
        st.write("• 'Resultado Comercial 08-01-2025'")
        st.write("• '¿Cuáles son las mejores estrategias de inversión?'")
    
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
        
        # Limpiar input
        st.session_state.user_input = ""
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
