#!/usr/bin/env python3
"""
Chatbot financiero con capacidad de análisis de datos CSV
"""

import pandas as pd
import requests
import json
import sys
import os
from datetime import datetime

class ChatbotCSV:
    def __init__(self):
        self.csv_path = "dataset/Prueba-Chatbot - BBDD.csv"
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Cargar datos del CSV"""
        try:
            print("📊 Cargando datos del CSV...")
            self.df = pd.read_csv(self.csv_path)
            print(f"✅ Datos cargados: {len(self.df)} registros")
            print(f"📋 Columnas: {list(self.df.columns)}")
        except Exception as e:
            print(f"❌ Error cargando CSV: {e}")
            self.df = None
    
    def analyze_data(self, query):
        """Analizar datos según la consulta"""
        if self.df is None:
            return "❌ No se pudieron cargar los datos del CSV"
        
        try:
            # Limpiar datos
            df = self.df.copy()
            df['Valor'] = pd.to_numeric(df['Valor'].astype(str).str.replace(',', ''), errors='coerce')
            
            # Análisis básico
            analysis = []
            
            # Estadísticas generales
            total_valor = df['Valor'].sum()
            analysis.append(f"💰 Valor total: ${total_valor:,.2f}")
            
            # Por país
            if 'Pais' in df.columns:
                pais_stats = df.groupby('Pais')['Valor'].sum().sort_values(ascending=False)
                analysis.append(f"\n🌍 Por país:\n{pais_stats.to_string()}")
            
            # Por negocio
            if 'Negocio' in df.columns:
                negocio_stats = df.groupby('Negocio')['Valor'].sum().sort_values(ascending=False)
                analysis.append(f"\n🏢 Por negocio:\n{negocio_stats.to_string()}")
            
            # Por concepto
            if 'Concepto' in df.columns:
                concepto_stats = df.groupby('Concepto')['Valor'].sum().sort_values(ascending=False)
                analysis.append(f"\n📊 Por concepto:\n{concepto_stats.to_string()}")
            
            # Por escenario
            if 'Escenario' in df.columns:
                escenario_stats = df.groupby('Escenario')['Valor'].sum().sort_values(ascending=False)
                analysis.append(f"\n🎯 Por escenario:\n{escenario_stats.to_string()}")
            
            # Top 10 registros por valor
            top_10 = df.nlargest(10, 'Valor')[['Pais', 'Negocio', 'Concepto', 'Valor']]
            analysis.append(f"\n🔝 Top 10 registros por valor:\n{top_10.to_string()}")
            
            return "\n".join(analysis)
            
        except Exception as e:
            return f"❌ Error en análisis: {e}"
    
    def get_insights(self, query):
        """Obtener insights específicos según la consulta"""
        if self.df is None:
            return "❌ No se pudieron cargar los datos del CSV"
        
        try:
            df = self.df.copy()
            df['Valor'] = pd.to_numeric(df['Valor'].astype(str).str.replace(',', ''), errors='coerce')
            
            insights = []
            
            # Análisis por palabras clave en la consulta
            query_lower = query.lower()
            
            if 'pais' in query_lower or 'país' in query_lower:
                pais_stats = df.groupby('Pais')['Valor'].sum().sort_values(ascending=False)
                insights.append(f"🌍 Análisis por país:\n{pais_stats.to_string()}")
            
            if 'negocio' in query_lower:
                negocio_stats = df.groupby('Negocio')['Valor'].sum().sort_values(ascending=False)
                insights.append(f"🏢 Análisis por negocio:\n{negocio_stats.to_string()}")
            
            if 'concepto' in query_lower:
                concepto_stats = df.groupby('Concepto')['Valor'].sum().sort_values(ascending=False)
                insights.append(f"📊 Análisis por concepto:\n{concepto_stats.to_string()}")
            
            if 'escenario' in query_lower:
                escenario_stats = df.groupby('Escenario')['Valor'].sum().sort_values(ascending=False)
                insights.append(f"🎯 Análisis por escenario:\n{escenario_stats.to_string()}")
            
            if 'cliente' in query_lower:
                cliente_data = df[df['Concepto'].str.contains('Cliente', case=False, na=False)]
                if not cliente_data.empty:
                    cliente_stats = cliente_data.groupby(['Pais', 'Negocio'])['Valor'].sum().sort_values(ascending=False)
                    insights.append(f"👥 Análisis de clientes:\n{cliente_stats.to_string()}")
            
            if 'tendencia' in query_lower or 'evolución' in query_lower:
                # Análisis por período si existe
                if 'Periodo' in df.columns:
                    periodo_stats = df.groupby('Periodo')['Valor'].sum().sort_values(ascending=False)
                    insights.append(f"📈 Análisis por período:\n{periodo_stats.to_string()}")
            
            if not insights:
                # Si no hay palabras clave específicas, dar análisis general
                insights.append(self.analyze_data(query))
            
            return "\n\n".join(insights)
            
        except Exception as e:
            return f"❌ Error en insights: {e}"
    
    def chat_with_openai(self, message):
        """Chat con OpenAI para consultas generales"""
        try:
            url = "https://finance-chat.loca.lt/chat/simple"
            data = {"message": message}
            
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result["response"]
                else:
                    return f"Error: {result.get('error', 'Error desconocido')}"
            else:
                return f"Error HTTP: {response.status_code}"
                
        except Exception as e:
            return f"Error de conexión: {str(e)}"
    
    def process_query(self, query):
        """Procesar consulta y determinar si necesita análisis de datos"""
        query_lower = query.lower()
        
        # Palabras clave que indican análisis de datos
        data_keywords = [
            'csv', 'datos', 'análisis', 'estadística', 'estadisticas',
            'pais', 'país', 'negocio', 'concepto', 'escenario',
            'cliente', 'valor', 'total', 'suma', 'promedio',
            'tendencia', 'evolución', 'distribución', 'ranking'
        ]
        
        # Verificar si la consulta requiere análisis de datos
        needs_data_analysis = any(keyword in query_lower for keyword in data_keywords)
        
        if needs_data_analysis:
            print("📊 Analizando datos del CSV...")
            data_analysis = self.get_insights(query)
            
            # Combinar con respuesta de OpenAI
            openai_response = self.chat_with_openai(f"Basándote en este análisis de datos: {data_analysis[:500]}... Responde la consulta: {query}")
            
            return f"📊 **Análisis de Datos:**\n{data_analysis}\n\n🤖 **Interpretación:**\n{openai_response}"
        else:
            # Consulta general, usar solo OpenAI
            return self.chat_with_openai(query)

def main():
    """Función principal"""
    print("🤖 Chatbot Financiero con Análisis de Datos CSV")
    print("=" * 60)
    
    chatbot = ChatbotCSV()
    
    if len(sys.argv) > 1:
        # Consulta desde línea de comandos
        query = " ".join(sys.argv[1:])
        print(f"🤔 Consultando: {query}")
        print("⏳ Procesando...")
        
        response = chatbot.process_query(query)
        print(f"\n🤖 Respuesta:\n{response}")
    else:
        # Mostrar ejemplos
        print("📋 Ejemplos de consultas:")
        print("1. '¿Cuál es el valor total por país?'")
        print("2. 'Analiza la distribución por negocio'")
        print("3. '¿Cuáles son los top 10 conceptos por valor?'")
        print("4. '¿Cómo se distribuyen los clientes por país?'")
        print("5. '¿Cuáles son las mejores estrategias de inversión?'")
        print("\n💡 Uso: python3 chatbot_csv.py 'Tu consulta aquí'")

if __name__ == "__main__":
    main()
