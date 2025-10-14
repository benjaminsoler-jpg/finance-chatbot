#!/usr/bin/env python3
"""
Chatbot Financiero con Gradio - Optimizado para Hugging Face Spaces
"""

import gradio as gr
import pandas as pd
import openai
import os
from datetime import datetime

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
                print("❌ No se pudo cargar el archivo CSV")
                return
            
            # Limpiar datos
            self.df.columns = self.df.columns.str.strip()
            self.df['Valor'] = self.df['Valor'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            self.df['Valor'] = pd.to_numeric(self.df['Valor'], errors='coerce')
            self.df.dropna(subset=['Valor'], inplace=True)
            
            print(f"✅ Datos cargados: {len(self.df):,} registros")
            
        except Exception as e:
            print(f"❌ Error al cargar datos: {e}")
    
    def setup_openai(self):
        """Configurar OpenAI"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️ OpenAI API Key no configurada. Solo análisis de datos disponible.")
            self.openai_available = False
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
        if not self.openai_available:
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

# Inicializar chatbot
chatbot = FinancialChatbot()

def chat_function(message, history):
    """Función de chat para Gradio"""
    response = chatbot.get_chat_response(message)
    return response

# Crear interfaz Gradio
with gr.Blocks(title="🤖 Chatbot Financiero", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 Chatbot Financiero con Análisis de Datos")
    gr.Markdown("Pregunta sobre tus datos financieros o consultas generales de finanzas.")
    
    with gr.Row():
        with gr.Column(scale=3):
            chatbot_interface = gr.ChatInterface(
                fn=chat_function,
                title="💬 Chat",
                description="Escribe tu consulta aquí",
                examples=[
                    "Análisis por negocio",
                    "Resumen general",
                    "Resultado Comercial 08-01-2025",
                    "¿Cuáles son las mejores estrategias de inversión?"
                ]
            )
        
        with gr.Column(scale=1):
            gr.Markdown("### 📊 Información de Datos")
            if chatbot.df is not None:
                gr.Markdown(f"**Total Registros:** {len(chatbot.df):,}")
                gr.Markdown(f"**Valor Total:** ${chatbot.df['Valor'].sum():,.0f}")
                
                if 'Pais' in chatbot.df.columns:
                    gr.Markdown("**Países:**")
                    gr.Markdown(", ".join(chatbot.df['Pais'].unique()))
                
                if 'Negocio' in chatbot.df.columns:
                    gr.Markdown("**Negocios:**")
                    gr.Markdown(", ".join(chatbot.df['Negocio'].unique()))
            else:
                gr.Markdown("No hay datos disponibles")

if __name__ == "__main__":
    demo.launch(share=True)
