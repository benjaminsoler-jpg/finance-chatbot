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
        
        # Patrones de reconocimiento para análisis inteligente
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
            # Convertir a numérico: quitar comas, convertir a float
            self.df['Valor'] = self.df['Valor'].astype(str).str.replace(',', '')
            self.df['Valor'] = pd.to_numeric(self.df['Valor'], errors='coerce').fillna(0)
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
        import re
        query_lower = query.lower()
        filters = {}
        
        # Extraer fechas (solo para Elaboracion) - patrón más específico
        if 'elaboracion' in query_lower or 'elaboración' in query_lower:
            # Buscar el patrón "Elaboracion XX-01-2025"
            elaboracion_match = re.search(r'elaboracion\s+(\d{2})-01-2025', query_lower)
            if elaboracion_match:
                filters['Elaboracion'] = elaboracion_match.group(1) + '-01-2025'
        
        # Extraer períodos (solo para Periodo) - patrón más específico
        if 'periodo' in query_lower or 'período' in query_lower:
            # Buscar el patrón "periodo XX-01-2025"
            periodo_match = re.search(r'periodo\s+(\d{2})-01-2025', query_lower)
            if periodo_match:
                filters['Periodo'] = periodo_match.group(1) + '-01-2025'
        
        # Extraer lógica de "últimos N períodos"
        if 'ultimos' in query_lower and ('periodos' in query_lower or 'períodos' in query_lower):
            ultimos_match = re.search(r'ultimos?\s+(\d+)\s+periodos?', query_lower)
            if ultimos_match:
                filters['ultimos_periodos'] = int(ultimos_match.group(1))
        
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
        
        # Extraer cohortes (solo si se menciona explícitamente)
        if 'cohorte' in query_lower or 'cohort' in query_lower:
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
        
        # Manejar lógica especial de "últimos N períodos"
        if 'ultimos_periodos' in filters and 'Elaboracion' in filters:
            ultimos_periodos = filters['ultimos_periodos']
            elaboracion = filters['Elaboracion']
            
            # Calcular períodos anteriores
            periodos_anteriores = self._get_periodos_anteriores(elaboracion, ultimos_periodos)
            
            # Filtrar por períodos específicos
            filtered_df = filtered_df[filtered_df['Periodo'].isin(periodos_anteriores)]
            
            # Remover el filtro especial para no aplicarlo dos veces
            filters = {k: v for k, v in filters.items() if k != 'ultimos_periodos'}
        
        for column, value in filters.items():
            if column in filtered_df.columns:
                if column == 'Cohort_Act' and value == '<2024':
                    filtered_df = filtered_df[filtered_df[column] == '<2024']
                else:
                    filtered_df = filtered_df[filtered_df[column] == value]
        
        return filtered_df
    
    def _get_periodos_anteriores(self, elaboracion, cantidad):
        """Calcular los últimos N períodos anteriores a una elaboración"""
        import datetime
        
        # Extraer mes de la elaboración (formato: MM-01-2025)
        mes_elaboracion = int(elaboracion.split('-')[0])
        
        # Calcular períodos anteriores
        periodos = []
        for i in range(cantidad):
            mes_anterior = mes_elaboracion - i - 1
            if mes_anterior <= 0:
                mes_anterior += 12
            periodos.append(f"{mes_anterior:02d}-01-2025")
        
        return periodos
    
    def analyze_data(self, query: str) -> str:
        """Análisis inteligente de datos del CSV"""
        if self.df is None:
            return "No hay datos disponibles para analizar."
        
        # Extraer filtros de la consulta
        filters = self.extract_filters(query)
        
        # Aplicar filtros
        filtered_df = self.apply_filters(filters)
        
        # Si no hay datos con filtros estrictos, intentar con filtros más flexibles
        if len(filtered_df) == 0 and filters:
            # Intentar con menos filtros
            for key in list(filters.keys()):
                temp_filters = filters.copy()
                del temp_filters[key]
                temp_df = self.apply_filters(temp_filters)
                if len(temp_df) > 0:
                    filtered_df = temp_df
                    break
        
        # Si aún no hay datos, usar todos los datos
        if len(filtered_df) == 0:
            filtered_df = self.df.copy()
        
        # Generar análisis
        analysis = self.generate_analysis(query, filtered_df, filters)
        
        return analysis
    
    def is_financial_query(self, query: str) -> bool:
        """Detectar si la consulta es financiera o general"""
        financial_keywords = [
            'originacion', 'originación', 'gross revenue', 'margen financiero',
            'resultado comercial', 'churn', 'clientes', 'ad rate', 'ad revenue',
            'cost of fund', 'cost of risk', 'fund rate', 'int rate', 'interest revenue',
            'ntr', 'rate all in', 'risk rate', 'spread', 'term', 'elaboracion', 'elaboración',
            'periodo', 'período', 'negocio', 'concepto', 'clasificación', 'cohort',
            'escenario', 'pais', 'país', 'valor', 'análisis', 'analisis', 'datos',
            'financiero', 'financiera', 'comercial', 'ventas', 'ingresos', 'costos',
            'margen', 'rentabilidad', 'inversión', 'inversion', 'como me fue', 'como nos fue',
            'ultimos', 'últimos', 'ultimo', 'último', 'meses', 'mes', 'comparar', 'predicción', 'prediccion'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in financial_keywords)
    
    def analyze_performance_comparison(self, query: str) -> str:
        """Análisis de comparación de rendimiento: predicción vs realidad"""
        import re
        
        # Extraer elaboración de la consulta
        elaboracion_match = re.search(r'elaboraci[oó]n\s+(\d{2})-01-2025', query.lower())
        if not elaboracion_match:
            return None
        
        elaboracion = elaboracion_match.group(1) + '-01-2025'
        
        # Calcular elaboración anterior (predicción)
        mes_actual = int(elaboracion.split('-')[0])
        mes_anterior = mes_actual - 1
        if mes_anterior <= 0:
            mes_anterior = 12
        elaboracion_anterior = f"{mes_anterior:02d}-01-2025"
        
        # Variables específicas para comparar
        variables_comparacion = {
            'concepto': ['Rate All In', 'Originacion Prom', 'Term', 'Risk Rate', 'Fund Rate'],
            'clasificacion': ['New Active', 'Churn Bruto', 'Resucitados']
        }
        
        analysis = f"📊 **Análisis de Rendimiento: Predicción vs Realidad**\n"
        analysis += f"🎯 **Elaboración analizada:** {elaboracion}\n"
        analysis += f"📈 **Predicción:** {elaboracion_anterior} (Periodo {elaboracion})\n"
        analysis += f"📉 **Realidad:** {elaboracion} (Periodo {elaboracion})\n\n"
        
        # Comparar por Concepto
        analysis += "📋 **Comparación por Concepto:**\n"
        for concepto in variables_comparacion['concepto']:
            # Datos de predicción
            pred_data = self.df[
                (self.df['Elaboracion'] == elaboracion_anterior) & 
                (self.df['Periodo'] == elaboracion) & 
                (self.df['Concepto'] == concepto)
            ]
            
            # Datos de realidad
            real_data = self.df[
                (self.df['Elaboracion'] == elaboracion) & 
                (self.df['Periodo'] == elaboracion) & 
                (self.df['Concepto'] == concepto)
            ]
            
            if len(pred_data) > 0 and len(real_data) > 0:
                pred_valor = pred_data['Valor'].sum()
                real_valor = real_data['Valor'].sum()
                
                if pred_valor != 0:
                    diferencia = real_valor - pred_valor
                    porcentaje = (diferencia / pred_valor) * 100
                    
                    if diferencia > 0:
                        emoji = "📈"
                        tendencia = "mejor"
                    else:
                        emoji = "📉"
                        tendencia = "peor"
                    
                    analysis += f"  {emoji} **{concepto}:**\n"
                    analysis += f"    - Predicción: ${pred_valor:,}\n"
                    analysis += f"    - Realidad: ${real_valor:,}\n"
                    analysis += f"    - Diferencia: ${diferencia:,} ({porcentaje:+.1f}%) - {tendencia}\n\n"
        
        # Comparar por Clasificación
        analysis += "🏷️ **Comparación por Clasificación:**\n"
        for clasificacion in variables_comparacion['clasificacion']:
            # Datos de predicción
            pred_data = self.df[
                (self.df['Elaboracion'] == elaboracion_anterior) & 
                (self.df['Periodo'] == elaboracion) & 
                (self.df['Clasificación'] == clasificacion)
            ]
            
            # Datos de realidad
            real_data = self.df[
                (self.df['Elaboracion'] == elaboracion) & 
                (self.df['Periodo'] == elaboracion) & 
                (self.df['Clasificación'] == clasificacion)
            ]
            
            if len(pred_data) > 0 and len(real_data) > 0:
                pred_valor = pred_data['Valor'].sum()
                real_valor = real_data['Valor'].sum()
                
                if pred_valor != 0:
                    diferencia = real_valor - pred_valor
                    porcentaje = (diferencia / pred_valor) * 100
                    
                    if diferencia > 0:
                        emoji = "📈"
                        tendencia = "mejor"
                    else:
                        emoji = "📉"
                        tendencia = "peor"
                    
                    analysis += f"  {emoji} **{clasificacion}:**\n"
                    analysis += f"    - Predicción: ${pred_valor:,}\n"
                    analysis += f"    - Realidad: ${real_valor:,}\n"
                    analysis += f"    - Diferencia: ${diferencia:,} ({porcentaje:+.1f}%) - {tendencia}\n\n"
        
        return analysis
    
    def analyze_last_months_performance(self, query: str) -> str:
        """Análisis de rendimiento de los últimos N meses"""
        import re
        
        # Extraer elaboración y cantidad de meses
        elaboracion_match = re.search(r'elaboraci[oó]n\s+(\d{2})-01-2025', query.lower())
        
        # Buscar "ultimos N meses" o "N ultimo(s) meses"
        meses_match = re.search(r'ultimos?\s+(\d+)\s+meses?', query.lower())
        if not meses_match:
            meses_match = re.search(r'(\d+)\s+ultimos?\s+meses?', query.lower())
        
        if not elaboracion_match:
            return None
        
        elaboracion = elaboracion_match.group(1) + '-01-2025'
        meses = int(meses_match.group(1)) if meses_match else 3
        
        # Extraer filtros adicionales
        escenario = None
        if 'moderado' in query.lower():
            escenario = 'Moderado'
        elif 'ambicion' in query.lower():
            escenario = 'Ambicion'
        
        # Calcular períodos anteriores
        mes_actual = int(elaboracion.split('-')[0])
        periodos = []
        for i in range(meses):
            mes_anterior = mes_actual - i - 1
            if mes_anterior <= 0:
                mes_anterior += 12
            periodos.append(f"{mes_anterior:02d}-01-2025")
        
        analysis = f"📊 **Rendimiento de los Últimos {meses} Meses**\n"
        analysis += f"🎯 **Elaboración base:** {elaboracion}\n"
        analysis += f"📅 **Períodos analizados:** {', '.join(periodos)}\n"
        if escenario:
            analysis += f"🎯 **Escenario:** {escenario}\n"
        analysis += "\n"
        
        # Variables clave para análisis
        variables_clave = ['Rate All In', 'Originacion Prom', 'Term', 'Risk Rate', 'Fund Rate']
        
        # Variables que son rates (porcentajes) - no se suman, se muestran por clasificación/cohort
        rate_variables = ['Rate All In', 'Risk Rate', 'Fund Rate']
        
        # Variables que se suman (valores monetarios)
        sum_variables = ['Originacion Prom', 'Term']
        
        # Obtener negocios únicos
        negocios = ['PYME', 'CORP', 'Brokers', 'WK']
        
        for negocio in negocios:
            analysis += f"🏢 **{negocio}:**\n\n"
            
            # Primero mostrar rates (porcentajes)
            analysis += "  📊 **Rates (Porcentajes):**\n"
            for variable in rate_variables:
                analysis += f"    📈 **{variable}:**\n"
                
                for periodo in periodos:
                    # Construir filtro base
                    filtro = (
                        (self.df['Elaboracion'] == elaboracion) & 
                        (self.df['Periodo'] == periodo) & 
                        (self.df['Concepto'] == variable) &
                        (self.df['Negocio'] == negocio)
                    )
                    
                    # Agregar filtro de escenario si se especifica
                    if escenario:
                        filtro = filtro & (self.df['Escenario'] == escenario)
                    
                    data = self.df[filtro]
                    
                    if len(data) > 0:
                        analysis += f"      • {periodo}:\n"
                        # Agrupar por clasificación y cohort
                        grouped = data.groupby(['Clasificación', 'Cohort_Act'])['Valor'].first().reset_index()
                        for _, row in grouped.iterrows():
                            clasificacion = row['Clasificación'] if pd.notna(row['Clasificación']) else 'Sin clasificación'
                            cohort = row['Cohort_Act'] if pd.notna(row['Cohort_Act']) else 'Sin cohort'
                            valor = row['Valor']
                            analysis += f"        - {clasificacion} ({cohort}): {valor*100:.2f}%\n"
                    else:
                        analysis += f"      • {periodo}: Sin datos\n"
                analysis += "\n"
            
            # Luego mostrar variables monetarias
            analysis += "  💰 **Valores Monetarios:**\n"
            for variable in sum_variables:
                analysis += f"    📈 **{variable}:**\n"
                
                valores_por_periodo = []
                for periodo in periodos:
                    # Construir filtro base
                    filtro = (
                        (self.df['Elaboracion'] == elaboracion) & 
                        (self.df['Periodo'] == periodo) & 
                        (self.df['Concepto'] == variable) &
                        (self.df['Negocio'] == negocio)
                    )
                    
                    # Agregar filtro de escenario si se especifica
                    if escenario:
                        filtro = filtro & (self.df['Escenario'] == escenario)
                    
                    data = self.df[filtro]
                    
                    if len(data) > 0:
                        valor = data['Valor'].sum()
                        valores_por_periodo.append(valor)
                        analysis += f"      • {periodo}: ${valor:,.0f}\n"
                    else:
                        analysis += f"      • {periodo}: Sin datos\n"
                
                if len(valores_por_periodo) > 1:
                    # Calcular tendencia
                    primer_valor = valores_por_periodo[0]
                    ultimo_valor = valores_por_periodo[-1]
                    
                    if primer_valor != 0:
                        cambio = ultimo_valor - primer_valor
                        porcentaje = (cambio / primer_valor) * 100
                        
                        if cambio > 0:
                            tendencia = "📈 Creciendo"
                        elif cambio < 0:
                            tendencia = "📉 Decreciendo"
                        else:
                            tendencia = "➡️ Estable"
                        
                        analysis += f"      **Tendencia:** {tendencia} ({porcentaje:+.1f}%)\n"
                analysis += "\n"
            
            analysis += "---\n\n"
        
        # Si se menciona "Resultado Comercial", agregar análisis por negocio
        if 'resultado comercial' in query.lower():
            analysis += "🏢 **Análisis por Negocio - Resultado Comercial:**\n"
            
            for negocio in self.df['Negocio'].unique():
                if pd.isna(negocio):
                    continue
                    
                analysis += f"\n📊 **{negocio}:**\n"
                
                for periodo in periodos:
                    # Construir filtro para Resultado Comercial por negocio
                    filtro = (
                        (self.df['Elaboracion'] == elaboracion) & 
                        (self.df['Periodo'] == periodo) & 
                        (self.df['Concepto'] == 'Resultado Comercial') &
                        (self.df['Negocio'] == negocio)
                    )
                    
                    # Agregar filtro de escenario si se especifica
                    if escenario:
                        filtro = filtro & (self.df['Escenario'] == escenario)
                    
                    data = self.df[filtro]
                    
                    if len(data) > 0:
                        valor = data['Valor'].sum()
                        analysis += f"  - {periodo}: ${valor:,}\n"
                    else:
                        analysis += f"  - {periodo}: Sin datos\n"
        
        return analysis
    
    def generate_analysis(self, query, df, filters):
        """Generar análisis basado en la consulta y filtros"""
        query_lower = query.lower()
        
        # Análisis básico
        total_value = df['Valor'].sum()
        total_records = len(df)
        
        analysis = f"📊 **Análisis de Datos:**\n"
        analysis += f"💰 Valor total: ${total_value:,}\n"
        analysis += f"📊 Registros: {total_records:,}\n\n"
        
        # Mostrar filtros aplicados
        if filters:
            analysis += "🔍 **Filtros aplicados:**\n"
            for col, val in filters.items():
                analysis += f"  - {col}: {val}\n"
            analysis += "\n"
        
        # Si no se encontraron datos con filtros exactos, mostrar datos relacionados
        if len(df) != len(self.df):
            analysis += "ℹ️ **Nota:** Se muestran datos relacionados ya que no se encontraron registros con todos los filtros exactos.\n\n"
        
        # Verificar si el concepto específico tiene valores válidos
        if 'Concepto' in filters:
            concepto_especifico = filters['Concepto']
            concepto_data = df[df['Concepto'].str.contains(concepto_especifico, case=False, na=False)]
            if len(concepto_data) > 0:
                # Verificar si hay valores no nulos para este concepto
                valores_validos = concepto_data['Valor'].dropna()
                if len(valores_validos) == 0:
                    analysis += f"⚠️ **Advertencia:** El concepto '{concepto_especifico}' no tiene valores válidos (todos son nulos).\n\n"
        
        # Análisis por negocio
        if 'Negocio' in df.columns and 'Valor' in df.columns:
            negocio_analysis = df.groupby('Negocio')['Valor'].sum().sort_values(ascending=False)
            analysis += "🏢 **Por Negocio:**\n"
            for negocio, valor in negocio_analysis.items():
                porcentaje = (valor / total_value) * 100 if total_value > 0 else 0
                analysis += f"  - {negocio}: ${valor:,} ({porcentaje:.1f}%)\n"
            analysis += "\n"
        
        # Análisis por concepto
        if 'Concepto' in df.columns and 'Valor' in df.columns:
            concepto_analysis = df.groupby('Concepto')['Valor'].sum().sort_values(ascending=False)
            analysis += "📋 **Por Concepto:**\n"
            for concepto, valor in concepto_analysis.items():
                porcentaje = (valor / total_value) * 100 if total_value > 0 else 0
                analysis += f"  - {concepto}: ${valor:,} ({porcentaje:.1f}%)\n"
            analysis += "\n"
            
            # Análisis específico de Originacion si se menciona
            if 'originacion' in query.lower() or 'originación' in query.lower():
                originacion_data = df[df['Concepto'].str.contains('Originacion', case=False, na=False)]
                if len(originacion_data) > 0:
                    originacion_total = originacion_data['Valor'].sum()
                    analysis += "🎯 **Análisis Específico de Originación:**\n"
                    analysis += f"💰 Valor total de Originación: ${originacion_total:,.2f}\n"
                    analysis += f"📊 Registros de Originación: {len(originacion_data):,}\n"
                    
                    # Debug: mostrar algunos valores para verificar
                    if originacion_total == 0:
                        analysis += f"⚠️ **Debug:** Primeros 5 valores de Originación: {originacion_data['Valor'].head().tolist()}\n"
                        analysis += f"⚠️ **Debug:** Tipos de datos: {originacion_data['Valor'].dtype}\n"
                    analysis += "\n"
                    
                    # Por negocio
                    if 'Negocio' in originacion_data.columns:
                        orig_negocio = originacion_data.groupby('Negocio')['Valor'].sum().sort_values(ascending=False)
                        analysis += "🏢 **Originación por Negocio:**\n"
                        for negocio, valor in orig_negocio.items():
                            porcentaje = (valor / originacion_total) * 100 if originacion_total > 0 else 0
                            analysis += f"  - {negocio}: ${valor:,} ({porcentaje:.1f}%)\n"
                        analysis += "\n"
                    
                    # Por cohorte
                    if 'Cohort_Act' in originacion_data.columns:
                        orig_cohorte = originacion_data.groupby('Cohort_Act')['Valor'].sum().sort_values(ascending=False)
                        analysis += "📈 **Originación por Cohorte:**\n"
                        for cohorte, valor in orig_cohorte.items():
                            porcentaje = (valor / originacion_total) * 100 if originacion_total > 0 else 0
                            analysis += f"  - {cohorte}: ${valor:,} ({porcentaje:.1f}%)\n"
                        analysis += "\n"
        
        # Análisis por cohorte
        if 'Cohort_Act' in df.columns and 'Valor' in df.columns:
            cohorte_analysis = df.groupby('Cohort_Act')['Valor'].sum().sort_values(ascending=False)
            analysis += "📈 **Por Cohorte:**\n"
            for cohorte, valor in cohorte_analysis.items():
                porcentaje = (valor / total_value) * 100 if total_value > 0 else 0
                analysis += f"  - {cohorte}: ${valor:,} ({porcentaje:.1f}%)\n"
            analysis += "\n"
        
        # Análisis por clasificación
        if 'Clasificación' in df.columns and 'Valor' in df.columns:
            clasif_analysis = df.groupby('Clasificación')['Valor'].sum().sort_values(ascending=False)
            analysis += "🏷️ **Por Clasificación:**\n"
            for clasif, valor in clasif_analysis.items():
                porcentaje = (valor / total_value) * 100 if total_value > 0 else 0
                analysis += f"  - {clasif}: ${valor:,} ({porcentaje:.1f}%)\n"
            analysis += "\n"
        
        # Análisis por período si se solicita "últimos N períodos"
        if 'ultimos_periodos' in filters:
            if 'Periodo' in df.columns:
                periodo_analysis = df.groupby('Periodo')['Valor'].sum().sort_index(ascending=False)
                analysis += "📅 **Análisis por Período:**\n"
                for periodo, valor in periodo_analysis.items():
                    porcentaje = (valor / total_value * 100) if total_value > 0 else 0
                    analysis += f"  - {periodo}: ${valor:,} ({porcentaje:.1f}%)\n"
                analysis += "\n"
        
        # Análisis por escenario
        if 'Escenario' in df.columns and 'Valor' in df.columns:
            escenario_analysis = df.groupby('Escenario')['Valor'].sum().sort_values(ascending=False)
            analysis += "🎯 **Por Escenario:**\n"
            for escenario, valor in escenario_analysis.items():
                porcentaje = (valor / total_value) * 100 if total_value > 0 else 0
                analysis += f"  - {escenario}: ${valor:,} ({porcentaje:.1f}%)\n"
            analysis += "\n"
        
        # Análisis por período
        if 'Periodo' in df.columns and 'Valor' in df.columns:
            periodo_analysis = df.groupby('Periodo')['Valor'].sum().sort_values(ascending=False)
            analysis += "📅 **Por Período:**\n"
            for periodo, valor in periodo_analysis.items():
                porcentaje = (valor / total_value) * 100 if total_value > 0 else 0
                analysis += f"  - {periodo}: ${valor:,} ({porcentaje:.1f}%)\n"
            analysis += "\n"
        
        return analysis
    
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
                analysis += f"  📈 {cohorte}: ${valor:,} ({porcentaje:.1f}%)\n"
            analysis += "\n"
        
        return analysis
    
    def analyze_originacion(self) -> str:
        """Análisis específico para Originación"""
        if self.df is None:
            return "No hay datos disponibles."
        
        # Filtrar datos específicos para Originación
        filtro = (
            (self.df['Elaboracion'] == '08-01-2025') &
            (self.df['Periodo'] == '08-01-2025') &
            (self.df['Pais'] == 'CL') &
            (self.df['Escenario'] == 'Moderado')
        )
        
        datos = self.df[filtro]
        
        if len(datos) == 0:
            return "No se encontraron datos para los filtros especificados."
        
        # Análisis específico por Originación
        if 'Concepto' in datos.columns:
            originacion_data = datos[datos['Concepto'].str.contains('Originación', case=False, na=False)]
        else:
            originacion_data = datos
        
        if len(originacion_data) == 0:
            return "No se encontraron datos específicos de Originación para los filtros especificados."
        
        # Análisis por negocio y cohorte para Originación
        resultado = originacion_data.groupby(['Negocio', 'Cohort_Act'])['Valor'].sum().reset_index()
        total = originacion_data['Valor'].sum()
        
        analysis = f"📊 **Análisis de Originación 08-01-2025:**\n"
        analysis += f"💰 Valor total de Originación: ${total:,.2f}\n"
        analysis += f"📊 Registros de Originación: {len(originacion_data):,}\n\n"
        
        for negocio in resultado['Negocio'].unique():
            negocio_data = resultado[resultado['Negocio'] == negocio]
            total_negocio = negocio_data['Valor'].sum()
            analysis += f"🏢 **{negocio}:** ${total_negocio:,.2f}\n"
            
            for _, row in negocio_data.iterrows():
                cohorte = row['Cohort_Act'] if pd.notna(row['Cohort_Act']) else 'Sin cohorte'
                valor = row['Valor']
                porcentaje = (valor / total_negocio) * 100 if total_negocio > 0 else 0
                analysis += f"  📈 {cohorte}: ${valor:,} ({porcentaje:.1f}%)\n"
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
        # Detectar si es una consulta financiera
        is_financial = self.is_financial_query(user_message)
        
        # Si es financiera, intentar análisis especializados primero
        if is_financial:
            # Verificar si es una consulta de "últimos N meses" (PRIORIDAD ALTA)
            if ('ultimos' in user_message.lower() or 'ultimo' in user_message.lower()) and 'meses' in user_message.lower():
                months_analysis = self.analyze_last_months_performance(user_message)
                if months_analysis:
                    return months_analysis
            
            # Verificar si es una consulta de "como nos fue" (comparación) - PRIORIDAD BAJA
            if 'como nos fue' in user_message.lower() or 'como me fue' in user_message.lower():
                if 'elaboracion' in user_message.lower():
                    comparison_analysis = self.analyze_performance_comparison(user_message)
                    if comparison_analysis:
                        return comparison_analysis
            
            # Análisis de datos estándar
            data_analysis = self.analyze_data(user_message)
            if data_analysis and "No hay datos disponibles" not in data_analysis:
                return data_analysis
        
        # Para consultas generales o si no hay datos financieros, usar OpenAI
        if not hasattr(self, 'openai_available') or not self.openai_available:
            if is_financial:
                return "Solo análisis de datos disponible. Configura OpenAI API Key para consultas generales."
            else:
                return "Configura OpenAI API Key para consultas generales."
        
        try:
            # Usar el prompt apropiado según el tipo de consulta
            system_prompt = "Eres un asistente inteligente y versátil. Para preguntas financieras, análisis de datos y temas de negocio, eres un experto serio y profesional que proporciona información precisa y detallada. Para preguntas cotidianas, conversaciones casuales o temas generales, eres amigable, conversacional y como un buen amigo. Adapta tu tono según el contexto: serio para finanzas, casual y amigable para todo lo demás."
            
            # Usar la nueva API de OpenAI
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
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
