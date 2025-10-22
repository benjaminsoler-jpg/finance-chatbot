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
import numpy as np

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
    .business-title {
        font-size: 1.4em;
        font-weight: bold;
        margin: 15px 0 10px 0;
        color: #2E86AB;
    }
    .variable-title {
        font-size: 1.2em;
        font-weight: bold;
        margin: 5px 0;
        color: #E63946;
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
            
            # Convertir columna Valor a numérico, manejando comas, % y valores nulos
            self.df['Valor'] = self.df['Valor'].astype(str).str.replace(',', '')
            
            # Detectar si el valor ya está en formato porcentaje (contiene %)
            def convert_percentage(value_str):
                value_str = str(value_str).strip()
                
                # Manejar casos especiales
                if value_str in ['#DIV/0!', '#VALUE!', '#N/A', 'N/A', '', 'nan', 'NaN']:
                    return 0.0
                
                if '%' in value_str:
                    # Si tiene %, convertir de porcentaje a decimal
                    try:
                        return float(value_str.replace('%', '')) / 100
                    except ValueError:
                        return 0.0
                else:
                    # Si no tiene %, convertir directamente
                    try:
                        return float(value_str)
                    except ValueError:
                        return 0.0
            
            self.df['Valor'] = self.df['Valor'].apply(convert_percentage)
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
    
    def is_single_variable_query(self, query: str) -> bool:
        """Detectar si es una consulta específica de una sola variable"""
        import re
        
        single_variable_patterns = [
            r'dame\s+la\s+rate\s+all\s+in',
            r'dame\s+el\s+rate\s+all\s+in',
            r'muestra\s+la\s+rate\s+all\s+in',
            r'muestra\s+el\s+rate\s+all\s+in',
            r'cuanto\s+es\s+la\s+rate\s+all\s+in',
            r'cuanto\s+es\s+el\s+rate\s+all\s+in',
            r'valor\s+de\s+la\s+rate\s+all\s+in',
            r'valor\s+del\s+rate\s+all\s+in'
        ]
        
        query_lower = query.lower()
        return any(re.search(pattern, query_lower) for pattern in single_variable_patterns)
    
    def analyze_single_variable(self, query: str) -> str:
        """Análisis específico para una sola variable"""
        import re
        
        # Extraer filtros de la consulta
        elaboracion = None
        periodo = None
        negocio = None
        escenario = None
        concepto = None
        
        # Buscar elaboración
        elaboracion_match = re.search(r'elaboraci[oó]n\s+(\d{2})-01-2025', query.lower())
        if elaboracion_match:
            elaboracion = elaboracion_match.group(1) + '-01-2025'
        
        # Buscar período
        periodo_match = re.search(r'periodo\s+(\d{2})-01-2025', query.lower())
        if periodo_match:
            periodo = periodo_match.group(1) + '-01-2025'
        
        # Buscar negocio
        if 'pyme' in query.lower():
            negocio = 'PYME'
        elif 'corp' in query.lower():
            negocio = 'CORP'
        elif 'brokers' in query.lower():
            negocio = 'Brokers'
        elif 'wk' in query.lower():
            negocio = 'WK'
        
        # Buscar escenario
        if 'moderado' in query.lower():
            escenario = 'Moderado'
        elif 'ambicion' in query.lower():
            escenario = 'Ambicion'
        
        # Buscar concepto específico
        if 'rate all in' in query.lower():
            concepto = 'Rate All In'
        elif 'risk rate' in query.lower():
            concepto = 'Risk Rate'
        elif 'fund rate' in query.lower():
            concepto = 'Fund Rate'
        elif 'originacion' in query.lower():
            concepto = 'Originacion'
        elif 'new active' in query.lower():
            concepto = 'New Active'
        elif 'churn bruto' in query.lower():
            concepto = 'Churn Bruto'
        
        # Construir filtro
        filtro = self.df.copy()
        
        if elaboracion:
            filtro = filtro[filtro['Elaboracion'] == elaboracion]
        if periodo:
            filtro = filtro[filtro['Periodo'] == periodo]
        if negocio:
            filtro = filtro[filtro['Negocio'] == negocio]
        if escenario:
            filtro = filtro[filtro['Escenario'] == escenario]
        if concepto:
            filtro = filtro[filtro['Concepto'] == concepto]
        
        if len(filtro) == 0:
            return f"❌ No se encontraron datos para {concepto or 'la variable solicitada'} con los filtros especificados."
        
        # Generar respuesta específica
        analysis = f"📊 **Consulta Específica: {concepto or 'Variable'}**\n\n"
        
        # Mostrar filtros aplicados
        analysis += "🔍 **Filtros aplicados:**\n"
        if elaboracion:
            analysis += f"- Elaboración: {elaboracion}\n"
        if periodo:
            analysis += f"- Período: {periodo}\n"
        if negocio:
            analysis += f"- Negocio: {negocio}\n"
        if escenario:
            analysis += f"- Escenario: {escenario}\n"
        if concepto:
            analysis += f"- Concepto: {concepto}\n"
        
        analysis += f"\n📈 **Resultados:**\n"
        
        # Mostrar datos por cohort
        if concepto in ['Rate All In', 'Risk Rate', 'Fund Rate', 'Term']:
            # Para rates, mostrar por cohort
            cohort_data = filtro.groupby('Cohort_Act')['Valor'].first()
            for cohort, valor in cohort_data.items():
                if pd.isna(cohort):
                    cohort_name = "Sin Cohort"
                else:
                    cohort_name = str(cohort)
                
                if concepto == 'Term':
                    analysis += f"- {cohort_name}: {valor:.0f}\n"
                else:  # Rates
                    analysis += f"- {cohort_name}: {valor*100:.2f}%\n"
        else:
            # Para variables monetarias, mostrar suma total
            total = filtro['Valor'].sum()
            analysis += f"- Valor total: ${total:,.0f}\n"
            analysis += f"- Registros: {len(filtro)}\n"
        
        return analysis
    
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
    
    def analyze_rolling_comparison(self, query: str) -> str:
        """Análisis específico de Rolling Predictivo vs Realidad Histórica"""
        import re
        
        # Patrón 1: "comparame los periodos X elaboracion Y y el periodo X elaboracion Z"
        pattern1 = r'comparame\s+los\s+periodos?\s+(\d{2})-01-2025\s+elaboraci[oó]n\s+(\d{2})-01-2025\s+y\s+el\s+periodo\s+(\d{2})-01-2025\s+elaboraci[oó]n\s+(\d{2})-01-2025'
        match1 = re.search(pattern1, query.lower())
        
        # Patrón 2: "como me fue en la elaboracion X sobre el periodo Y, comparando con la predicha en la elaboracion Z en el periodo Y"
        pattern2 = r'como me fue en la elaboraci[oó]n\s+(\d{2})-01-2025\s+sobre el periodo\s+(\d{2})-01-2025.*?comparando con la predicha en la elaboraci[oó]n\s+(\d{2})-01-2025\s+en el periodo\s+(\d{2})-01-2025'
        match2 = re.search(pattern2, query.lower())
        
        if match1:
            # Patrón 1
            periodo1 = match1.group(1) + '-01-2025'
            elaboracion1 = match1.group(2) + '-01-2025'
            periodo2 = match1.group(3) + '-01-2025'
            elaboracion2 = match1.group(4) + '-01-2025'
            
            # Verificar que ambos períodos sean iguales
            if periodo1 != periodo2:
                return None
            
            periodo = periodo1
            
            # Determinar cuál es predicción y cuál es realidad
            mes_elaboracion1 = int(elaboracion1.split('-')[0])
            mes_elaboracion2 = int(elaboracion2.split('-')[0])
            mes_periodo = int(periodo.split('-')[0])
            
            # Si elaboración = período, es predicción (rolling predictivo)
            # Si elaboración > período, es realidad (datos históricos)
            if mes_elaboracion1 == mes_periodo:
                elaboracion_prediccion = elaboracion1
                elaboracion_realidad = elaboracion2
            elif mes_elaboracion2 == mes_periodo:
                elaboracion_prediccion = elaboracion2
                elaboracion_realidad = elaboracion1
            else:
                # Si ninguna coincide exactamente, usar la más cercana
                if abs(mes_elaboracion1 - mes_periodo) < abs(mes_elaboracion2 - mes_periodo):
                    elaboracion_prediccion = elaboracion1
                    elaboracion_realidad = elaboracion2
                else:
                    elaboracion_prediccion = elaboracion2
                    elaboracion_realidad = elaboracion1
            
        elif match2:
            # Patrón 2
            elaboracion_realidad = match2.group(1) + '-01-2025'
            periodo = match2.group(2) + '-01-2025'
            elaboracion_prediccion = match2.group(3) + '-01-2025'
            periodo_verificacion = match2.group(4) + '-01-2025'
            
            # Verificar que ambos períodos sean iguales
            if periodo != periodo_verificacion:
                return None
            
            # Verificar que la lógica sea correcta:
            # elaboracion_realidad > periodo (datos históricos)
            # elaboracion_prediccion <= periodo (predicción)
            mes_elaboracion_realidad = int(elaboracion_realidad.split('-')[0])
            mes_elaboracion_prediccion = int(elaboracion_prediccion.split('-')[0])
            mes_periodo = int(periodo.split('-')[0])
            
            if mes_elaboracion_realidad <= mes_periodo or mes_elaboracion_prediccion > mes_periodo:
                # Intercambiar si la lógica está invertida
                elaboracion_realidad, elaboracion_prediccion = elaboracion_prediccion, elaboracion_realidad
                
        else:
            return None
        
        # Determinar si separar por negocio
        separar_por_negocio = 'separalo por negocio' in query.lower() or 'separar por negocio' in query.lower()
        
        # Obtener negocios a analizar
        if separar_por_negocio:
            negocios = ['PYME', 'CORP', 'Brokers', 'WK']
        else:
            negocios = ['TODOS']  # Análisis consolidado
        
        analysis = f"📊 **Análisis Rolling: Predicción vs Realidad**\n"
        analysis += f"🎯 **Período analizado:** {periodo}\n"
        analysis += f"📈 **Rolling Predictivo:** {elaboracion_prediccion} (Elaboración = Período)\n"
        analysis += f"📉 **Datos Históricos:** {elaboracion_realidad} (Elaboración > Período)\n"
        if separar_por_negocio:
            analysis += f"🏢 **Análisis separado por Negocio**\n"
        analysis += "\n"
        
        # Variables específicas para comparar
        variables_comparacion = {
            'concepto': ['Rate All In', 'Originacion Prom', 'Term', 'Risk Rate', 'Fund Rate'],
            'clasificacion': ['New Active', 'Churn Bruto', 'Resucitados']
        }
        
        # Iterar por cada negocio
        for negocio in negocios:
            if separar_por_negocio:
                analysis += f"<div class='business-title'>🏢 {negocio}</div>\n\n"
            
            # Comparar por Concepto
            analysis += "📋 **Comparación por Concepto:**\n"
            for concepto in variables_comparacion['concepto']:
                if concepto in ['Rate All In', 'Risk Rate', 'Fund Rate', 'Term']:
                    # Para rates y term: comparar por cohorts
                    analysis += f"📈 **{concepto}:**\n"
                    
                    # Obtener datos de predicción por cohort
                    pred_data = self.df[
                        (self.df['Elaboracion'] == elaboracion_prediccion) & 
                        (self.df['Periodo'] == periodo) & 
                        (self.df['Concepto'] == concepto)
                    ]
                    
                    # Obtener datos de realidad por cohort
                    real_data = self.df[
                        (self.df['Elaboracion'] == elaboracion_realidad) & 
                        (self.df['Periodo'] == periodo) & 
                        (self.df['Concepto'] == concepto)
                    ]
                    
                    # Aplicar filtro de negocio si es necesario
                    if separar_por_negocio:
                        pred_data = pred_data[pred_data['Negocio'] == negocio]
                        real_data = real_data[real_data['Negocio'] == negocio]
                    
                    if len(pred_data) > 0 and len(real_data) > 0:
                        # Agrupar por cohort y tomar el primer valor único
                        pred_grouped = pred_data.groupby('Cohort_Act')['Valor'].first()
                        real_grouped = real_data.groupby('Cohort_Act')['Valor'].first()
                        
                        # Obtener cohorts comunes
                        cohorts_comunes = set(pred_grouped.index) & set(real_grouped.index)
                        
                        if cohorts_comunes:
                            for cohort in sorted(cohorts_comunes):
                                pred_valor = pred_grouped[cohort]
                                real_valor = real_grouped[cohort]
                                
                                diferencia = real_valor - pred_valor
                                
                                if diferencia > 0:
                                    tendencia = "mejor"
                                    emoji = "📈"
                                elif diferencia < 0:
                                    tendencia = "peor"
                                    emoji = "📉"
                                else:
                                    tendencia = "igual"
                                    emoji = "➡️"
                                
                                if concepto == 'Term':
                                    analysis += f"    {emoji} **{cohort}:**\n"
                                    analysis += f"      - Rolling Predictivo: {pred_valor:.0f}\n"
                                    analysis += f"      - Datos Históricos: {real_valor:.0f}\n"
                                    analysis += f"      - Diferencia: {diferencia:+.0f} - {tendencia}\n"
                                else:  # Rates
                                    analysis += f"    {emoji} **{cohort}:**\n"
                                    analysis += f"      - Rolling Predictivo: {pred_valor*100:.2f}%\n"
                                    analysis += f"      - Datos Históricos: {real_valor*100:.2f}%\n"
                                    analysis += f"      - Diferencia: {diferencia*100:+.2f}pp - {tendencia}\n"
                            analysis += "\n"
                        else:
                            analysis += f"    - No hay cohorts comunes para comparar\n\n"
                    else:
                        analysis += f"    - No hay datos disponibles para comparar\n\n"
                else:
                    # Para variables monetarias: sumar y comparar
                    pred_data = self.df[
                        (self.df['Elaboracion'] == elaboracion_prediccion) & 
                        (self.df['Periodo'] == periodo) & 
                        (self.df['Concepto'] == concepto)
                    ]
                    
                    real_data = self.df[
                        (self.df['Elaboracion'] == elaboracion_realidad) & 
                        (self.df['Periodo'] == periodo) & 
                        (self.df['Concepto'] == concepto)
                    ]
                    
                    # Aplicar filtro de negocio si es necesario
                    if separar_por_negocio:
                        pred_data = pred_data[pred_data['Negocio'] == negocio]
                        real_data = real_data[real_data['Negocio'] == negocio]
                    
                    if len(pred_data) > 0 and len(real_data) > 0:
                        pred_valor = pred_data['Valor'].sum()
                        real_valor = real_data['Valor'].sum()
                        
                        diferencia = real_valor - pred_valor
                        porcentaje = (diferencia / pred_valor * 100) if pred_valor != 0 else 0
                        
                        if diferencia > 0:
                            tendencia = "mejor"
                            emoji = "📈"
                        elif diferencia < 0:
                            tendencia = "peor"
                            emoji = "📉"
                        else:
                            tendencia = "igual"
                            emoji = "➡️"
                        
                        analysis += f"  {emoji} **{concepto}:**\n"
                        analysis += f"    - Rolling Predictivo: ${pred_valor:,.0f}\n"
                        analysis += f"    - Datos Históricos: ${real_valor:,.0f}\n"
                        analysis += f"    - Diferencia: ${diferencia:+,.0f} ({porcentaje:+.1f}%) - {tendencia}\n\n"
            
            # Comparar por Clasificación (variables numéricas - se suman)
            analysis += "🏷️ **Comparación por Clasificación:**\n"
            for clasificacion in variables_comparacion['clasificacion']:
                # Datos de predicción (rolling predictivo)
                pred_data = self.df[
                    (self.df['Elaboracion'] == elaboracion_prediccion) & 
                    (self.df['Periodo'] == periodo) & 
                    (self.df['Clasificación'] == clasificacion)
                ]
                
                # Datos de realidad (históricos)
                real_data = self.df[
                    (self.df['Elaboracion'] == elaboracion_realidad) & 
                    (self.df['Periodo'] == periodo) & 
                    (self.df['Clasificación'] == clasificacion)
                ]
                
                # Aplicar filtro de negocio si es necesario
                if separar_por_negocio:
                    pred_data = pred_data[pred_data['Negocio'] == negocio]
                    real_data = real_data[real_data['Negocio'] == negocio]
                
                if len(pred_data) > 0 and len(real_data) > 0:
                    pred_valor = pred_data['Valor'].sum()
                    real_valor = real_data['Valor'].sum()
                    
                    diferencia = real_valor - pred_valor
                    porcentaje = (diferencia / pred_valor * 100) if pred_valor != 0 else 0
                    
                    if diferencia > 0:
                        tendencia = "mejor"
                        emoji = "📈"
                    elif diferencia < 0:
                        tendencia = "peor"
                        emoji = "📉"
                    else:
                        tendencia = "igual"
                        emoji = "➡️"
                    
                    analysis += f"  {emoji} **{clasificacion}:**\n"
                    analysis += f"    - Rolling Predictivo: {pred_valor:,.0f}\n"
                    analysis += f"    - Datos Históricos: {real_valor:,.0f}\n"
                    analysis += f"    - Diferencia: {diferencia:+,.0f} ({porcentaje:+.1f}%) - {tendencia}\n\n"
            
            if separar_por_negocio:
                analysis += "---\n\n"
        
        # Agregar storytelling ejecutivo
        analysis += self._generate_rolling_storytelling(elaboracion_prediccion, elaboracion_realidad, periodo, separar_por_negocio, negocios)
        
        # Marcar que se deben generar gráficos
        analysis += "---\n\n"
        analysis += "## 📊 **VISUALIZACIONES INTERACTIVAS**\n\n"
        analysis += "**GENERATE_ROLLING_CHARTS:**\n"
        analysis += f"elaboracion_prediccion={elaboracion_prediccion}\n"
        analysis += f"elaboracion_realidad={elaboracion_realidad}\n"
        analysis += f"periodo={periodo}\n"
        analysis += f"separar_por_negocio={separar_por_negocio}\n"
        analysis += f"negocios={negocios}\n"
        
        return analysis
    
    def _generate_rolling_storytelling(self, elaboracion_prediccion, elaboracion_realidad, periodo, separar_por_negocio, negocios):
        """Generar storytelling ejecutivo para comparación rolling"""
        analysis = ""
        
        # Obtener datos para análisis
        variables_clave = ['Rate All In', 'Originacion Prom', 'Term', 'Risk Rate', 'Fund Rate']
        clasificaciones_clave = ['New Active', 'Churn Bruto', 'Resucitados']
        
        analysis += "---\n\n"
        analysis += "## 📖 **ANÁLISIS EJECUTIVO ROLLING**\n\n"
        
        # Análisis general
        analysis += "### 🎯 **RESUMEN EJECUTIVO**\n\n"
        analysis += f"El análisis de **rolling predictivo** vs **realidad histórica** para el período **{periodo}** revela insights críticos sobre la **precisión de nuestros modelos predictivos** y las **dinámicas del mercado**. "
        analysis += f"La comparación entre la **elaboración {elaboracion_prediccion}** (predicción) y la **elaboración {elaboracion_realidad}** (realidad) proporciona una **evaluación objetiva** de nuestro desempeño en la **planificación financiera**.\n\n"
        
        if separar_por_negocio:
            analysis += "### 🏢 **ANÁLISIS POR SEGMENTO DE NEGOCIO**\n\n"
            
            for negocio in negocios:
                # Obtener datos específicos del negocio
                negocio_data = self._get_rolling_negocio_summary(elaboracion_prediccion, elaboracion_realidad, periodo, negocio, variables_clave, clasificaciones_clave)
                
                if negocio_data:
                    analysis += f"#### **{negocio}**\n\n"
                    analysis += f"{negocio_data['story']}\n\n"
        else:
            # Análisis consolidado
            consolidated_data = self._get_rolling_consolidated_summary(elaboracion_prediccion, elaboracion_realidad, periodo, variables_clave, clasificaciones_clave)
            if consolidated_data:
                analysis += f"### 📊 **ANÁLISIS CONSOLIDADO**\n\n"
                analysis += f"{consolidated_data['story']}\n\n"
        
        # Recomendaciones estratégicas
        analysis += "### 💡 **RECOMENDACIONES ESTRATÉGICAS**\n\n"
        analysis += "Basado en este análisis de **rolling predictivo**, se recomienda:\n\n"
        analysis += "• **Revisar modelos predictivos** en variables con desviaciones significativas (>5%)\n"
        analysis += "• **Ajustar estrategias de pricing** según la precisión de Rate All In por cohort\n"
        analysis += "• **Optimizar gestión de riesgo** basada en la precisión de Risk Rate\n"
        analysis += "• **Mejorar proyecciones de originación** para mayor precisión en planificación\n"
        analysis += "• **Implementar monitoreo continuo** de la precisión predictiva por segmento\n\n"
        
        return analysis
    
    def _get_rolling_negocio_summary(self, elaboracion_prediccion, elaboracion_realidad, periodo, negocio, variables_clave, clasificaciones_clave):
        """Obtener resumen específico por negocio para storytelling"""
        try:
            # Obtener datos de predicción y realidad
            pred_data = self.df[
                (self.df['Elaboracion'] == elaboracion_prediccion) & 
                (self.df['Periodo'] == periodo) & 
                (self.df['Negocio'] == negocio)
            ]
            
            real_data = self.df[
                (self.df['Elaboracion'] == elaboracion_realidad) & 
                (self.df['Periodo'] == periodo) & 
                (self.df['Negocio'] == negocio)
            ]
            
            if len(pred_data) == 0 or len(real_data) == 0:
                return None
            
            # Analizar variables clave
            insights = []
            
            # Rate All In por cohort
            rate_all_in_pred = pred_data[pred_data['Concepto'] == 'Rate All In'].groupby('Cohort_Act')['Valor'].first()
            rate_all_in_real = real_data[real_data['Concepto'] == 'Rate All In'].groupby('Cohort_Act')['Valor'].first()
            
            if len(rate_all_in_pred) > 0 and len(rate_all_in_real) > 0:
                cohorts_comunes = set(rate_all_in_pred.index) & set(rate_all_in_real.index)
                if cohorts_comunes:
                    mejoras = 0
                    deterioros = 0
                    for cohort in cohorts_comunes:
                        diff = (rate_all_in_real[cohort] - rate_all_in_pred[cohort]) * 100
                        if diff > 0.05:  # >0.05pp mejora
                            mejoras += 1
                        elif diff < -0.05:  # <-0.05pp deterioro
                            deterioros += 1
                    
                    if mejoras > deterioros:
                        insights.append(f"**Rate All In** muestra **mejoras** en la mayoría de cohorts, indicando **precisión predictiva** en pricing")
                    elif deterioros > mejoras:
                        insights.append(f"**Rate All In** presenta **desviaciones negativas** en múltiples cohorts, sugiriendo **revisión del modelo de pricing**")
                    else:
                        insights.append(f"**Rate All In** mantiene **estabilidad** entre predicción y realidad")
            
            # Originacion Prom
            originacion_pred = pred_data[pred_data['Concepto'] == 'Originacion Prom']['Valor'].sum()
            originacion_real = real_data[real_data['Concepto'] == 'Originacion Prom']['Valor'].sum()
            
            if originacion_pred > 0 and originacion_real > 0:
                diff_pct = ((originacion_real - originacion_pred) / originacion_pred) * 100
                if abs(diff_pct) > 5:
                    if diff_pct > 0:
                        insights.append(f"**Originación** superó las expectativas en **{abs(diff_pct):.1f}%**, demostrando **fortaleza del mercado**")
                    else:
                        insights.append(f"**Originación** estuvo **{abs(diff_pct):.1f}%** por debajo de la predicción, indicando **desafíos de mercado**")
                else:
                    insights.append(f"**Originación** se alineó estrechamente con las predicciones, mostrando **precisión del modelo**")
            
            # New Active
            new_active_pred = pred_data[pred_data['Clasificación'] == 'New Active']['Valor'].sum()
            new_active_real = real_data[real_data['Clasificación'] == 'New Active']['Valor'].sum()
            
            if new_active_pred > 0 and new_active_real > 0:
                diff_pct = ((new_active_real - new_active_pred) / new_active_pred) * 100
                if abs(diff_pct) > 10:
                    if diff_pct > 0:
                        insights.append(f"**Adquisición de clientes** superó las proyecciones en **{abs(diff_pct):.1f}%**, reflejando **efectividad de estrategias de marketing**")
                    else:
                        insights.append(f"**Adquisición de clientes** estuvo **{abs(diff_pct):.1f}%** por debajo de las proyecciones, requiriendo **ajuste en estrategias de adquisición**")
            
            # Generar story
            if insights:
                story = f"El segmento **{negocio}** presenta un **comportamiento mixto** en la comparación rolling. "
                story += " ".join(insights) + ". "
                
                # Conclusión específica
                if len(insights) >= 3:
                    story += f"En general, **{negocio}** muestra **variabilidad** en la precisión predictiva, sugiriendo la necesidad de **modelos más granulares** para este segmento."
                else:
                    story += f"El segmento **{negocio}** mantiene **consistencia** en la mayoría de indicadores, validando las **estrategias actuales**."
                
                return {'story': story}
            
            return None
            
        except Exception as e:
            return None
    
    def _get_rolling_consolidated_summary(self, elaboracion_prediccion, elaboracion_realidad, periodo, variables_clave, clasificaciones_clave):
        """Obtener resumen consolidado para storytelling"""
        try:
            # Obtener datos consolidados
            pred_data = self.df[
                (self.df['Elaboracion'] == elaboracion_prediccion) & 
                (self.df['Periodo'] == periodo)
            ]
            
            real_data = self.df[
                (self.df['Elaboracion'] == elaboracion_realidad) & 
                (self.df['Periodo'] == periodo)
            ]
            
            if len(pred_data) == 0 or len(real_data) == 0:
                return None
            
            # Análisis consolidado
            insights = []
            
            # Rate All In consolidado
            rate_all_in_pred = pred_data[pred_data['Concepto'] == 'Rate All In']['Valor'].mean()
            rate_all_in_real = real_data[real_data['Concepto'] == 'Rate All In']['Valor'].mean()
            
            if rate_all_in_pred > 0 and rate_all_in_real > 0:
                diff_pp = (rate_all_in_real - rate_all_in_pred) * 100
                if abs(diff_pp) > 0.1:
                    if diff_pp > 0:
                        insights.append(f"**Rate All In** promedio superó las predicciones en **{diff_pp:.2f}pp**, indicando **mejor performance de pricing**")
                    else:
                        insights.append(f"**Rate All In** promedio estuvo **{abs(diff_pp):.2f}pp** por debajo de las predicciones, sugiriendo **presión competitiva**")
                else:
                    insights.append(f"**Rate All In** promedio se mantuvo **estable** respecto a las predicciones")
            
            # Originacion Prom consolidado
            originacion_pred = pred_data[pred_data['Concepto'] == 'Originacion Prom']['Valor'].sum()
            originacion_real = real_data[real_data['Concepto'] == 'Originacion Prom']['Valor'].sum()
            
            if originacion_pred > 0 and originacion_real > 0:
                diff_pct = ((originacion_real - originacion_pred) / originacion_pred) * 100
                if abs(diff_pct) > 3:
                    if diff_pct > 0:
                        insights.append(f"**Originación total** superó las proyecciones en **{diff_pct:.1f}%**, demostrando **fortaleza del mercado**")
                    else:
                        insights.append(f"**Originación total** estuvo **{abs(diff_pct):.1f}%** por debajo de las proyecciones, indicando **desafíos de mercado**")
                else:
                    insights.append(f"**Originación total** se alineó **precisamente** con las proyecciones")
            
            # New Active consolidado
            new_active_pred = pred_data[pred_data['Clasificación'] == 'New Active']['Valor'].sum()
            new_active_real = real_data[real_data['Clasificación'] == 'New Active']['Valor'].sum()
            
            if new_active_pred > 0 and new_active_real > 0:
                diff_pct = ((new_active_real - new_active_pred) / new_active_pred) * 100
                if abs(diff_pct) > 5:
                    if diff_pct > 0:
                        insights.append(f"**Adquisición de clientes** superó las proyecciones en **{diff_pct:.1f}%**, validando **estrategias de crecimiento**")
                    else:
                        insights.append(f"**Adquisición de clientes** estuvo **{abs(diff_pct):.1f}%** por debajo de las proyecciones, requiriendo **ajuste estratégico**")
            
            # Generar story consolidado
            if insights:
                story = f"El análisis **consolidado** del rolling predictivo revela un **panorama diverso** en la precisión de nuestros modelos. "
                story += " ".join(insights) + ". "
                story += "Esta **variabilidad** en la precisión predictiva subraya la importancia de **modelos adaptativos** y **monitoreo continuo** para optimizar la **planificación financiera**."
                
                return {'story': story}
            
            return None
            
        except Exception as e:
            return None
    
    def _generate_rolling_visualizations(self, elaboracion_prediccion, elaboracion_realidad, periodo, separar_por_negocio, negocios):
        """Generar visualizaciones interactivas para comparación rolling"""
        try:
            import plotly.express as px
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            import pandas as pd
            
            analysis = ""
            analysis += "---\n\n"
            analysis += "## 📊 **VISUALIZACIONES INTERACTIVAS**\n\n"
            
            # 1. Gráfico de barras - Comparación por Variable
            analysis += "### 📈 **Gráfico 1: Comparación Predicción vs Realidad por Variable**\n"
            self._create_rolling_comparison_chart(elaboracion_prediccion, elaboracion_realidad, periodo, separar_por_negocio, negocios)
            
            # 2. Gráfico de dispersión - Precisión Predictiva
            analysis += "### 🎯 **Gráfico 2: Precisión Predictiva por Segmento**\n"
            self._create_rolling_accuracy_chart(elaboracion_prediccion, elaboracion_realidad, periodo, separar_por_negocio, negocios)
            
            # 3. Heatmap - Desviaciones por Cohort
            analysis += "### 🔥 **Gráfico 3: Heatmap de Desviaciones por Cohort**\n"
            self._create_rolling_heatmap_chart(elaboracion_prediccion, elaboracion_realidad, periodo, separar_por_negocio, negocios)
            
            # 4. Gráfico de líneas - Tendencias por Negocio
            if separar_por_negocio:
                analysis += "### 📊 **Gráfico 4: Tendencias por Segmento de Negocio**\n"
                self._create_rolling_trends_chart(elaboracion_prediccion, elaboracion_realidad, periodo, negocios)
            
            return analysis
            
        except Exception as e:
            return ""
    
    def _create_rolling_comparison_chart(self, elaboracion_prediccion, elaboracion_realidad, periodo, separar_por_negocio, negocios):
        """Crear gráfico de comparación predicción vs realidad"""
        try:
            import plotly.express as px
            import pandas as pd
            
            # Obtener datos
            variables = ['Rate All In', 'Originacion Prom', 'Term', 'Risk Rate', 'Fund Rate']
            data = []
            
            for variable in variables:
                if variable in ['Rate All In', 'Risk Rate', 'Fund Rate', 'Term']:
                    # Para rates y term: promedio por cohort
                    pred_data = self.df[
                        (self.df['Elaboracion'] == elaboracion_prediccion) & 
                        (self.df['Periodo'] == periodo) & 
                        (self.df['Concepto'] == variable)
                    ]
                    real_data = self.df[
                        (self.df['Elaboracion'] == elaboracion_realidad) & 
                        (self.df['Periodo'] == periodo) & 
                        (self.df['Concepto'] == variable)
                    ]
                    
                    if separar_por_negocio:
                        for negocio in negocios:
                            pred_negocio = pred_data[pred_data['Negocio'] == negocio]
                            real_negocio = real_data[real_data['Negocio'] == negocio]
                            
                            if len(pred_negocio) > 0 and len(real_negocio) > 0:
                                pred_valor = pred_negocio.groupby('Cohort_Act')['Valor'].first().mean()
                                real_valor = real_negocio.groupby('Cohort_Act')['Valor'].first().mean()
                                
                                if variable == 'Term':
                                    data.append({
                                        'Variable': f"{variable} - {negocio}",
                                        'Predicción': pred_valor,
                                        'Realidad': real_valor,
                                        'Tipo': 'Term'
                                    })
                                else:
                                    data.append({
                                        'Variable': f"{variable} - {negocio}",
                                        'Predicción': pred_valor * 100,
                                        'Realidad': real_valor * 100,
                                        'Tipo': 'Rate (%)'
                                    })
                    else:
                        if len(pred_data) > 0 and len(real_data) > 0:
                            pred_valor = pred_data.groupby('Cohort_Act')['Valor'].first().mean()
                            real_valor = real_data.groupby('Cohort_Act')['Valor'].first().mean()
                            
                            if variable == 'Term':
                                data.append({
                                    'Variable': variable,
                                    'Predicción': pred_valor,
                                    'Realidad': real_valor,
                                    'Tipo': 'Term'
                                })
                            else:
                                data.append({
                                    'Variable': variable,
                                    'Predicción': pred_valor * 100,
                                    'Realidad': real_valor * 100,
                                    'Tipo': 'Rate (%)'
                                })
                else:
                    # Para variables monetarias: suma total
                    pred_data = self.df[
                        (self.df['Elaboracion'] == elaboracion_prediccion) & 
                        (self.df['Periodo'] == periodo) & 
                        (self.df['Concepto'] == variable)
                    ]
                    real_data = self.df[
                        (self.df['Elaboracion'] == elaboracion_realidad) & 
                        (self.df['Periodo'] == periodo) & 
                        (self.df['Concepto'] == variable)
                    ]
                    
                    if separar_por_negocio:
                        for negocio in negocios:
                            pred_negocio = pred_data[pred_data['Negocio'] == negocio]
                            real_negocio = real_data[real_data['Negocio'] == negocio]
                            
                            if len(pred_negocio) > 0 and len(real_negocio) > 0:
                                pred_valor = pred_negocio['Valor'].sum() / 1_000_000  # En millones
                                real_valor = real_negocio['Valor'].sum() / 1_000_000
                                
                                data.append({
                                    'Variable': f"{variable} - {negocio}",
                                    'Predicción': pred_valor,
                                    'Realidad': real_valor,
                                    'Tipo': 'Monetario (M$)'
                                })
                    else:
                        if len(pred_data) > 0 and len(real_data) > 0:
                            pred_valor = pred_data['Valor'].sum() / 1_000_000
                            real_valor = real_data['Valor'].sum() / 1_000_000
                            
                            data.append({
                                'Variable': variable,
                                'Predicción': pred_valor,
                                'Realidad': real_valor,
                                'Tipo': 'Monetario (M$)'
                            })
            
            if data:
                df = pd.DataFrame(data)
                
                # Crear gráfico de barras agrupadas
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    name='Predicción',
                    x=df['Variable'],
                    y=df['Predicción'],
                    marker_color='#3498db',
                    text=df['Predicción'].round(2),
                    textposition='auto'
                ))
                
                fig.add_trace(go.Bar(
                    name='Realidad',
                    x=df['Variable'],
                    y=df['Realidad'],
                    marker_color='#e74c3c',
                    text=df['Realidad'].round(2),
                    textposition='auto'
                ))
                
                fig.update_layout(
                    title="Comparación Rolling: Predicción vs Realidad",
                    xaxis_title="Variables",
                    yaxis_title="Valores",
                    barmode='group',
                    height=500,
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.info("No se pudieron generar los datos para el gráfico de comparación.")
    
    def _create_rolling_accuracy_chart(self, elaboracion_prediccion, elaboracion_realidad, periodo, separar_por_negocio, negocios):
        """Crear gráfico de precisión predictiva"""
        try:
            import plotly.express as px
            import pandas as pd
            
            data = []
            
            if separar_por_negocio:
                for negocio in negocios:
                    # Obtener datos del negocio
                    pred_data = self.df[
                        (self.df['Elaboracion'] == elaboracion_prediccion) & 
                        (self.df['Periodo'] == periodo) & 
                        (self.df['Negocio'] == negocio)
                    ]
                    real_data = self.df[
                        (self.df['Elaboracion'] == elaboracion_realidad) & 
                        (self.df['Periodo'] == periodo) & 
                        (self.df['Negocio'] == negocio)
                    ]
                    
                    if len(pred_data) > 0 and len(real_data) > 0:
                        # Calcular precisión para Rate All In
                        rate_pred = pred_data[pred_data['Concepto'] == 'Rate All In'].groupby('Cohort_Act')['Valor'].first().mean()
                        rate_real = real_data[real_data['Concepto'] == 'Rate All In'].groupby('Cohort_Act')['Valor'].first().mean()
                        
                        if rate_pred > 0 and rate_real > 0:
                            accuracy = 100 - abs((rate_real - rate_pred) / rate_pred * 100)
                            data.append({
                                'Negocio': negocio,
                                'Precisión (%)': accuracy,
                                'Variable': 'Rate All In'
                            })
                        
                        # Calcular precisión para Originacion Prom
                        orig_pred = pred_data[pred_data['Concepto'] == 'Originacion Prom']['Valor'].sum()
                        orig_real = real_data[real_data['Concepto'] == 'Originacion Prom']['Valor'].sum()
                        
                        if orig_pred > 0 and orig_real > 0:
                            accuracy = 100 - abs((orig_real - orig_pred) / orig_pred * 100)
                            data.append({
                                'Negocio': negocio,
                                'Precisión (%)': accuracy,
                                'Variable': 'Originacion Prom'
                            })
            else:
                # Análisis consolidado
                pred_data = self.df[
                    (self.df['Elaboracion'] == elaboracion_prediccion) & 
                    (self.df['Periodo'] == periodo)
                ]
                real_data = self.df[
                    (self.df['Elaboracion'] == elaboracion_realidad) & 
                    (self.df['Periodo'] == periodo)
                ]
                
                if len(pred_data) > 0 and len(real_data) > 0:
                    # Rate All In consolidado
                    rate_pred = pred_data[pred_data['Concepto'] == 'Rate All In']['Valor'].mean()
                    rate_real = real_data[real_data['Concepto'] == 'Rate All In']['Valor'].mean()
                    
                    if rate_pred > 0 and rate_real > 0:
                        accuracy = 100 - abs((rate_real - rate_pred) / rate_pred * 100)
                        data.append({
                            'Negocio': 'Consolidado',
                            'Precisión (%)': accuracy,
                            'Variable': 'Rate All In'
                        })
                    
                    # Originacion Prom consolidado
                    orig_pred = pred_data[pred_data['Concepto'] == 'Originacion Prom']['Valor'].sum()
                    orig_real = real_data[real_data['Concepto'] == 'Originacion Prom']['Valor'].sum()
                    
                    if orig_pred > 0 and orig_real > 0:
                        accuracy = 100 - abs((orig_real - orig_pred) / orig_pred * 100)
                        data.append({
                            'Negocio': 'Consolidado',
                            'Precisión (%)': accuracy,
                            'Variable': 'Originacion Prom'
                        })
            
            if data:
                df = pd.DataFrame(data)
                
                fig = px.scatter(
                    df, 
                    x='Negocio', 
                    y='Precisión (%)', 
                    color='Variable',
                    size='Precisión (%)',
                    title="Precisión Predictiva por Segmento",
                    labels={'Precisión (%)': 'Precisión (%)', 'Negocio': 'Segmento'}
                )
                
                fig.update_layout(
                    height=400,
                    showlegend=True
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.info("No se pudieron generar los datos para el gráfico de precisión.")
    
    def _create_rolling_heatmap_chart(self, elaboracion_prediccion, elaboracion_realidad, periodo, separar_por_negocio, negocios):
        """Crear heatmap de desviaciones por cohort"""
        try:
            import plotly.express as px
            import pandas as pd
            import numpy as np
            
            # Obtener datos de Rate All In por cohort
            pred_data = self.df[
                (self.df['Elaboracion'] == elaboracion_prediccion) & 
                (self.df['Periodo'] == periodo) & 
                (self.df['Concepto'] == 'Rate All In')
            ]
            real_data = self.df[
                (self.df['Elaboracion'] == elaboracion_realidad) & 
                (self.df['Periodo'] == periodo) & 
                (self.df['Concepto'] == 'Rate All In')
            ]
            
            if len(pred_data) > 0 and len(real_data) > 0:
                # Crear matriz de desviaciones
                cohorts = sorted(set(pred_data['Cohort_Act'].unique()) | set(real_data['Cohort_Act'].unique()))
                
                if separar_por_negocio:
                    negocio_list = negocios
                else:
                    negocio_list = ['Consolidado']
                
                heatmap_data = []
                
                for negocio in negocio_list:
                    for cohort in cohorts:
                        if separar_por_negocio:
                            pred_cohort = pred_data[
                                (pred_data['Negocio'] == negocio) & 
                                (pred_data['Cohort_Act'] == cohort)
                            ]['Valor'].first()
                            real_cohort = real_data[
                                (real_data['Negocio'] == negocio) & 
                                (real_data['Cohort_Act'] == cohort)
                            ]['Valor'].first()
                        else:
                            pred_cohort = pred_data[pred_data['Cohort_Act'] == cohort]['Valor'].first()
                            real_cohort = real_data[real_data['Cohort_Act'] == cohort]['Valor'].first()
                        
                        if not pd.isna(pred_cohort) and not pd.isna(real_cohort) and pred_cohort > 0:
                            deviation = (real_cohort - pred_cohort) * 100  # En pp
                            heatmap_data.append({
                                'Negocio': negocio,
                                'Cohort': str(cohort),
                                'Desviación (pp)': deviation
                            })
                
                if heatmap_data:
                    df = pd.DataFrame(heatmap_data)
                    
                    # Crear pivot table
                    pivot_df = df.pivot(index='Negocio', columns='Cohort', values='Desviación (pp)')
                    
                    fig = px.imshow(
                        pivot_df.values,
                        x=pivot_df.columns,
                        y=pivot_df.index,
                        color_continuous_scale='RdBu',
                        title="Heatmap de Desviaciones Rate All In (pp)",
                        labels=dict(x="Cohort", y="Negocio", color="Desviación (pp)")
                    )
                    
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.info("No se pudieron generar los datos para el heatmap.")
    
    def _create_rolling_trends_chart(self, elaboracion_prediccion, elaboracion_realidad, periodo, negocios):
        """Crear gráfico de tendencias por negocio"""
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            import pandas as pd
            
            # Crear subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Rate All In por Negocio', 'Originacion Prom por Negocio', 
                              'Risk Rate por Negocio', 'Fund Rate por Negocio'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            variables = [
                ('Rate All In', 1, 1),
                ('Originacion Prom', 1, 2),
                ('Risk Rate', 2, 1),
                ('Fund Rate', 2, 2)
            ]
            
            for variable, row, col in variables:
                pred_values = []
                real_values = []
                negocio_names = []
                
                for negocio in negocios:
                    if variable in ['Rate All In', 'Risk Rate', 'Fund Rate']:
                        pred_data = self.df[
                            (self.df['Elaboracion'] == elaboracion_prediccion) & 
                            (self.df['Periodo'] == periodo) & 
                            (self.df['Concepto'] == variable) &
                            (self.df['Negocio'] == negocio)
                        ].groupby('Cohort_Act')['Valor'].first().mean()
                        
                        real_data = self.df[
                            (self.df['Elaboracion'] == elaboracion_realidad) & 
                            (self.df['Periodo'] == periodo) & 
                            (self.df['Concepto'] == variable) &
                            (self.df['Negocio'] == negocio)
                        ].groupby('Cohort_Act')['Valor'].first().mean()
                        
                        if not pd.isna(pred_data) and not pd.isna(real_data):
                            pred_values.append(pred_data * 100 if variable != 'Term' else pred_data)
                            real_values.append(real_data * 100 if variable != 'Term' else real_data)
                            negocio_names.append(negocio)
                    else:
                        pred_data = self.df[
                            (self.df['Elaboracion'] == elaboracion_prediccion) & 
                            (self.df['Periodo'] == periodo) & 
                            (self.df['Concepto'] == variable) &
                            (self.df['Negocio'] == negocio)
                        ]['Valor'].sum() / 1_000_000
                        
                        real_data = self.df[
                            (self.df['Elaboracion'] == elaboracion_realidad) & 
                            (self.df['Periodo'] == periodo) & 
                            (self.df['Concepto'] == variable) &
                            (self.df['Negocio'] == negocio)
                        ]['Valor'].sum() / 1_000_000
                        
                        if not pd.isna(pred_data) and not pd.isna(real_data):
                            pred_values.append(pred_data)
                            real_values.append(real_data)
                            negocio_names.append(negocio)
                
                if pred_values and real_values:
                    fig.add_trace(
                        go.Bar(name='Predicción', x=negocio_names, y=pred_values, 
                               marker_color='#3498db', showlegend=(row==1 and col==1)),
                        row=row, col=col
                    )
                    fig.add_trace(
                        go.Bar(name='Realidad', x=negocio_names, y=real_values, 
                               marker_color='#e74c3c', showlegend=(row==1 and col==1)),
                        row=row, col=col
                    )
            
            fig.update_layout(
                title="Tendencias por Segmento de Negocio",
                height=600,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.info("No se pudieron generar los datos para el gráfico de tendencias.")
    
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
        
        # Extraer concepto específico si se menciona
        concepto_match = re.search(r'(resultado comercial|originacion|gross revenue|interest revenue|margen financiero|cost of fund|ad revenue|cost of risk|clientes|churn|term|ad rate|int rate|fund rate|rate all in|ntr|risk rate|spread)', query.lower())
        if concepto_match:
            concepto_especifico = concepto_match.group(1).title()
            if concepto_especifico == 'Resultado Comercial':
                variables_clave = ['Resultado Comercial']
            elif concepto_especifico == 'Originacion':
                variables_clave = ['Originacion Prom']
            elif concepto_especifico == 'Gross Revenue':
                variables_clave = ['Gross Revenue']
            elif concepto_especifico == 'Interest Revenue':
                variables_clave = ['Interest Revenue']
            elif concepto_especifico == 'Margen Financiero':
                variables_clave = ['Margen Financiero']
            elif concepto_especifico == 'Cost Of Fund':
                variables_clave = ['Cost of Fund']
            elif concepto_especifico == 'Ad Revenue':
                variables_clave = ['AD Revenue']
            elif concepto_especifico == 'Cost Of Risk':
                variables_clave = ['Cost of Risk']
            elif concepto_especifico == 'Clientes':
                variables_clave = ['Clientes']
            elif concepto_especifico == 'Churn':
                variables_clave = ['Churn Bruto']
            elif concepto_especifico == 'Term':
                variables_clave = ['Term']
            elif concepto_especifico == 'Ad Rate':
                variables_clave = ['AD Rate']
            elif concepto_especifico == 'Int Rate':
                variables_clave = ['Int Rate']
            elif concepto_especifico == 'Fund Rate':
                variables_clave = ['Fund Rate']
            elif concepto_especifico == 'Rate All In':
                variables_clave = ['Rate All In']
            elif concepto_especifico == 'Ntr':
                variables_clave = ['NTR']
            elif concepto_especifico == 'Risk Rate':
                variables_clave = ['Risk Rate']
            elif concepto_especifico == 'Spread':
                variables_clave = ['Spread']
            else:
                variables_clave = ['Rate All In', 'Originacion Prom', 'Term', 'Risk Rate', 'Fund Rate']
        else:
            # Variables clave para análisis (default)
            variables_clave = ['Rate All In', 'Originacion Prom', 'Term', 'Risk Rate', 'Fund Rate']
        
        # Variables que son rates (porcentajes) - no se suman, se muestran por clasificación/cohort
        rate_variables = ['Rate All In', 'Risk Rate', 'Fund Rate', 'Term']
        
        # Variables que se suman (valores monetarios)
        sum_variables = ['Originacion Prom']
        
        # Extraer negocio específico si se menciona
        negocio_match = re.search(r'(pyme|corp|brokers|wk)', query.lower())
        if negocio_match:
            negocio_especifico = negocio_match.group(1).upper()
            if negocio_especifico == 'BROKERS':
                negocio_especifico = 'Brokers'
            negocios = [negocio_especifico]
        else:
            # Obtener todos los negocios disponibles
            negocios = ['PYME', 'CORP', 'Brokers', 'WK']
        
        for negocio in negocios:
            analysis += f"<div class='business-title'>🏢 {negocio}</div>\n\n"
            
            # Si se especificó un concepto específico, mostrar solo ese
            if len(variables_clave) == 1 and variables_clave[0] in ['Resultado Comercial', 'Gross Revenue', 'Interest Revenue', 'Margen Financiero', 'Cost of Fund', 'AD Revenue', 'Cost of Risk', 'Clientes', 'Churn Bruto', 'NTR', 'Spread']:
                variable = variables_clave[0]
                analysis += f"💰 **Valores Monetarios:**\n"
                analysis += f"📈 **{variable}:**\n"
                
                valores_por_periodo = []
                for periodo in periodos:
                    valor = self._get_monetary_value(variable, elaboracion, periodo, escenario, negocio)
                    if valor is not None:
                        analysis += f"• {periodo}: ${valor:,.0f}\n"
                        valores_por_periodo.append(valor)
                    else:
                        analysis += f"• {periodo}: No hay datos disponibles\n"
                
                # Calcular tendencia
                if len(valores_por_periodo) >= 2:
                    primer_valor = valores_por_periodo[-1]  # Más antiguo
                    ultimo_valor = valores_por_periodo[0]   # Más reciente
                    
                    if primer_valor != 0:
                        cambio_porcentaje = ((ultimo_valor - primer_valor) / primer_valor) * 100
                        if cambio_porcentaje > 0:
                            analysis += f"**Tendencia:** 📈 Creciendo (+{cambio_porcentaje:.1f}%)\n"
                        else:
                            analysis += f"**Tendencia:** 📉 Decreciendo ({cambio_porcentaje:.1f}%)\n"
                
                analysis += "\n---\n\n"
            else:
                # Lógica original para múltiples variables
                # Primero mostrar rates (porcentajes)
                analysis += "  📊 **Rates (Porcentajes):**\n"
                for variable in rate_variables:
                    if variable in variables_clave:
                        analysis += f"    📈 **{variable}:**\n"
                        
                        # Mostrar datos por período y cohort
                        for periodo in periodos:
                            # Obtener datos para este período
                            data = self.df[
                                (self.df['Elaboracion'] == elaboracion) & 
                                (self.df['Periodo'] == periodo) & 
                                (self.df['Concepto'] == variable) &
                                (self.df['Negocio'] == negocio)
                            ]
                            
                            # Agregar filtro de escenario si se especifica
                            if escenario:
                                data = data[data['Escenario'] == escenario]
                            
                            analysis += f"    • {periodo}:\n"
                            
                            if len(data) > 0:
                                # Agrupar por cohort y mostrar valores
                                cohort_data = data.groupby('Cohort_Act')['Valor'].first()
                                for cohort, valor in cohort_data.items():
                                    # Manejar cohorts nulos
                                    if pd.isna(cohort):
                                        cohort_name = "Sin Cohort"
                                    else:
                                        cohort_name = str(cohort)
                                    
                                    # Formatear según el tipo de variable
                                    if variable == 'Term':
                                        # Term es un número entero
                                        analysis += f"      - {cohort_name}: {valor:.0f}\n"
                                    elif variable in ['Rate All In', 'Risk Rate', 'Fund Rate']:
                                        # Rates son porcentajes
                                        analysis += f"      - {cohort_name}: {valor*100:.2f}%\n"
                                    else:
                                        # Otras variables (por si acaso)
                                        analysis += f"      - {cohort_name}: {valor:.2f}\n"
                            else:
                                analysis += f"      - No hay datos disponibles\n"
                
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
                    
                    # Esta sección está duplicada - se elimina para evitar redundancia
                analysis += "\n"
            
                # Luego mostrar variables monetarias
                analysis += "  💰 **Valores Monetarios:**\n"
                for variable in sum_variables:
                    if variable in variables_clave:
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
        
        # Obtener cambios significativos para análisis y visualizaciones
        cambios_significativos = []
        for variable in variables_clave:
            if variable in rate_variables:
                cambios = self._get_significant_rate_changes(variable, elaboracion, periodos, escenario, negocios)
                if cambios:
                    cambios_significativos.extend(cambios)
            else:
                cambios = self._get_significant_monetary_changes(variable, elaboracion, periodos, escenario, negocios)
                if cambios:
                    cambios_significativos.extend(cambios)
        
        # Análisis automático de variables - Solo cambios significativos
        analysis += "📊 **Análisis Automático de Variables:**\n\n"
        
        # Analizar cada variable para todos los negocios
        for variable in variables_clave:
            if variable in rate_variables:
                # Análisis para rates
                rate_analysis = self._analyze_rate_variable(variable, elaboracion, periodos, escenario, negocios)
                if rate_analysis.strip():  # Solo mostrar si hay cambios significativos
                    analysis += f"🔍 **{variable}:**\n"
                    analysis += rate_analysis
                    analysis += "\n"
            else:
                # Análisis para variables monetarias
                monetary_analysis = self._analyze_monetary_variable(variable, elaboracion, periodos, escenario, negocios)
                if monetary_analysis.strip():  # Solo mostrar si hay cambios significativos
                    analysis += f"🔍 **{variable}:**\n"
                    analysis += monetary_analysis
                    analysis += "\n"
        
        # Storytelling completo
        analysis += self._generate_storytelling(elaboracion, periodos, escenario, negocios)
        
        # Marcar que se deben generar gráficos de últimos meses
        if cambios_significativos:
            analysis += "---\n\n"
            analysis += "## 📊 **VISUALIZACIONES INTERACTIVAS**\n\n"
            # Debug marker para generar gráficos (no visible al usuario)
            analysis += "**GENERATE_LAST_MONTHS_CHARTS:**\n"
            analysis += f"elaboracion={elaboracion}\n"
            analysis += f"periodos={periodos}\n"
            analysis += f"escenario={escenario}\n"
            analysis += f"negocios={negocios}\n"
        else:
            analysis += "ℹ️ No hay cambios significativos para visualizar.\n\n"
        
        # Detección de anomalías
        analysis += self.detect_anomalies(elaboracion, periodos, escenario, negocios)
        
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
    
    def _analyze_rate_variable(self, variable, elaboracion, periodos, escenario, negocios):
        """Análisis automático para variables de rate (porcentajes) - Comparativo entre períodos"""
        analysis = ""
        
        # Obtener datos para todos los negocios
        all_data = []
        for negocio in negocios:
            for periodo in periodos:
                filtro = (
                    (self.df['Elaboracion'] == elaboracion) & 
                    (self.df['Periodo'] == periodo) & 
                    (self.df['Concepto'] == variable) &
                    (self.df['Negocio'] == negocio)
                )
                
                if escenario:
                    filtro = filtro & (self.df['Escenario'] == escenario)
                
                data = self.df[filtro]
                if len(data) > 0:
                    # Agrupar por Cohort_Act y tomar solo el primer registro de cada cohort único
                    grouped = data.groupby('Cohort_Act')['Valor'].first().reset_index()
                    for _, row in grouped.iterrows():
                        cohort = row['Cohort_Act'] if pd.notna(row['Cohort_Act']) else 'Sin cohort'
                        valor = row['Valor']
                        all_data.append({
                            'negocio': negocio,
                            'periodo': periodo,
                            'cohort': cohort,
                            'valor': valor
                        })
        
        if not all_data:
            return "  ℹ️ No hay datos disponibles para este período.\n"
        
        # Convertir a DataFrame para análisis
        df_analysis = pd.DataFrame(all_data)
        
        # Análisis comparativo por período
        periodo_stats = df_analysis.groupby('periodo')['valor'].agg(['mean', 'count']).round(2)
        periodos_ordenados = sorted(periodo_stats.index)
        
        # Solo mostrar si hay cambios significativos (>0.1pp)
        cambios_significativos = False
        analysis += "  📅 **Comparación por Período:**\n"
        for i, periodo in enumerate(periodos_ordenados):
            stats = periodo_stats.loc[periodo]
            
            # Comparar con período anterior
            if i > 0:
                periodo_anterior = periodos_ordenados[i-1]
                valor_anterior = periodo_stats.loc[periodo_anterior, 'mean']
                valor_actual = stats['mean']
                cambio = valor_actual - valor_anterior
                porcentaje = (cambio / valor_anterior * 100) if valor_anterior != 0 else 0
                
                # Solo mostrar si el cambio es significativo (>0.1pp)
                if abs(cambio) > 0.1:
                    cambios_significativos = True
                    if cambio > 0:
                        emoji = "📈"
                        tendencia = "subió"
                    elif cambio < 0:
                        emoji = "📉"
                        tendencia = "bajó"
                    
                    analysis += f"    • {periodo}: {emoji} {tendencia} {abs(cambio):.2f}pp ({abs(porcentaje):.1f}%)\n"
        
        if not cambios_significativos:
            return "  ℹ️ No hay cambios significativos en este período.\n"
        
        # Análisis por negocio - comparación entre períodos
        analysis += "  🏢 **Análisis por Negocio:**\n"
        for negocio in negocios:
            negocio_data = df_analysis[df_analysis['negocio'] == negocio]
            if len(negocio_data) > 0:
                negocio_periodo = negocio_data.groupby('periodo')['valor'].mean().round(2)
                if len(negocio_periodo) > 1:
                    primer_periodo = negocio_periodo.iloc[0]
                    ultimo_periodo = negocio_periodo.iloc[-1]
                    cambio = ultimo_periodo - primer_periodo
                    porcentaje = (cambio / primer_periodo * 100) if primer_periodo != 0 else 0
                    
                    if cambio > 0:
                        emoji = "📈"
                        tendencia = "creció"
                    elif cambio < 0:
                        emoji = "📉"
                        tendencia = "decreció"
                    else:
                        emoji = "➡️"
                        tendencia = "se mantuvo"
                    
                    analysis += f"    • {negocio}: {emoji} {tendencia} {abs(cambio):.2f}pp ({abs(porcentaje):.1f}%)\n"
        
        # Análisis por cohort - comparación entre períodos
        analysis += "  📊 **Análisis por Cohort:**\n"
        for cohort in df_analysis['cohort'].unique():
            cohort_data = df_analysis[df_analysis['cohort'] == cohort]
            if len(cohort_data) > 0:
                cohort_periodo = cohort_data.groupby('periodo')['valor'].mean().round(2)
                if len(cohort_periodo) > 1:
                    primer_periodo = cohort_periodo.iloc[0]
                    ultimo_periodo = cohort_periodo.iloc[-1]
                    cambio = ultimo_periodo - primer_periodo
                    porcentaje = (cambio / primer_periodo * 100) if primer_periodo != 0 else 0
                    
                    if cambio > 0:
                        emoji = "📈"
                        tendencia = "creció"
                    elif cambio < 0:
                        emoji = "📉"
                        tendencia = "decreció"
                    else:
                        emoji = "➡️"
                        tendencia = "se mantuvo"
                    
                    analysis += f"    • {cohort}: {emoji} {tendencia} {abs(cambio):.2f}pp ({abs(porcentaje):.1f}%)\n"
        
        return analysis
    
    def _analyze_monetary_variable(self, variable, elaboracion, periodos, escenario, negocios):
        """Análisis automático para variables monetarias - Comparativo entre períodos"""
        analysis = ""
        
        # Obtener datos para todos los negocios
        all_data = []
        for negocio in negocios:
            for periodo in periodos:
                filtro = (
                    (self.df['Elaboracion'] == elaboracion) & 
                    (self.df['Periodo'] == periodo) & 
                    (self.df['Concepto'] == variable) &
                    (self.df['Negocio'] == negocio)
                )
                
                if escenario:
                    filtro = filtro & (self.df['Escenario'] == escenario)
                
                data = self.df[filtro]
                if len(data) > 0:
                    # Para variables monetarias, sumar todos los valores del período
                    valor = data['Valor'].sum()
                    all_data.append({
                        'negocio': negocio,
                        'periodo': periodo,
                        'valor': valor
                    })
        
        if not all_data:
            return "  ℹ️ No hay datos disponibles para este período.\n"
        
        # Convertir a DataFrame para análisis
        df_analysis = pd.DataFrame(all_data)
        
        # Análisis comparativo por período
        periodo_stats = df_analysis.groupby('periodo')['valor'].sum().round(0)
        periodos_ordenados = sorted(periodo_stats.index)
        
        # Solo mostrar si hay cambios significativos (>3%)
        cambios_significativos = False
        analysis += "  📅 **Comparación por Período:**\n"
        for i, periodo in enumerate(periodos_ordenados):
            valor = periodo_stats.loc[periodo]
            
            # Comparar con período anterior
            if i > 0:
                periodo_anterior = periodos_ordenados[i-1]
                valor_anterior = periodo_stats.loc[periodo_anterior]
                valor_actual = valor
                cambio = valor_actual - valor_anterior
                porcentaje = (cambio / valor_anterior * 100) if valor_anterior != 0 else 0
                
                # Solo mostrar si el cambio es significativo (>3%)
                if abs(porcentaje) > 3:
                    cambios_significativos = True
                    if cambio > 0:
                        emoji = "📈"
                        tendencia = "subió"
                    elif cambio < 0:
                        emoji = "📉"
                        tendencia = "bajó"
                    
                    analysis += f"    • {periodo}: {emoji} {tendencia} ${abs(cambio):,.0f} ({abs(porcentaje):.1f}%)\n"
        
        if not cambios_significativos:
            return "  ℹ️ No hay cambios significativos en este período.\n"
        
        # Análisis por negocio - comparación entre períodos
        analysis += "  🏢 **Análisis por Negocio:**\n"
        for negocio in negocios:
            negocio_data = df_analysis[df_analysis['negocio'] == negocio]
            if len(negocio_data) > 0:
                negocio_periodo = negocio_data.groupby('periodo')['valor'].sum().round(0)
                if len(negocio_periodo) > 1:
                    primer_periodo = negocio_periodo.iloc[0]
                    ultimo_periodo = negocio_periodo.iloc[-1]
                    cambio = ultimo_periodo - primer_periodo
                    porcentaje = (cambio / primer_periodo * 100) if primer_periodo != 0 else 0
                    
                    if cambio > 0:
                        emoji = "📈"
                        tendencia = "creció"
                    elif cambio < 0:
                        emoji = "📉"
                        tendencia = "decreció"
                    else:
                        emoji = "➡️"
                        tendencia = "se mantuvo"
                    
                    analysis += f"    • {negocio}: {emoji} {tendencia} ${abs(cambio):,.0f} ({abs(porcentaje):.1f}%)\n"
        
        # Análisis de concentración por período
        if variable == 'Originacion Prom':
            analysis += "  🎯 **Concentración por Período:**\n"
            for periodo in periodos_ordenados:
                periodo_data = df_analysis[df_analysis['periodo'] == periodo]
                negocio_periodo = periodo_data.groupby('negocio')['valor'].sum().round(0)
                total_periodo = negocio_periodo.sum()
                
                if total_periodo > 0:
                    negocio_dominante = negocio_periodo.idxmax()
                    porcentaje_dominante = (negocio_periodo.max() / total_periodo * 100)
                    analysis += f"    • {periodo}: {negocio_dominante} lidera ({porcentaje_dominante:.1f}%)\n"
        
        return analysis
    
    def _generate_storytelling(self, elaboracion, periodos, escenario, negocios):
        """Generar storytelling elegante y profesional en un párrafo estético"""
        storytelling = "📖 **ANÁLISIS FINANCIERO EJECUTIVO**\n\n"
        
        # Obtener datos para análisis
        variables_clave = ['Rate All In', 'New Active', 'Churn Bruto', 'Resucitados', 'Originacion Prom', 'Term', 'Risk Rate', 'Fund Rate']
        rate_variables = ['Rate All In', 'Risk Rate', 'Fund Rate', 'Term']
        
        # Análisis de cambios significativos
        cambios_significativos = []
        
        for variable in variables_clave:
            if variable in rate_variables:
                # Análisis para rates
                cambios = self._get_significant_rate_changes(variable, elaboracion, periodos, escenario, negocios)
                if cambios:
                    cambios_significativos.extend(cambios)
            else:
                # Análisis para variables monetarias
                cambios = self._get_significant_monetary_changes(variable, elaboracion, periodos, escenario, negocios)
                if cambios:
                    cambios_significativos.extend(cambios)
        
        if not cambios_significativos:
            storytelling += "ℹ️ **No se detectaron cambios significativos** en el período analizado. Los indicadores se mantuvieron estables.\n\n"
            return storytelling
        
        # Ordenar cambios por magnitud
        cambios_significativos.sort(key=lambda x: abs(x['magnitud']), reverse=True)
        
        # Header elegante
        storytelling += f"**📅 Período:** {elaboracion} | **🎯 Escenario:** {escenario} | **📊 Meses:** {len(periodos)}\n\n"
        
        # Analizar tendencia general
        cambios_positivos = [c for c in cambios_significativos if c['tendencia'] in ['creció', 'subió']]
        cambios_negativos = [c for c in cambios_significativos if c['tendencia'] in ['decreció', 'bajó']]
        
        if len(cambios_negativos) > len(cambios_positivos):
            tendencia_general = "**tendencia general negativa**"
            contexto = "deterioro en varios indicadores críticos que requiere **atención inmediata** y revisión de estrategias operativas"
        elif len(cambios_positivos) > len(cambios_negativos):
            tendencia_general = "**tendencia general positiva**"
            contexto = "mejoras en múltiples indicadores clave que valida las estrategias implementadas y sugiere **oportunidades de crecimiento**"
        else:
            tendencia_general = "**tendencia general mixta**"
            contexto = "resultados mixtos entre segmentos que requiere **análisis granular** y estrategias diferenciadas por área de negocio"
        
        # Top 3 cambios más críticos
        top_cambios = cambios_significativos[:3]
        
        # Generar párrafo estético
        storytelling += f"El análisis de rendimiento para el período **{elaboracion}** en escenario **{escenario}** revela una {tendencia_general} con {contexto}. "
        
        # Analizar por segmento
        analisis_por_negocio = []
        for negocio in negocios:
            cambios_negocio = [c for c in cambios_significativos if c['negocio'] == negocio]
            if cambios_negocio:
                cambios_pos_negocio = [c for c in cambios_negocio if c['tendencia'] in ['creció', 'subió']]
                cambios_neg_negocio = [c for c in cambios_negocio if c['tendencia'] in ['decreció', 'bajó']]
                
                if len(cambios_neg_negocio) > len(cambios_pos_negocio):
                    tendencia_negocio = "**deterioro**"
                elif len(cambios_pos_negocio) > len(cambios_neg_negocio):
                    tendencia_negocio = "**crecimiento**"
                else:
                    tendencia_negocio = "**comportamiento mixto**"
                
                # Cambio más significativo del negocio
                cambio_principal = max(cambios_negocio, key=lambda x: abs(x['magnitud']))
                if cambio_principal['tipo'] == 'rate':
                    if cambio_principal['magnitud'] > 0:
                        cambio_texto = f"**{cambio_principal['variable']}** mejoró +{abs(cambio_principal['magnitud']):.2f}pp"
                    else:
                        cambio_texto = f"**{cambio_principal['variable']}** se deterioró {cambio_principal['magnitud']:.2f}pp"
                else:
                    if cambio_principal['magnitud'] > 0:
                        cambio_texto = f"**{cambio_principal['variable']}** creció +${abs(cambio_principal['magnitud']):,.0f}"
                    else:
                        cambio_texto = f"**{cambio_principal['variable']}** decreció ${cambio_principal['magnitud']:,.0f}"
                
                analisis_por_negocio.append(f"**{negocio}** muestra {tendencia_negocio} con {cambio_texto}")
        
        if analisis_por_negocio:
            storytelling += "Por segmento, " + ", ".join(analisis_por_negocio) + ". "
        
        # Recomendaciones estratégicas
        if len(cambios_negativos) > len(cambios_positivos):
            storytelling += "Se recomienda **revisión urgente** de las estrategias operativas, **implementación de medidas de apoyo** para segmentos en deterioro, y **desarrollo de planes de recuperación** específicos por área de negocio. "
        elif len(cambios_positivos) > len(cambios_negativos):
            storytelling += "Se recomienda **capitalizar el momentum positivo**, **replicar las mejores prácticas** en segmentos exitosos, y **acelerar la expansión** en áreas de crecimiento. "
        else:
            storytelling += "Se recomienda **análisis granular** por segmento, **estrategias diferenciadas** según el comportamiento específico, y **monitoreo continuo** para optimizar el rendimiento. "
        
        storytelling += "La implementación de **monitoreo en tiempo real** y **alertas automáticas** permitirá una **respuesta ágil** a las condiciones del mercado, mientras que el desarrollo de **modelos predictivos más granulares** mejorará la precisión de las proyecciones futuras."
        
        return storytelling
    
    def _generate_executive_summary(self, cambios_significativos):
        """Generar resumen ejecutivo elegante"""
        cambios_positivos = [c for c in cambios_significativos if c['tendencia'] in ['creció', 'subió']]
        cambios_negativos = [c for c in cambios_significativos if c['tendencia'] in ['decreció', 'bajó']]
        
        summary = "## 🎯 **RESUMEN EJECUTIVO**\n\n"
        
        if len(cambios_negativos) > len(cambios_positivos):
            summary += "El análisis revela una **tendencia general negativa** con deterioro en varios indicadores críticos. "
            summary += "Esta situación requiere **atención inmediata** y revisión de estrategias operativas.\n\n"
            
            # Destacar los cambios más críticos
            top_negativos = sorted(cambios_negativos, key=lambda x: abs(x['magnitud']), reverse=True)[:2]
            summary += "**🔴 Cambios más críticos:**\n"
            for cambio in top_negativos:
                if cambio['tipo'] == 'rate':
                    summary += f"• **{cambio['variable']}** en {cambio['negocio']}: {abs(cambio['magnitud']):.2f}pp ({abs(cambio['porcentaje']):.1f}%)\n"
                else:
                    summary += f"• **{cambio['variable']}** en {cambio['negocio']}: ${abs(cambio['magnitud']):,.0f} ({abs(cambio['porcentaje']):.1f}%)\n"
            summary += "\n"
            
        elif len(cambios_positivos) > len(cambios_negativos):
            summary += "El análisis revela una **tendencia general positiva** con mejoras en múltiples indicadores clave. "
            summary += "Esta situación valida las estrategias implementadas y sugiere **oportunidades de crecimiento**.\n\n"
            
            # Destacar los cambios más positivos
            top_positivos = sorted(cambios_positivos, key=lambda x: abs(x['magnitud']), reverse=True)[:2]
            summary += "**🟢 Cambios más positivos:**\n"
            for cambio in top_positivos:
                if cambio['tipo'] == 'rate':
                    summary += f"• **{cambio['variable']}** en {cambio['negocio']}: +{cambio['magnitud']:.2f}pp (+{cambio['porcentaje']:.1f}%)\n"
                else:
                    summary += f"• **{cambio['variable']}** en {cambio['negocio']}: +${cambio['magnitud']:,.0f} (+{cambio['porcentaje']:.1f}%)\n"
            summary += "\n"
            
        else:
            summary += "El análisis revela un **comportamiento mixto** con mejoras en algunos indicadores y deterioro en otros. "
            summary += "Esta situación requiere **estrategias diferenciadas** y **monitoreo continuo**.\n\n"
        
        return summary
    
    def _generate_variable_analysis(self, cambios_significativos):
        """Generar análisis por variable con formato elegante"""
        # Agrupar por variable
        variables_impacto = {}
        for cambio in cambios_significativos:
            var = cambio['variable']
            if var not in variables_impacto:
                variables_impacto[var] = []
            variables_impacto[var].append(cambio)
        
        # Ordenar variables por impacto total
        variables_ordenadas = sorted(variables_impacto.items(), 
                                   key=lambda x: sum(abs(c['magnitud']) for c in x[1]), 
                                   reverse=True)
        
        analysis = "## 📈 **ANÁLISIS POR VARIABLE CLAVE**\n\n"
        
        for i, (variable, cambios_var) in enumerate(variables_ordenadas[:3]):  # Top 3 variables
            analysis += f"### 🔍 **{variable}**\n\n"
            
            # Análisis específico por variable
            if variable == 'Originacion Prom':
                analysis += self._analyze_originacion_prom_elegant(cambios_var)
            elif variable == 'Rate All In':
                analysis += self._analyze_rate_all_in_elegant(cambios_var)
            elif variable == 'Term':
                analysis += self._analyze_term_elegant(cambios_var)
            elif variable == 'Risk Rate':
                analysis += self._analyze_risk_rate_elegant(cambios_var)
            elif variable == 'Fund Rate':
                analysis += self._analyze_fund_rate_elegant(cambios_var)
            else:
                analysis += self._analyze_generic_variable_elegant(variable, cambios_var)
            
            analysis += "\n"
        
        return analysis
    
    def _generate_business_analysis(self, cambios_significativos):
        """Generar análisis por segmento con formato elegante"""
        # Agrupar por negocio
        negocios_cambios = {}
        for cambio in cambios_significativos:
            negocio = cambio['negocio']
            if negocio not in negocios_cambios:
                negocios_cambios[negocio] = []
            negocios_cambios[negocio].append(cambio)
        
        analysis = "## 🏢 **ANÁLISIS POR SEGMENTO DE NEGOCIO**\n\n"
        
        for negocio in ['PYME', 'CORP', 'Brokers', 'WK']:
            if negocio in negocios_cambios:
                analysis += f"### 🏢 **{negocio}**\n\n"
                analysis += self._analyze_business_segment_elegant(negocio, negocios_cambios[negocio])
                analysis += "\n"
        
        return analysis
    
    def _generate_strategic_recommendations_elegant(self, cambios_significativos):
        """Generar recomendaciones estratégicas elegantes"""
        recommendations = "## 💡 **RECOMENDACIONES ESTRATÉGICAS**\n\n"
        
        # Analizar patrones para recomendaciones específicas
        cambios_positivos = [c for c in cambios_significativos if c['tendencia'] in ['creció', 'subió']]
        cambios_negativos = [c for c in cambios_significativos if c['tendencia'] in ['decreció', 'bajó']]
        
        # Recomendación 1: Estrategia de adquisición
        originacion_cambios = [c for c in cambios_negativos if 'Originacion' in c['variable']]
        if originacion_cambios:
            recommendations += "### 🎯 **Estrategia de Adquisición**\n\n"
            recommendations += "La **contracción** en Originación Promedio requiere una **revisión integral** de las estrategias de adquisición. "
            recommendations += "Se recomienda implementar **campañas de marketing dirigidas**, **optimizar los procesos** de onboarding y "
            recommendations += "**fortalecer la propuesta de valor** diferenciada por segmento.\n\n"
        
        # Recomendación 2: Gestión de riesgo
        risk_cambios = [c for c in cambios_negativos if 'Risk' in c['variable']]
        if risk_cambios:
            recommendations += "### ⚠️ **Gestión de Riesgo**\n\n"
            recommendations += "El deterioro en Risk Rate indica **mayor exposición al riesgo**. Se recomienda **revisar los criterios** de evaluación, "
            recommendations += "**ajustar los modelos** de scoring y **implementar controles** adicionales para mitigar el riesgo crediticio.\n\n"
        
        # Recomendación 3: Retención de clientes
        term_cambios = [c for c in cambios_negativos if c['variable'] == 'Term']
        if term_cambios:
            recommendations += "### 🔄 **Retención de Clientes**\n\n"
            recommendations += "La **reducción** en Term indica **desafíos en la retención**. Se recomienda implementar **programas de fidelización**, "
            recommendations += "**mejorar la experiencia del cliente** y desarrollar estrategias de **upselling y cross-selling**.\n\n"
        
        # Recomendación 4: Estrategia diferenciada
        if cambios_positivos and cambios_negativos:
            recommendations += "### 🎨 **Estrategia Diferenciada**\n\n"
            recommendations += "La **naturaleza mixta** de los resultados sugiere la necesidad de **estrategias diferenciadas** por segmento. "
            recommendations += "Se recomienda desarrollar **planes de acción específicos** para cada área de negocio, "
            recommendations += "**capitalizando las fortalezas** identificadas y **abordando las debilidades** detectadas.\n\n"
        
        # Recomendación 5: Monitoreo continuo
        recommendations += "### 📊 **Monitoreo Continuo**\n\n"
        recommendations += "Se recomienda implementar un **sistema de monitoreo en tiempo real** para detectar **cambios tempranos** en los indicadores clave "
        recommendations += "y permitir una **respuesta ágil** a las condiciones del mercado. Esto incluye **alertas automáticas** y **dashboards** ejecutivos.\n\n"
        
        return recommendations
    
    def _analyze_originacion_prom_elegant(self, cambios):
        """Análisis elegante de Originacion Prom"""
        analysis = ""
        
        cambios_positivos = [c for c in cambios if c['tendencia'] == 'creció']
        cambios_negativos = [c for c in cambios if c['tendencia'] == 'decreció']
        
        if cambios_negativos and not cambios_positivos:
            analysis += "La **Originación Promedio** presenta un **deterioro generalizado** en todos los segmentos analizados. "
            analysis += "Esta **caída sistemática** en los volúmenes de originación sugiere **desafíos estructurales** en la capacidad de adquisición de nuevos clientes.\n\n"
            
            for cambio in cambios_negativos:
                analysis += f"El segmento **{cambio['negocio']}** registra la mayor **contracción** con una reducción de ${abs(cambio['magnitud']):,.0f} ({abs(cambio['porcentaje']):.1f}%), "
                analysis += f"lo que representa un **riesgo significativo** para la **sostenibilidad del negocio** en este segmento.\n\n"
            
        elif cambios_positivos and not cambios_negativos:
            analysis += "La **Originación Promedio** muestra un **crecimiento robusto** en todos los segmentos, "
            analysis += "indicando una **estrategia de adquisición exitosa** y una **demanda saludable** en el mercado.\n\n"
            
            for cambio in cambios_positivos:
                analysis += f"El segmento **{cambio['negocio']}** destaca con un **crecimiento** de ${cambio['magnitud']:,.0f} ({cambio['porcentaje']:.1f}%), "
                analysis += f"demostrando una **excelente penetración** en este nicho de mercado.\n\n"
            
        else:
            analysis += "La **Originación Promedio** presenta un **comportamiento mixto** entre segmentos, "
            analysis += "con algunos mostrando **crecimiento** mientras otros experimentan **contracción**.\n\n"
            
            for cambio in cambios:
                if cambio['tendencia'] == 'creció':
                    analysis += f"**{cambio['negocio']}** registra un **crecimiento positivo** de ${cambio['magnitud']:,.0f} ({cambio['porcentaje']:.1f}%), "
                    analysis += f"indicando **fortaleza** en este segmento.\n\n"
                else:
                    analysis += f"**{cambio['negocio']}** experimenta una **contracción** de ${abs(cambio['magnitud']):,.0f} ({abs(cambio['porcentaje']):.1f}%), "
                    analysis += f"requiriendo **atención estratégica**.\n\n"
        
        return analysis
    
    def _analyze_rate_all_in_elegant(self, cambios):
        """Análisis elegante de Rate All In"""
        analysis = ""
        
        cambios_positivos = [c for c in cambios if c['tendencia'] == 'subió']
        cambios_negativos = [c for c in cambios if c['tendencia'] == 'bajó']
        
        if cambios_positivos and not cambios_negativos:
            analysis += "El **Rate All In** muestra una **tendencia alcista** en todos los segmentos, "
            analysis += "indicando una **mejora en la rentabilidad** y **fortalecimiento de la propuesta de valor**.\n\n"
            
        elif cambios_negativos and not cambios_positivos:
            analysis += "El **Rate All In** presenta una **tendencia bajista** generalizada, "
            analysis += "sugiriendo **presión competitiva** o **ajustes en la estrategia de pricing**.\n\n"
            
        else:
            analysis += "El **Rate All In** muestra un **comportamiento diverso** entre segmentos, "
            analysis += "reflejando **estrategias de pricing diferenciadas** por tipo de cliente.\n\n"
        
        return analysis
    
    def _analyze_term_elegant(self, cambios):
        """Análisis elegante de Term"""
        analysis = ""
        
        cambios_positivos = [c for c in cambios if c['tendencia'] == 'subió']
        cambios_negativos = [c for c in cambios if c['tendencia'] == 'bajó']
        
        if cambios_positivos and not cambios_negativos:
            analysis += "El **Term** muestra una **tendencia alcista** en todos los segmentos, "
            analysis += "indicando una **mejora en la retención de clientes** y **fortalecimiento de la relación**.\n\n"
            
        elif cambios_negativos and not cambios_positivos:
            analysis += "El **Term** presenta una **tendencia bajista** generalizada, "
            analysis += "sugiriendo **desafíos en la retención** o **cambios en las preferencias** de los clientes.\n\n"
            
        else:
            analysis += "El **Term** muestra un **comportamiento diverso** entre segmentos, "
            analysis += "reflejando **diferentes patrones de retención** por tipo de cliente.\n\n"
        
        return analysis
    
    def _analyze_risk_rate_elegant(self, cambios):
        """Análisis elegante de Risk Rate"""
        analysis = ""
        
        cambios_positivos = [c for c in cambios if c['tendencia'] == 'subió']
        cambios_negativos = [c for c in cambios if c['tendencia'] == 'bajó']
        
        if cambios_positivos and not cambios_negativos:
            analysis += "El **Risk Rate** muestra una **tendencia alcista** en todos los segmentos, "
            analysis += "indicando una **mayor exposición al riesgo** y **necesidad de revisión** de criterios de evaluación.\n\n"
            
        elif cambios_negativos and not cambios_positivos:
            analysis += "El **Risk Rate** presenta una **tendencia bajista** generalizada, "
            analysis += "sugiriendo una **mejora en la calidad** de la cartera y **efectividad** de los controles de riesgo.\n\n"
            
        else:
            analysis += "El **Risk Rate** muestra un **comportamiento diverso** entre segmentos, "
            analysis += "reflejando **diferentes niveles de riesgo** por tipo de cliente.\n\n"
        
        return analysis
    
    def _analyze_fund_rate_elegant(self, cambios):
        """Análisis elegante de Fund Rate"""
        analysis = ""
        
        cambios_positivos = [c for c in cambios if c['tendencia'] == 'subió']
        cambios_negativos = [c for c in cambios if c['tendencia'] == 'bajó']
        
        if cambios_positivos and not cambios_negativos:
            analysis += "El **Fund Rate** muestra una **tendencia alcista** en todos los segmentos, "
            analysis += "indicando un **aumento en los costos de fondeo** y **presión en los márgenes**.\n\n"
            
        elif cambios_negativos and not cambios_positivos:
            analysis += "El **Fund Rate** presenta una **tendencia bajista** generalizada, "
            analysis += "sugiriendo una **mejora en los costos de fondeo** y **optimización** de la estructura de financiamiento.\n\n"
            
        else:
            analysis += "El **Fund Rate** muestra un **comportamiento diverso** entre segmentos, "
            analysis += "reflejando **diferentes estructuras de fondeo** por tipo de cliente.\n\n"
        
        return analysis
    
    def _analyze_generic_variable_elegant(self, variable, cambios):
        """Análisis elegante de variable genérica"""
        analysis = ""
        
        cambios_positivos = [c for c in cambios if c['tendencia'] in ['creció', 'subió']]
        cambios_negativos = [c for c in cambios if c['tendencia'] in ['decreció', 'bajó']]
        
        if cambios_positivos and not cambios_negativos:
            analysis += f"La variable **{variable}** muestra una **tendencia positiva** en todos los segmentos, "
            analysis += f"indicando **mejoras significativas** en este indicador clave.\n\n"
            
        elif cambios_negativos and not cambios_positivos:
            analysis += f"La variable **{variable}** presenta una **tendencia negativa** generalizada, "
            analysis += f"sugiriendo **desafíos** que requieren **atención estratégica**.\n\n"
            
        else:
            analysis += f"La variable **{variable}** muestra un **comportamiento mixto** entre segmentos, "
            analysis += f"reflejando **diferentes dinámicas** por tipo de cliente.\n\n"
        
        return analysis
    
    def _analyze_business_segment_elegant(self, negocio, cambios):
        """Análisis elegante por segmento de negocio"""
        analysis = ""
        
        # Contexto del segmento
        if negocio == 'PYME':
            analysis += "El segmento **PYME** representa el **núcleo del negocio** y su desempeño es crítico para la **sostenibilidad operativa**. "
        elif negocio == 'CORP':
            analysis += "El segmento **CORP** constituye el **motor de crecimiento principal** y su evolución impacta significativamente en los **resultados consolidados**. "
        elif negocio == 'Brokers':
            analysis += "El segmento **Brokers** actúa como un **canal de distribución clave** y su rendimiento refleja la eficiencia de las **estrategias de canal**. "
        elif negocio == 'WK':
            analysis += "El segmento **WK** representa una **oportunidad de crecimiento emergente** y su desarrollo es fundamental para la **diversificación del negocio**. "
        
        # Analizar todos los cambios del segmento
        if cambios:
            # Separar cambios positivos y negativos
            cambios_positivos = [c for c in cambios if c['tendencia'] in ['subió', 'creció']]
            cambios_negativos = [c for c in cambios if c['tendencia'] in ['bajó', 'decreció']]
            
            if cambios_positivos and not cambios_negativos:
                analysis += "Los resultados muestran una **tendencia completamente positiva** con mejoras en múltiples indicadores, "
                analysis += "sugiriendo una **estrategia exitosa** en este segmento.\n\n"
            elif cambios_negativos and not cambios_positivos:
                analysis += "Los resultados revelan una **tendencia completamente negativa** con deterioro en múltiples indicadores, "
                analysis += "indicando la necesidad de **intervención estratégica inmediata**.\n\n"
            else:
                analysis += "Los resultados presentan un **comportamiento mixto** con mejoras en algunos indicadores y deterioro en otros, "
                analysis += "sugiriendo la necesidad de **estrategias diferenciadas**.\n\n"
            
            # Detallar los cambios más importantes
            cambios_ordenados = sorted(cambios, key=lambda x: abs(x['magnitud']), reverse=True)
            for i, cambio in enumerate(cambios_ordenados[:2]):  # Solo los 2 más importantes
                if cambio['tipo'] == 'rate':
                    if cambio['tendencia'] in ['subió', 'creció']:
                        analysis += f"• **{cambio['variable']}** registra una **mejora** de {cambio['magnitud']:.2f}pp ({cambio['porcentaje']:.1f}%), "
                        analysis += f"indicando **fortaleza** en este indicador.\n\n"
                    else:
                        analysis += f"• **{cambio['variable']}** experimenta una **reducción** de {abs(cambio['magnitud']):.2f}pp ({abs(cambio['porcentaje']):.1f}%), "
                        analysis += f"requiriendo **atención estratégica**.\n\n"
                else:
                    if cambio['tendencia'] in ['subió', 'creció']:
                        analysis += f"• **{cambio['variable']}** presenta un **crecimiento** de ${cambio['magnitud']:,.0f} ({cambio['porcentaje']:.1f}%), "
                        analysis += f"demostrando **fortaleza** en este segmento.\n\n"
                    else:
                        analysis += f"• **{cambio['variable']}** registra una **contracción** de ${abs(cambio['magnitud']):,.0f} ({abs(cambio['porcentaje']):.1f}%), "
                        analysis += f"sugiriendo **desafíos** en este segmento.\n\n"
            
            # Recomendaciones específicas por negocio
            if negocio == 'PYME':
                if cambios_negativos:
                    analysis += "**Recomendación estratégica:** Dado el carácter crítico del segmento PYME, se recomienda implementar un **plan de acción inmediato** "
                    analysis += "que incluya **revisión de pricing**, **optimización de procesos** y **fortalecimiento de la propuesta de valor**.\n\n"
                else:
                    analysis += "**Recomendación estratégica:** El crecimiento en PYME valida la estrategia actual. Se recomienda **capitalizar este momentum** "
                    analysis += "para **acelerar la expansión** y replicar las mejores prácticas en otros segmentos.\n\n"
            elif negocio == 'CORP':
                if cambios_negativos:
                    analysis += "**Recomendación estratégica:** El deterioro en CORP requiere una **revisión urgente** de la estrategia de crecimiento "
                    analysis += "y la implementación de **medidas de apoyo** para fortalecer la **sostenibilidad del segmento**.\n\n"
                else:
                    analysis += "**Recomendación estratégica:** El crecimiento en CORP presenta una **oportunidad** para acelerar la expansión "
                    analysis += "y replicar las **mejores prácticas** en otros segmentos.\n\n"
            elif negocio == 'Brokers':
                if cambios_negativos:
                    analysis += "**Recomendación estratégica:** El deterioro en Brokers requiere una **revisión de la estrategia de canal** "
                    analysis += "y la implementación de **medidas de apoyo** para fortalecer la **red de distribución**.\n\n"
                else:
                    analysis += "**Recomendación estratégica:** El crecimiento en Brokers valida la estrategia de canal. Se recomienda **expandir la red** "
                    analysis += "y **optimizar los procesos** de distribución.\n\n"
            elif negocio == 'WK':
                if cambios_negativos:
                    analysis += "**Recomendación estratégica:** El deterioro en WK sugiere desafíos en la estrategia de diversificación. "
                    analysis += "Se recomienda **revisar el modelo de negocio** y **ajustar la propuesta de valor**.\n\n"
                else:
                    analysis += "**Recomendación estratégica:** El crecimiento en WK valida la **estrategia de diversificación** "
                    analysis += "y sugiere **oportunidades** para expandir la presencia en este **segmento emergente**.\n\n"
        
        return analysis
    
    def generate_visualizations(self, cambios_significativos, elaboracion, periodos, escenario):
        """Generar visualizaciones con Plotly para los cambios significativos"""
        if not cambios_significativos:
            return "ℹ️ No hay cambios significativos para visualizar.\n\n"
        
        visualizations = "📊 **VISUALIZACIONES INTERACTIVAS:**\n\n"
        
        # 1. Gráfico de barras - Top cambios por magnitud
        visualizations += self._create_top_changes_chart(cambios_significativos)
        
        # 2. Gráfico de líneas - Tendencias temporales
        visualizations += self._create_trends_chart(cambios_significativos, elaboracion, periodos, escenario)
        
        # 3. Gráfico de torta - Distribución por segmento
        visualizations += self._create_segment_distribution_chart(cambios_significativos)
        
        # 4. Heatmap - Cambios por variable y negocio
        visualizations += self._create_heatmap_chart(cambios_significativos)
        
        return visualizations
    
    def _get_significant_changes_for_charts(self, elaboracion, periodos, escenario, negocios):
        """Regenerar cambios significativos para los gráficos"""
        cambios_significativos = []
        
        # Variables de tasa
        rate_variables = ['Rate All In', 'Risk Rate', 'Fund Rate', 'Term']
        for variable in rate_variables:
            cambios = self._get_significant_rate_changes(variable, elaboracion, periodos, escenario, negocios)
            cambios_significativos.extend(cambios)
        
        # Variables monetarias
        sum_variables = ['Originacion Prom', 'New Active', 'Churn Bruto', 'Resucitados']
        for variable in sum_variables:
            cambios = self._get_significant_monetary_changes(variable, elaboracion, periodos, escenario, negocios)
            cambios_significativos.extend(cambios)
        
        return cambios_significativos

    def generate_visualizations_streamlit(self, cambios_significativos, elaboracion, periodos, escenario):
        """Generar visualizaciones específicas para análisis de últimos meses"""
        if not cambios_significativos:
            st.info("ℹ️ No hay cambios significativos para visualizar.")
            return
        
        st.markdown("📊 **VISUALIZACIONES INTERACTIVAS:**")
        
        # 1. Gráfico de tendencias temporales por variable
        st.markdown("**Gráfico 1: Tendencias Temporales por Variable**")
        self._create_temporal_trends_chart_streamlit(elaboracion, periodos, escenario)
        
        # 2. Gráfico de comparación entre períodos
        st.markdown("**Gráfico 2: Comparación Período Inicial vs Final**")
        self._create_period_comparison_chart_streamlit(elaboracion, periodos, escenario)
        
        # 3. Gráfico de evolución por negocio
        st.markdown("**Gráfico 3: Evolución por Segmento de Negocio**")
        self._create_business_evolution_chart_streamlit(elaboracion, periodos, escenario)
        
        # 4. Heatmap de cambios significativos
        st.markdown("**Gráfico 4: Heatmap de Cambios Significativos**")
        self._create_significant_changes_heatmap_streamlit(cambios_significativos)
    
    def _create_temporal_trends_chart_streamlit(self, elaboracion, periodos, escenario):
        """Crear gráfico de tendencias temporales por variable"""
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        # Obtener datos para cada variable clave
        variables = ['Rate All In', 'Originacion Prom', 'Term', 'Risk Rate']
        negocios = ['PYME', 'CORP', 'Brokers', 'WK']
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=variables,
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        
        for i, variable in enumerate(variables):
            row = (i // 2) + 1
            col = (i % 2) + 1
            
            for j, negocio in enumerate(negocios):
                # Obtener datos para esta variable y negocio
                data = self.df[
                    (self.df['Elaboracion'] == elaboracion) &
                    (self.df['Escenario'] == escenario) &
                    (self.df['Negocio'] == negocio) &
                    (self.df['Concepto'] == variable) &
                    (self.df['Periodo'].isin(periodos))
                ].copy()
                
                if not data.empty:
                    # Agrupar por período y obtener el valor promedio
                    period_data = data.groupby('Periodo')['Valor'].mean().reset_index()
                    period_data = period_data.sort_values('Periodo')
                    
                    # Formatear valores según el tipo de variable
                    if variable in ['Rate All In', 'Risk Rate', 'Fund Rate']:
                        y_values = period_data['Valor'] * 100  # Convertir a porcentaje
                        y_title = "Valor (%)"
                    elif variable == 'Term':
                        y_values = period_data['Valor']
                        y_title = "Valor (días)"
                    else:  # Originacion Prom
                        y_values = period_data['Valor'] / 1000000  # Convertir a millones
                        y_title = "Valor (M$)"
                    
                    fig.add_trace(
                        go.Scatter(
                            x=period_data['Periodo'],
                            y=y_values,
                            mode='lines+markers',
                            name=f"{variable} - {negocio}",
                            line=dict(color=colors[j % len(colors)], width=2),
                            marker=dict(size=8)
                        ),
                        row=row, col=col
                    )
            
            # Configurar ejes
            fig.update_xaxes(title_text="Período", row=row, col=col)
            fig.update_yaxes(title_text=y_title, row=row, col=col)
        
        fig.update_layout(
            height=600,
            title_text="📈 Tendencias Temporales por Variable (Últimos 3 Meses)",
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_period_comparison_chart_streamlit(self, elaboracion, periodos, escenario):
        """Crear gráfico de comparación entre período inicial y final"""
        import plotly.graph_objects as go
        
        if len(periodos) < 2:
            st.info("Se necesitan al menos 2 períodos para la comparación.")
            return
        
        periodo_inicial = periodos[-1]  # El más antiguo
        periodo_final = periodos[0]     # El más reciente
        
        variables = ['Rate All In', 'Originacion Prom', 'Term', 'Risk Rate', 'Fund Rate']
        negocios = ['PYME', 'CORP', 'Brokers', 'WK']
        
        fig = go.Figure()
        
        for negocio in negocios:
            valores_inicial = []
            valores_final = []
            labels = []
            
            for variable in variables:
                # Obtener datos del período inicial
                data_inicial = self.df[
                    (self.df['Elaboracion'] == elaboracion) &
                    (self.df['Escenario'] == escenario) &
                    (self.df['Negocio'] == negocio) &
                    (self.df['Concepto'] == variable) &
                    (self.df['Periodo'] == periodo_inicial)
                ]['Valor'].mean()
                
                # Obtener datos del período final
                data_final = self.df[
                    (self.df['Elaboracion'] == elaboracion) &
                    (self.df['Escenario'] == escenario) &
                    (self.df['Negocio'] == negocio) &
                    (self.df['Concepto'] == variable) &
                    (self.df['Periodo'] == periodo_final)
                ]['Valor'].mean()
                
                if not pd.isna(data_inicial) and not pd.isna(data_final):
                    # Formatear valores según el tipo
                    if variable in ['Rate All In', 'Risk Rate', 'Fund Rate']:
                        valor_inicial = data_inicial * 100
                        valor_final = data_final * 100
                    elif variable == 'Term':
                        valor_inicial = data_inicial
                        valor_final = data_final
                    else:  # Originacion Prom
                        valor_inicial = data_inicial / 1000000
                        valor_final = data_final / 1000000
                    
                    valores_inicial.append(valor_inicial)
                    valores_final.append(valor_final)
                    labels.append(variable)
            
            if valores_inicial and valores_final:
                fig.add_trace(go.Bar(
                    name=f"{negocio} - {periodo_inicial}",
                    x=labels,
                    y=valores_inicial,
                    marker_color='lightblue',
                    opacity=0.7
                ))
                
                fig.add_trace(go.Bar(
                    name=f"{negocio} - {periodo_final}",
                    x=labels,
                    y=valores_final,
                    marker_color='darkblue',
                    opacity=0.9
                ))
        
        fig.update_layout(
            title=f"📊 Comparación {periodo_inicial} vs {periodo_final}",
            xaxis_title="Variables",
            yaxis_title="Valor",
            barmode='group',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_business_evolution_chart_streamlit(self, elaboracion, periodos, escenario):
        """Crear gráfico de evolución por segmento de negocio"""
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        negocios = ['PYME', 'CORP', 'Brokers', 'WK']
        variables = ['Originacion Prom', 'Rate All In']
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=['Originacion Prom (M$)', 'Rate All In (%)'],
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        
        for i, variable in enumerate(variables):
            for j, negocio in enumerate(negocios):
                # Obtener datos para esta variable y negocio
                data = self.df[
                    (self.df['Elaboracion'] == elaboracion) &
                    (self.df['Escenario'] == escenario) &
                    (self.df['Negocio'] == negocio) &
                    (self.df['Concepto'] == variable) &
                    (self.df['Periodo'].isin(periodos))
                ].copy()
                
                if not data.empty:
                    # Agrupar por período y obtener el valor promedio
                    period_data = data.groupby('Periodo')['Valor'].mean().reset_index()
                    period_data = period_data.sort_values('Periodo')
                    
                    # Formatear valores
                    if variable == 'Rate All In':
                        y_values = period_data['Valor'] * 100
                    else:  # Originacion Prom
                        y_values = period_data['Valor'] / 1000000
                    
                    fig.add_trace(
                        go.Scatter(
                            x=period_data['Periodo'],
                            y=y_values,
                            mode='lines+markers',
                            name=f"{negocio}",
                            line=dict(color=colors[j], width=3),
                            marker=dict(size=10)
                        ),
                        row=1, col=i+1
                    )
        
        fig.update_layout(
            height=400,
            title_text="🏢 Evolución por Segmento de Negocio (Últimos 3 Meses)",
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_significant_changes_heatmap_streamlit(self, cambios_significativos):
        """Crear heatmap de cambios significativos"""
        import plotly.graph_objects as go
        
        if not cambios_significativos:
            st.info("No hay cambios significativos para mostrar en el heatmap.")
            return
        
        # Preparar datos para el heatmap
        variables = list(set([c['variable'] for c in cambios_significativos]))
        negocios = list(set([c['negocio'] for c in cambios_significativos]))
        
        # Crear matriz de cambios
        matrix = []
        for variable in variables:
            row = []
            for negocio in negocios:
                # Buscar el cambio para esta combinación
                cambio = next((c for c in cambios_significativos 
                             if c['variable'] == variable and c['negocio'] == negocio), None)
                if cambio:
                    row.append(cambio['magnitud'])
                else:
                    row.append(0)
            matrix.append(row)
        
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=negocios,
            y=variables,
            colorscale='RdBu',
            hoverongaps=False,
            text=[[f"{val:.2f}" for val in row] for row in matrix],
            texttemplate="%{text}",
            textfont={"size": 12}
        ))
        
        fig.update_layout(
            title="🔥 Heatmap de Cambios Significativos",
            xaxis_title="Negocio",
            yaxis_title="Variable",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_top_changes_chart(self, cambios_significativos):
        """Crear gráfico de barras con los cambios más importantes"""
        import plotly.express as px
        import plotly.graph_objects as go
        
        # Preparar datos
        top_changes = sorted(cambios_significativos, key=lambda x: abs(x['magnitud']), reverse=True)[:10]
        
        data = []
        for cambio in top_changes:
            if cambio['tipo'] == 'rate':
                valor = cambio['magnitud']
                unidad = "pp"
            else:
                valor = cambio['magnitud'] / 1000000  # Convertir a millones
                unidad = "M$"
            
            data.append({
                'Variable': cambio['variable'],
                'Negocio': cambio['negocio'],
                'Valor': valor,
                'Tendencia': cambio['tendencia'],
                'Unidad': unidad,
                'Label': f"{cambio['negocio']} - {cambio['variable']}"
            })
        
        if not data:
            return ""
        
        df_viz = pd.DataFrame(data)
        
        # Crear gráfico
        fig = px.bar(
            df_viz, 
            x='Valor', 
            y='Label',
            color='Tendencia',
            color_discrete_map={'creció': '#2E8B57', 'subió': '#2E8B57', 'decreció': '#DC143C', 'bajó': '#DC143C'},
            title="🔝 Top 10 Cambios Más Significativos",
            labels={'Valor': 'Magnitud del Cambio', 'Label': 'Variable - Negocio'}
        )
        
        fig.update_layout(
            height=400,
            showlegend=True,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        # Usar st.plotly_chart en lugar de HTML
        st.plotly_chart(fig, use_container_width=True)
        return "**Gráfico 1: Top Cambios por Magnitud**\n\n"
    
    def _create_top_changes_chart_streamlit(self, cambios_significativos):
        """Crear gráfico de barras con los cambios más importantes para Streamlit"""
        import plotly.express as px
        import plotly.graph_objects as go
        
        # Preparar datos
        top_changes = sorted(cambios_significativos, key=lambda x: abs(x['magnitud']), reverse=True)[:10]
        
        data = []
        for cambio in top_changes:
            if cambio['tipo'] == 'rate':
                valor = cambio['magnitud']
                unidad = "pp"
            else:
                valor = cambio['magnitud'] / 1000000  # Convertir a millones
                unidad = "M$"
            
            data.append({
                'Variable': cambio['variable'],
                'Negocio': cambio['negocio'],
                'Valor': valor,
                'Tendencia': cambio['tendencia'],
                'Unidad': unidad,
                'Label': f"{cambio['negocio']} - {cambio['variable']}"
            })
        
        if not data:
            st.info("No hay datos suficientes para generar el gráfico.")
            return
        
        df_viz = pd.DataFrame(data)
        
        # Crear gráfico
        fig = px.bar(
            df_viz, 
            x='Valor', 
            y='Label',
            color='Tendencia',
            color_discrete_map={'creció': '#2E8B57', 'subió': '#2E8B57', 'decreció': '#DC143C', 'bajó': '#DC143C'},
            title="🔝 Top 10 Cambios Más Significativos",
            labels={'Valor': 'Magnitud del Cambio', 'Label': 'Variable - Negocio'}
        )
        
        fig.update_layout(
            height=400,
            showlegend=True,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_trends_chart_streamlit(self, cambios_significativos, elaboracion, periodos, escenario):
        """Crear gráfico de líneas para tendencias temporales para Streamlit"""
        import plotly.express as px
        import plotly.graph_objects as go
        
        # Agrupar por variable y negocio
        trends_data = {}
        for cambio in cambios_significativos:
            key = f"{cambio['variable']} - {cambio['negocio']}"
            if key not in trends_data:
                trends_data[key] = []
            trends_data[key].append({
                'periodo': cambio['periodo'],
                'valor': cambio['magnitud'],
                'tendencia': cambio['tendencia']
            })
        
        if not trends_data:
            st.info("No hay datos suficientes para generar el gráfico de tendencias.")
            return
        
        # Crear gráfico de líneas
        fig = go.Figure()
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
        
        for i, (key, data) in enumerate(trends_data.items()):
            if len(data) > 1:  # Solo mostrar si hay múltiples puntos
                df_trend = pd.DataFrame(data)
                df_trend = df_trend.sort_values('periodo')
                
                fig.add_trace(go.Scatter(
                    x=df_trend['periodo'],
                    y=df_trend['valor'],
                    mode='lines+markers',
                    name=key,
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=8)
                ))
        
        fig.update_layout(
            title="📈 Tendencias Temporales por Variable y Negocio",
            xaxis_title="Período",
            yaxis_title="Magnitud del Cambio",
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_trends_chart(self, cambios_significativos, elaboracion, periodos, escenario):
        """Crear gráfico de líneas para tendencias temporales"""
        import plotly.express as px
        import plotly.graph_objects as go
        
        # Agrupar por variable y negocio
        trends_data = {}
        for cambio in cambios_significativos:
            key = f"{cambio['variable']} - {cambio['negocio']}"
            if key not in trends_data:
                trends_data[key] = []
            trends_data[key].append({
                'periodo': cambio['periodo'],
                'valor': cambio['magnitud'],
                'tendencia': cambio['tendencia']
            })
        
        if not trends_data:
            return ""
        
        # Crear gráfico de líneas
        fig = go.Figure()
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
        
        for i, (key, data) in enumerate(trends_data.items()):
            if len(data) > 1:  # Solo mostrar si hay múltiples puntos
                df_trend = pd.DataFrame(data)
                df_trend = df_trend.sort_values('periodo')
                
                fig.add_trace(go.Scatter(
                    x=df_trend['periodo'],
                    y=df_trend['valor'],
                    mode='lines+markers',
                    name=key,
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=8)
                ))
        
        fig.update_layout(
            title="📈 Tendencias Temporales por Variable y Negocio",
            xaxis_title="Período",
            yaxis_title="Magnitud del Cambio",
            height=400,
            showlegend=True
        )
        
        # Usar st.plotly_chart en lugar de HTML
        st.plotly_chart(fig, use_container_width=True)
        return "**Gráfico 2: Tendencias Temporales**\n\n"
    
    def _create_segment_distribution_chart(self, cambios_significativos):
        """Crear gráfico de torta para distribución por segmento"""
        import plotly.express as px
        
        # Contar cambios por negocio
        negocio_counts = {}
        for cambio in cambios_significativos:
            negocio = cambio['negocio']
            if negocio not in negocio_counts:
                negocio_counts[negocio] = {'positivos': 0, 'negativos': 0}
            
            if cambio['tendencia'] in ['creció', 'subió']:
                negocio_counts[negocio]['positivos'] += 1
            else:
                negocio_counts[negocio]['negativos'] += 1
        
        if not negocio_counts:
            return ""
        
        # Preparar datos para gráfico de torta
        labels = []
        values = []
        colors = []
        
        for negocio, counts in negocio_counts.items():
            total = counts['positivos'] + counts['negativos']
            if total > 0:
                labels.append(f"{negocio} ({total} cambios)")
                values.append(total)
                # Color basado en la proporción de positivos
                if counts['positivos'] > counts['negativos']:
                    colors.append('#2E8B57')  # Verde
                elif counts['negativos'] > counts['positivos']:
                    colors.append('#DC143C')  # Rojo
                else:
                    colors.append('#FFD700')  # Amarillo
        
        fig = px.pie(
            values=values,
            names=labels,
            title="🥧 Distribución de Cambios por Segmento de Negocio",
            color_discrete_sequence=colors
        )
        
        fig.update_layout(height=400)
        
        # Usar st.plotly_chart en lugar de HTML
        st.plotly_chart(fig, use_container_width=True)
        return "**Gráfico 3: Distribución por Segmento**\n\n"
    
    def _create_segment_distribution_chart_streamlit(self, cambios_significativos):
        """Crear gráfico de torta para distribución por segmento para Streamlit"""
        import plotly.express as px
        
        # Contar cambios por negocio
        negocio_counts = {}
        for cambio in cambios_significativos:
            negocio = cambio['negocio']
            if negocio not in negocio_counts:
                negocio_counts[negocio] = {'positivos': 0, 'negativos': 0}
            
            if cambio['tendencia'] in ['creció', 'subió']:
                negocio_counts[negocio]['positivos'] += 1
            else:
                negocio_counts[negocio]['negativos'] += 1
        
        if not negocio_counts:
            st.info("No hay datos suficientes para generar el gráfico de distribución.")
            return
        
        # Preparar datos para gráfico de torta
        labels = []
        values = []
        colors = []
        
        for negocio, counts in negocio_counts.items():
            total = counts['positivos'] + counts['negativos']
            if total > 0:
                labels.append(f"{negocio} ({total} cambios)")
                values.append(total)
                # Color basado en la proporción de positivos
                if counts['positivos'] > counts['negativos']:
                    colors.append('#2E8B57')  # Verde
                elif counts['negativos'] > counts['positivos']:
                    colors.append('#DC143C')  # Rojo
                else:
                    colors.append('#FFD700')  # Amarillo
        
        fig = px.pie(
            values=values,
            names=labels,
            title="🥧 Distribución de Cambios por Segmento de Negocio",
            color_discrete_sequence=colors
        )
        
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_heatmap_chart(self, cambios_significativos):
        """Crear heatmap de cambios por variable y negocio"""
        import plotly.express as px
        
        # Preparar matriz de datos
        variables = list(set([c['variable'] for c in cambios_significativos]))
        negocios = list(set([c['negocio'] for c in cambios_significativos]))
        
        # Crear matriz de valores
        matrix_data = []
        for variable in variables:
            row = []
            for negocio in negocios:
                # Buscar el cambio para esta combinación
                cambio = next((c for c in cambios_significativos if c['variable'] == variable and c['negocio'] == negocio), None)
                if cambio:
                    row.append(cambio['magnitud'])
                else:
                    row.append(0)
            matrix_data.append(row)
        
        if not matrix_data:
            return ""
        
        # Crear heatmap
        fig = px.imshow(
            matrix_data,
            x=negocios,
            y=variables,
            color_continuous_scale='RdBu',
            title="🔥 Heatmap: Cambios por Variable y Negocio",
            labels=dict(x="Negocio", y="Variable", color="Magnitud del Cambio")
        )
        
        fig.update_layout(height=400)
        
        # Usar st.plotly_chart en lugar de HTML
        st.plotly_chart(fig, use_container_width=True)
        return "**Gráfico 4: Heatmap de Cambios**\n\n"
    
    def _create_heatmap_chart_streamlit(self, cambios_significativos):
        """Crear heatmap de cambios por variable y negocio para Streamlit"""
        import plotly.express as px
        
        # Preparar matriz de datos
        variables = list(set([c['variable'] for c in cambios_significativos]))
        negocios = list(set([c['negocio'] for c in cambios_significativos]))
        
        # Crear matriz de valores
        matrix_data = []
        for variable in variables:
            row = []
            for negocio in negocios:
                # Buscar el cambio para esta combinación
                cambio = next((c for c in cambios_significativos if c['variable'] == variable and c['negocio'] == negocio), None)
                if cambio:
                    row.append(cambio['magnitud'])
                else:
                    row.append(0)
            matrix_data.append(row)
        
        if not matrix_data:
            st.info("No hay datos suficientes para generar el heatmap.")
            return
        
        # Crear heatmap
        fig = px.imshow(
            matrix_data,
            x=negocios,
            y=variables,
            color_continuous_scale='RdBu',
            title="🔥 Heatmap: Cambios por Variable y Negocio",
            labels=dict(x="Negocio", y="Variable", color="Magnitud del Cambio")
        )
        
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, use_container_width=True)
    
    def detect_anomalies(self, elaboracion, periodos, escenario, negocios):
        """Detectar anomalías y outliers en los datos financieros"""
        anomalies = "🚨 **DETECCIÓN DE ANOMALÍAS:**\n\n"
        
        # Variables clave para análisis de anomalías
        variables_clave = ['Rate All In', 'New Active', 'Churn Bruto', 'Resucitados', 'Originacion Prom', 'Term', 'Risk Rate', 'Fund Rate']
        rate_variables = ['Rate All In', 'Risk Rate', 'Fund Rate', 'Term']
        
        anomalies_detected = []
        
        for variable in variables_clave:
            if variable in rate_variables:
                # Análisis de anomalías para rates
                var_anomalies = self._detect_rate_anomalies(variable, elaboracion, periodos, escenario, negocios)
                if var_anomalies:
                    anomalies_detected.extend(var_anomalies)
            else:
                # Análisis de anomalías para variables monetarias
                var_anomalies = self._detect_monetary_anomalies(variable, elaboracion, periodos, escenario, negocios)
                if var_anomalies:
                    anomalies_detected.extend(var_anomalies)
        
        if not anomalies_detected:
            anomalies += "✅ **No se detectaron anomalías significativas** en el período analizado. Los datos muestran un comportamiento normal.\n\n"
            return anomalies
        
        # Ordenar anomalías por severidad
        anomalies_detected.sort(key=lambda x: x['severity_score'], reverse=True)
        
        # Mostrar top anomalías
        anomalies += f"⚠️ **Se detectaron {len(anomalies_detected)} anomalías** que requieren atención:\n\n"
        
        for i, anomaly in enumerate(anomalies_detected[:5]):  # Top 5 anomalías
            severity_emoji = "🔴" if anomaly['severity_score'] > 3 else "🟡" if anomaly['severity_score'] > 2 else "🟠"
            anomalies += f"{i+1}. {severity_emoji} **{anomaly['variable']}** en **{anomaly['negocio']}**\n"
            anomalies += f"   • **Período:** {anomaly['periodo']}\n"
            anomalies += f"   • **Valor:** {anomaly['valor']:.2f}\n"
            anomalies += f"   • **Desviación:** {anomaly['deviation']:.1f} desviaciones estándar\n"
            anomalies += f"   • **Severidad:** {anomaly['severity']}\n"
            anomalies += f"   • **Descripción:** {anomaly['description']}\n\n"
        
        # Recomendaciones para anomalías
        anomalies += "💡 **RECOMENDACIONES:**\n"
        anomalies += "• **Revisar datos de origen** para verificar la precisión de los valores anómalos\n"
        anomalies += "• **Investigar causas raíz** de las desviaciones significativas\n"
        anomalies += "• **Implementar alertas automáticas** para detectar futuras anomalías\n"
        anomalies += "• **Validar procesos de carga** de datos para evitar errores\n\n"
        
        return anomalies
    
    def _detect_rate_anomalies(self, variable, elaboracion, periodos, escenario, negocios):
        """Detectar anomalías en variables de rate"""
        anomalies = []
        
        for negocio in negocios:
            # Obtener valores históricos para calcular estadísticas
            values = []
            for periodo in periodos:
                valor = self._get_rate_value(variable, elaboracion, periodo, escenario, negocio)
                if valor is not None:
                    values.append(valor)
            
            if len(values) < 2:
                continue
            
            # Calcular estadísticas
            mean_val = np.mean(values)
            std_val = np.std(values)
            
            if std_val == 0:
                continue
            
            # Detectar outliers (valores que se desvían más de 2 desviaciones estándar)
            for i, valor in enumerate(values):
                z_score = abs((valor - mean_val) / std_val)
                
                if z_score > 2.0:  # Umbral de anomalía
                    severity_score = min(z_score, 5.0)  # Cap a 5
                    severity = "Alta" if severity_score > 3 else "Media" if severity_score > 2 else "Baja"
                    
                    anomalies.append({
                        'variable': variable,
                        'negocio': negocio,
                        'periodo': periodos[i],
                        'valor': valor,
                        'deviation': z_score,
                        'severity_score': severity_score,
                        'severity': severity,
                        'description': f"Valor {valor:.2f}pp se desvía {z_score:.1f} desviaciones estándar del promedio {mean_val:.2f}pp"
                    })
        
        return anomalies
    
    def _detect_monetary_anomalies(self, variable, elaboracion, periodos, escenario, negocios):
        """Detectar anomalías en variables monetarias"""
        anomalies = []
        
        for negocio in negocios:
            # Obtener valores históricos para calcular estadísticas
            values = []
            for periodo in periodos:
                valor = self._get_monetary_value(variable, elaboracion, periodo, escenario, negocio)
                if valor is not None and valor > 0:
                    values.append(valor)
            
            if len(values) < 2:
                continue
            
            # Calcular estadísticas (usar log para variables monetarias)
            log_values = [np.log(val) for val in values if val > 0]
            
            if len(log_values) < 2:
                continue
                
            mean_log = np.mean(log_values)
            std_log = np.std(log_values)
            
            if std_log == 0:
                continue
            
            # Detectar outliers
            for i, valor in enumerate(values):
                if valor > 0:
                    log_val = np.log(valor)
                    z_score = abs((log_val - mean_log) / std_log)
                    
                    if z_score > 2.0:  # Umbral de anomalía
                        severity_score = min(z_score, 5.0)  # Cap a 5
                        severity = "Alta" if severity_score > 3 else "Media" if severity_score > 2 else "Baja"
                        
                        anomalies.append({
                            'variable': variable,
                            'negocio': negocio,
                            'periodo': periodos[i],
                            'valor': valor,
                            'deviation': z_score,
                            'severity_score': severity_score,
                            'severity': severity,
                            'description': f"Valor ${valor:,.0f} se desvía {z_score:.1f} desviaciones estándar del promedio logarítmico"
                        })
        
        return anomalies
    
    def _analyze_originacion_prom(self, cambios):
        """Análisis experto de Originacion Prom"""
        analysis = ""
        
        cambios_positivos = [c for c in cambios if c['tendencia'] == 'creció']
        cambios_negativos = [c for c in cambios if c['tendencia'] == 'decreció']
        
        if cambios_negativos and not cambios_positivos:
            analysis += "La **Originación Promedio** presenta un **deterioro generalizado** en todos los segmentos analizados. Esta **caída sistemática** en los volúmenes de originación sugiere **desafíos estructurales** en la capacidad de adquisición de nuevos clientes o en la retención de la cartera existente.\n\n"
            
            for cambio in cambios_negativos:
                analysis += f"El segmento **{cambio['negocio']}** registra la mayor **contracción** con una reducción de ${abs(cambio['magnitud']):,.0f} ({abs(cambio['porcentaje']):.1f}%), lo que representa un **riesgo significativo** para la **sostenibilidad del negocio** en este segmento.\n\n"
            
            analysis += "**Implicaciones estratégicas:** Esta **tendencia negativa** requiere una **revisión inmediata** de las estrategias de adquisición, pricing y retención. Se recomienda un **análisis profundo** de la competencia y la propuesta de valor para identificar las **causas raíz** del deterioro.\n\n"
            
        elif cambios_positivos and not cambios_negativos:
            analysis += "La **Originación Promedio** muestra un **crecimiento robusto** en todos los segmentos, indicando una **estrategia de adquisición exitosa** y una **demanda saludable** en el mercado.\n\n"
            
            for cambio in cambios_positivos:
                analysis += f"El segmento **{cambio['negocio']}** destaca con un **crecimiento** de ${cambio['magnitud']:,.0f} ({cambio['porcentaje']:.1f}%), demostrando una **excelente penetración** en este nicho de mercado.\n\n"
            
            analysis += "**Implicaciones estratégicas:** Este **crecimiento sostenido** valida la estrategia actual y sugiere **oportunidades** para expandir la presencia en segmentos de **alto rendimiento**. Se recomienda **capitalizar este momentum** para acelerar el crecimiento.\n\n"
            
        else:
            analysis += "La **Originación Promedio** presenta un **comportamiento mixto** entre segmentos, con algunos mostrando **crecimiento** mientras otros experimentan **contracción**.\n\n"
            
            for cambio in cambios:
                if cambio['tendencia'] == 'creció':
                    analysis += f"**{cambio['negocio']}** registra un **crecimiento positivo** de ${cambio['magnitud']:,.0f} ({cambio['porcentaje']:.1f}%), indicando **fortaleza** en este segmento.\n\n"
                else:
                    analysis += f"**{cambio['negocio']}** experimenta una **contracción** de ${abs(cambio['magnitud']):,.0f} ({abs(cambio['porcentaje']):.1f}%), requiriendo **atención estratégica**.\n\n"
            
            analysis += "**Implicaciones estratégicas:** Esta **divergencia** entre segmentos sugiere la necesidad de **estrategias diferenciadas**. Los segmentos en **crecimiento** deben recibir **mayor inversión**, mientras que los en **contracción** requieren **intervención inmediata**.\n\n"
        
        return analysis
    
    def _analyze_rate_all_in(self, cambios):
        """Análisis experto de Rate All In"""
        analysis = ""
        
        cambios_positivos = [c for c in cambios if c['tendencia'] == 'subió']
        cambios_negativos = [c for c in cambios if c['tendencia'] == 'bajó']
        
        if cambios_positivos and not cambios_negativos:
            analysis += "El **Rate All In** presenta una **tendencia alcista generalizada**, lo que indica una **mejora en la rentabilidad** por producto y una **mayor eficiencia** en la estructura de costos.\n\n"
            
            for cambio in cambios_positivos:
                analysis += f"El segmento **{cambio['negocio']}** muestra la mayor **mejora** con un incremento de {cambio['magnitud']:.2f} puntos porcentuales ({cambio['porcentaje']:.1f}%), reflejando una **optimización exitosa** de la propuesta de valor.\n\n"
            
            analysis += "**Implicaciones estratégicas:** Esta **mejora en rentabilidad** valida las estrategias de **pricing** y **optimización de costos**. Se recomienda **mantener esta tendencia** mientras se evalúan **oportunidades de crecimiento** adicional.\n\n"
            
        elif cambios_negativos and not cambios_positivos:
            analysis += "El **Rate All In** experimenta una **presión a la baja** en todos los segmentos, lo que sugiere **desafíos en la sostenibilidad** de la rentabilidad y posible **erosión de márgenes**.\n\n"
            
            for cambio in cambios_negativos:
                analysis += f"El segmento **{cambio['negocio']}** registra la mayor **contracción** con una reducción de {abs(cambio['magnitud']):.2f} puntos porcentuales ({abs(cambio['porcentaje']):.1f}%), indicando **presión competitiva** significativa.\n\n"
            
            analysis += "**Implicaciones estratégicas:** Esta **tendencia negativa** requiere una **revisión urgente** de la estrategia de **pricing** y la estructura de costos. Se recomienda un **análisis competitivo profundo** y la implementación de **medidas de optimización**.\n\n"
            
        else:
            analysis += "El **Rate All In** presenta un **comportamiento divergente** entre segmentos, con algunos mostrando mejoras mientras otros experimentan deterioro.\n\n"
            
            for cambio in cambios:
                if cambio['tendencia'] == 'subió':
                    analysis += f"**{cambio['negocio']}** registra una mejora de {cambio['magnitud']:.2f}pp ({cambio['porcentaje']:.1f}%), demostrando fortaleza en la gestión de rentabilidad.\n\n"
                else:
                    analysis += f"**{cambio['negocio']}** experimenta una reducción de {abs(cambio['magnitud']):.2f}pp ({abs(cambio['porcentaje']):.1f}%), requiriendo intervención estratégica.\n\n"
            
            analysis += "**Implicaciones estratégicas:** Esta divergencia sugiere la necesidad de estrategias de pricing diferenciadas por segmento. Los segmentos con mejoras deben servir como modelo para los que presentan deterioro.\n\n"
        
        return analysis
    
    def _analyze_term(self, cambios):
        """Análisis experto de Term"""
        analysis = ""
        
        cambios_positivos = [c for c in cambios if c['tendencia'] == 'subió']
        cambios_negativos = [c for c in cambios if c['tendencia'] == 'bajó']
        
        if cambios_positivos and not cambios_negativos:
            analysis += "El **Term** muestra una **tendencia alcista** en todos los segmentos, indicando una mayor duración promedio de los contratos y una mejora en la estabilidad de la cartera.\n\n"
            
            for cambio in cambios_positivos:
                analysis += f"El segmento **{cambio['negocio']}** presenta la mayor mejora con un incremento de {cambio['magnitud']:.2f} puntos porcentuales ({cambio['porcentaje']:.1f}%), reflejando una **mayor lealtad del cliente** y una propuesta de valor más atractiva.\n\n"
            
            analysis += "**Implicaciones estratégicas:** Esta mejora en la duración de contratos sugiere una mayor satisfacción del cliente y una reducción del riesgo de churn. Se recomienda capitalizar esta tendencia para mejorar la predictibilidad de los ingresos.\n\n"
            
        elif cambios_negativos and not cambios_positivos:
            analysis += "El **Term** experimenta una **tendencia a la baja** en todos los segmentos, lo que indica una reducción en la duración promedio de los contratos y posibles desafíos en la retención de clientes.\n\n"
            
            for cambio in cambios_negativos:
                analysis += f"El segmento **{cambio['negocio']}** registra la mayor contracción con una reducción de {abs(cambio['magnitud']):.2f} puntos porcentuales ({abs(cambio['porcentaje']):.1f}%), sugiriendo **desafíos en la retención** y posible erosión de la propuesta de valor.\n\n"
            
            analysis += "**Implicaciones estratégicas:** Esta tendencia negativa requiere una revisión urgente de las estrategias de retención y la propuesta de valor. Se recomienda implementar programas de fidelización y mejorar la experiencia del cliente.\n\n"
            
        else:
            analysis += "El **Term** presenta un **comportamiento mixto** entre segmentos, con algunos mostrando mejoras mientras otros experimentan deterioro.\n\n"
            
            for cambio in cambios:
                if cambio['tendencia'] == 'subió':
                    analysis += f"**{cambio['negocio']}** registra una mejora de {cambio['magnitud']:.2f}pp ({cambio['porcentaje']:.1f}%), indicando fortaleza en la retención de clientes.\n\n"
                else:
                    analysis += f"**{cambio['negocio']}** experimenta una reducción de {abs(cambio['magnitud']):.2f}pp ({abs(cambio['porcentaje']):.1f}%), requiriendo atención estratégica.\n\n"
            
            analysis += "**Implicaciones estratégicas:** Esta divergencia sugiere la necesidad de estrategias de retención diferenciadas por segmento. Los segmentos con mejoras deben servir como modelo para los que presentan deterioro.\n\n"
        
        return analysis
    
    def _analyze_risk_rate(self, cambios):
        """Análisis experto de Risk Rate"""
        analysis = ""
        
        cambios_positivos = [c for c in cambios if c['tendencia'] == 'subió']
        cambios_negativos = [c for c in cambios if c['tendencia'] == 'bajó']
        
        if cambios_positivos and not cambios_negativos:
            analysis += "El **Risk Rate** presenta una **tendencia alcista** en todos los segmentos, lo que indica un aumento en la percepción de riesgo y posibles desafíos en la calidad de la cartera.\n\n"
            
            for cambio in cambios_positivos:
                analysis += f"El segmento **{cambio['negocio']}** muestra la mayor elevación con un incremento de {cambio['magnitud']:.2f} puntos porcentuales ({cambio['porcentaje']:.1f}%), sugiriendo **deterioro en la calidad crediticia** de este segmento.\n\n"
            
            analysis += "**Implicaciones estratégicas:** Esta tendencia alcista requiere una revisión urgente de los criterios de aprobación y las políticas de riesgo. Se recomienda implementar medidas de mitigación y fortalecer los procesos de evaluación crediticia.\n\n"
            
        elif cambios_negativos and not cambios_positivos:
            analysis += "El **Risk Rate** muestra una **tendencia a la baja** en todos los segmentos, indicando una mejora en la calidad de la cartera y una mayor eficiencia en la gestión de riesgo.\n\n"
            
            for cambio in cambios_negativos:
                analysis += f"El segmento **{cambio['negocio']}** presenta la mayor mejora con una reducción de {abs(cambio['magnitud']):.2f} puntos porcentuales ({abs(cambio['porcentaje']):.1f}%), reflejando una **excelente gestión de riesgo** y una cartera de mayor calidad.\n\n"
            
            analysis += "**Implicaciones estratégicas:** Esta mejora en la calidad de riesgo valida las estrategias de evaluación crediticia y gestión de cartera. Se recomienda mantener esta tendencia mientras se evalúan oportunidades de crecimiento con mayor apetito de riesgo.\n\n"
            
        else:
            analysis += "El **Risk Rate** presenta un **comportamiento divergente** entre segmentos, con algunos mostrando mejoras mientras otros experimentan deterioro.\n\n"
            
            for cambio in cambios:
                if cambio['tendencia'] == 'subió':
                    analysis += f"**{cambio['negocio']}** registra un incremento de {cambio['magnitud']:.2f}pp ({cambio['porcentaje']:.1f}%), indicando mayor percepción de riesgo en este segmento.\n\n"
                else:
                    analysis += f"**{cambio['negocio']}** experimenta una reducción de {abs(cambio['magnitud']):.2f}pp ({abs(cambio['porcentaje']):.1f}%), demostrando mejor gestión de riesgo.\n\n"
            
            analysis += "**Implicaciones estratégicas:** Esta divergencia sugiere la necesidad de estrategias de riesgo diferenciadas por segmento. Los segmentos con mejoras deben servir como modelo para los que presentan deterioro.\n\n"
        
        return analysis
    
    def _analyze_fund_rate(self, cambios):
        """Análisis experto de Fund Rate"""
        analysis = ""
        
        cambios_positivos = [c for c in cambios if c['tendencia'] == 'subió']
        cambios_negativos = [c for c in cambios if c['tendencia'] == 'bajó']
        
        if cambios_positivos and not cambios_negativos:
            analysis += "El **Fund Rate** presenta una **tendencia alcista** en todos los segmentos, lo que indica un aumento en los costos de fondeo y posibles presiones en la estructura de financiamiento.\n\n"
            
            for cambio in cambios_positivos:
                analysis += f"El segmento **{cambio['negocio']}** muestra la mayor elevación con un incremento de {cambio['magnitud']:.2f} puntos porcentuales ({cambio['porcentaje']:.1f}%), sugiriendo **mayores costos de financiamiento** para este segmento.\n\n"
            
            analysis += "**Implicaciones estratégicas:** Esta tendencia alcista requiere una revisión de la estrategia de fondeo y la estructura de financiamiento. Se recomienda diversificar las fuentes de financiamiento y optimizar la gestión de liquidez.\n\n"
            
        elif cambios_negativos and not cambios_positivos:
            analysis += "El **Fund Rate** muestra una **tendencia a la baja** en todos los segmentos, indicando una mejora en la eficiencia del fondeo y una optimización de la estructura de financiamiento.\n\n"
            
            for cambio in cambios_negativos:
                analysis += f"El segmento **{cambio['negocio']}** presenta la mayor mejora con una reducción de {abs(cambio['magnitud']):.2f} puntos porcentuales ({abs(cambio['porcentaje']):.1f}%), reflejando una **excelente gestión de fondeo** y menores costos de financiamiento.\n\n"
            
            analysis += "**Implicaciones estratégicas:** Esta mejora en los costos de fondeo valida las estrategias de financiamiento y optimización de liquidez. Se recomienda mantener esta tendencia mientras se evalúan oportunidades de crecimiento.\n\n"
            
        else:
            analysis += "El **Fund Rate** presenta un **comportamiento divergente** entre segmentos, con algunos mostrando mejoras mientras otros experimentan deterioro.\n\n"
            
            for cambio in cambios:
                if cambio['tendencia'] == 'subió':
                    analysis += f"**{cambio['negocio']}** registra un incremento de {cambio['magnitud']:.2f}pp ({cambio['porcentaje']:.1f}%), indicando mayores costos de fondeo en este segmento.\n\n"
                else:
                    analysis += f"**{cambio['negocio']}** experimenta una reducción de {abs(cambio['magnitud']):.2f}pp ({abs(cambio['porcentaje']):.1f}%), demostrando mejor gestión de fondeo.\n\n"
            
            analysis += "**Implicaciones estratégicas:** Esta divergencia sugiere la necesidad de estrategias de fondeo diferenciadas por segmento. Los segmentos con mejoras deben servir como modelo para los que presentan deterioro.\n\n"
        
        return analysis
    
    def _analyze_generic_variable(self, variable, cambios):
        """Análisis genérico para otras variables"""
        analysis = ""
        
        cambios_positivos = [c for c in cambios if c['tendencia'] in ['subió', 'creció']]
        cambios_negativos = [c for c in cambios if c['tendencia'] in ['bajó', 'decreció']]
        
        if cambios_positivos and not cambios_negativos:
            analysis += f"La variable **{variable}** presenta una **tendencia positiva** en todos los segmentos analizados, indicando mejoras significativas en este indicador clave.\n\n"
        elif cambios_negativos and not cambios_positivos:
            analysis += f"La variable **{variable}** experimenta una **tendencia negativa** en todos los segmentos, lo que sugiere desafíos en este indicador crítico.\n\n"
        else:
            analysis += f"La variable **{variable}** presenta un **comportamiento mixto** entre segmentos, con algunos mostrando mejoras mientras otros experimentan deterioro.\n\n"
        
        for cambio in cambios:
            if cambio['tendencia'] in ['subió', 'creció']:
                if cambio['tipo'] == 'rate':
                    analysis += f"El segmento **{cambio['negocio']}** registra una mejora de {cambio['magnitud']:.2f}pp ({cambio['porcentaje']:.1f}%), demostrando fortaleza en este indicador.\n\n"
                else:
                    analysis += f"El segmento **{cambio['negocio']}** presenta un crecimiento de ${cambio['magnitud']:,.0f} ({cambio['porcentaje']:.1f}%), indicando un desempeño sólido.\n\n"
            else:
                if cambio['tipo'] == 'rate':
                    analysis += f"El segmento **{cambio['negocio']}** experimenta una reducción de {abs(cambio['magnitud']):.2f}pp ({abs(cambio['porcentaje']):.1f}%), requiriendo atención estratégica.\n\n"
                else:
                    analysis += f"El segmento **{cambio['negocio']}** registra una contracción de ${abs(cambio['magnitud']):,.0f} ({abs(cambio['porcentaje']):.1f}%), sugiriendo desafíos en este segmento.\n\n"
        
        return analysis
    
    def _analyze_business_segment(self, negocio, cambios):
        """Análisis experto por segmento de negocio"""
        analysis = ""
        
        # Contexto del segmento
        if negocio == 'PYME':
            analysis += "El segmento **PYME** representa el **núcleo del negocio** y su desempeño es crítico para la **sostenibilidad operativa**. "
        elif negocio == 'CORP':
            analysis += "El segmento **CORP** constituye el **motor de crecimiento principal** y su evolución impacta significativamente en los **resultados consolidados**. "
        elif negocio == 'Brokers':
            analysis += "El segmento **Brokers** actúa como un **canal de distribución clave** y su rendimiento refleja la eficiencia de las **estrategias de canal**. "
        elif negocio == 'WK':
            analysis += "El segmento **WK** representa una **oportunidad de crecimiento emergente** y su desarrollo es fundamental para la **diversificación del negocio**. "
        
        # Analizar todos los cambios del segmento
        if cambios:
            # Separar cambios positivos y negativos
            cambios_positivos = [c for c in cambios if c['tendencia'] in ['subió', 'creció']]
            cambios_negativos = [c for c in cambios if c['tendencia'] in ['bajó', 'decreció']]
            
            if cambios_positivos and not cambios_negativos:
                analysis += "Los resultados muestran una **tendencia completamente positiva** con mejoras en múltiples indicadores, sugiriendo una **estrategia exitosa** en este segmento.\n\n"
            elif cambios_negativos and not cambios_positivos:
                analysis += "Los resultados revelan una **tendencia completamente negativa** con deterioro en múltiples indicadores, indicando la necesidad de **intervención estratégica inmediata**.\n\n"
            else:
                analysis += "Los resultados presentan un **comportamiento mixto** con mejoras en algunos indicadores y deterioro en otros, sugiriendo la necesidad de **estrategias diferenciadas**.\n\n"
            
            # Detallar los cambios más importantes
            cambios_ordenados = sorted(cambios, key=lambda x: abs(x['magnitud']), reverse=True)
            for i, cambio in enumerate(cambios_ordenados[:2]):  # Solo los 2 más importantes
                if cambio['tipo'] == 'rate':
                    if cambio['tendencia'] in ['subió', 'creció']:
                        analysis += f"• **{cambio['variable']}** registra una **mejora** de {cambio['magnitud']:.2f}pp ({cambio['porcentaje']:.1f}%), indicando **fortaleza** en este indicador.\n\n"
                    else:
                        analysis += f"• **{cambio['variable']}** experimenta una **reducción** de {abs(cambio['magnitud']):.2f}pp ({abs(cambio['porcentaje']):.1f}%), requiriendo **atención estratégica**.\n\n"
                else:
                    if cambio['tendencia'] in ['subió', 'creció']:
                        analysis += f"• **{cambio['variable']}** presenta un **crecimiento** de ${cambio['magnitud']:,.0f} ({cambio['porcentaje']:.1f}%), demostrando **fortaleza** en este segmento.\n\n"
                    else:
                        analysis += f"• **{cambio['variable']}** registra una **contracción** de ${abs(cambio['magnitud']):,.0f} ({abs(cambio['porcentaje']):.1f}%), sugiriendo **desafíos** en este segmento.\n\n"
            
            # Recomendaciones específicas por negocio
            if negocio == 'PYME':
                if cambios_negativos:
                    analysis += "**Recomendación estratégica:** Dado el carácter crítico del segmento PYME, se recomienda implementar un **plan de acción inmediato** que incluya **revisión de pricing**, **optimización de procesos** y **fortalecimiento de la propuesta de valor**.\n\n"
                else:
                    analysis += "**Recomendación estratégica:** El crecimiento en PYME valida la estrategia actual. Se recomienda **capitalizar este momentum** para **acelerar la expansión** y replicar las mejores prácticas en otros segmentos.\n\n"
            elif negocio == 'CORP':
                if cambios_negativos:
                    analysis += "**Recomendación estratégica:** El deterioro en CORP requiere una **revisión urgente** de la estrategia de crecimiento y la implementación de **medidas de apoyo** para fortalecer la **sostenibilidad del segmento**.\n\n"
                else:
                    analysis += "**Recomendación estratégica:** El crecimiento en CORP presenta una **oportunidad** para acelerar la expansión y replicar las **mejores prácticas** en otros segmentos.\n\n"
            elif negocio == 'Brokers':
                if cambios_negativos:
                    analysis += "**Recomendación estratégica:** El deterioro en Brokers requiere una **revisión de la estrategia de canal** y la implementación de **medidas de apoyo** para fortalecer la **red de distribución**.\n\n"
                else:
                    analysis += "**Recomendación estratégica:** El crecimiento en Brokers valida la estrategia de canal. Se recomienda **expandir la red** y **optimizar los procesos** de distribución.\n\n"
            elif negocio == 'WK':
                if cambios_negativos:
                    analysis += "**Recomendación estratégica:** El deterioro en WK sugiere desafíos en la estrategia de diversificación. Se recomienda **revisar el modelo de negocio** y **ajustar la propuesta de valor**.\n\n"
                else:
                    analysis += "**Recomendación estratégica:** El crecimiento en WK valida la **estrategia de diversificación** y sugiere **oportunidades** para expandir la presencia en este **segmento emergente**.\n\n"
        
        return analysis
    
    def _generate_strategic_recommendations(self, cambios_significativos):
        """Generar recomendaciones estratégicas basadas en los cambios"""
        recommendations = ""
        
        # Analizar patrones generales
        variables_negativas = set()
        variables_positivas = set()
        
        for cambio in cambios_significativos:
            if cambio['tendencia'] in ['bajó', 'decreció']:
                variables_negativas.add(cambio['variable'])
            else:
                variables_positivas.add(cambio['variable'])
        
        # Recomendaciones basadas en patrones
        if 'Originacion Prom' in variables_negativas:
            recommendations += "**1. Estrategia de Adquisición:** La **contracción** en Originación Promedio requiere una **revisión integral** de las estrategias de adquisición. Se recomienda implementar **campañas de marketing dirigidas**, **optimizar los procesos** de onboarding y **fortalecer la propuesta de valor** diferenciada.\n\n"
        
        if 'Rate All In' in variables_negativas:
            recommendations += "**2. Optimización de Rentabilidad:** El **deterioro** en Rate All In sugiere **presiones en la rentabilidad**. Se recomienda **revisar la estructura de costos**, **optimizar los procesos operativos** y evaluar **ajustes en la estrategia de pricing**.\n\n"
        
        if 'Term' in variables_negativas:
            recommendations += "**3. Retención de Clientes:** La **reducción** en Term indica **desafíos en la retención**. Se recomienda implementar **programas de fidelización**, **mejorar la experiencia del cliente** y desarrollar estrategias de **upselling y cross-selling**.\n\n"
        
        if 'Risk Rate' in variables_positivas:
            recommendations += "**4. Gestión de Riesgo:** La **mejora** en Risk Rate valida las estrategias de **evaluación crediticia**. Se recomienda **mantener esta tendencia** mientras se evalúan **oportunidades de crecimiento** con mayor **apetito de riesgo controlado**.\n\n"
        
        if 'Fund Rate' in variables_positivas:
            recommendations += "**5. Optimización de Fondeo:** La **mejora** en Fund Rate indica una **gestión eficiente** del financiamiento. Se recomienda **capitalizar esta ventaja competitiva** para impulsar el **crecimiento sostenible**.\n\n"
        
        # Recomendaciones generales
        if len(variables_negativas) > len(variables_positivas):
            recommendations += "**6. Plan de Recuperación:** Dado el **predominio de tendencias negativas**, se recomienda implementar un **plan de recuperación integral** que incluya **revisión de estrategias**, **optimización de procesos** y **fortalecimiento de capacidades operativas**.\n\n"
        elif len(variables_positivas) > len(variables_negativas):
            recommendations += "**6. Aceleración del Crecimiento:** El **predominio de tendencias positivas** presenta una **oportunidad** para acelerar el crecimiento. Se recomienda **capitalizar este momentum** para expandir la presencia en segmentos de **alto rendimiento**.\n\n"
        else:
            recommendations += "**6. Estrategia Diferenciada:** La **naturaleza mixta** de los resultados sugiere la necesidad de **estrategias diferenciadas** por segmento. Se recomienda desarrollar **planes de acción específicos** para cada área de negocio.\n\n"
        
        recommendations += "**7. Monitoreo Continuo:** Se recomienda implementar un **sistema de monitoreo en tiempo real** para detectar **cambios tempranos** en los indicadores clave y permitir una **respuesta ágil** a las condiciones del mercado.\n\n"
        
        return recommendations
    
    def _get_significant_rate_changes(self, variable, elaboracion, periodos, escenario, negocios):
        """Obtener cambios significativos en rates (>0.1pp)"""
        cambios = []
        
        for negocio in negocios:
            # Solo comparar el último período con el primero (tendencia general)
            if len(periodos) >= 2:
                periodo_actual = periodos[0]  # Primer período (más reciente)
                periodo_anterior = periodos[-1]  # Último período (más antiguo)
                
                # Obtener valores
                valor_actual = self._get_rate_value(variable, elaboracion, periodo_actual, escenario, negocio)
                valor_anterior = self._get_rate_value(variable, elaboracion, periodo_anterior, escenario, negocio)
                
                if valor_actual is not None and valor_anterior is not None:
                    cambio = valor_actual - valor_anterior
                    porcentaje = (cambio / valor_anterior * 100) if valor_anterior != 0 else 0
                    
                    if abs(cambio) > 0.1:  # Cambio significativo
                        cambios.append({
                            'variable': variable,
                            'negocio': negocio,
                            'periodo': periodo_actual,
                            'periodo_anterior': periodo_anterior,
                            'magnitud': cambio,
                            'porcentaje': porcentaje,
                            'tendencia': 'subió' if cambio > 0 else 'bajó',
                            'emoji': '📈' if cambio > 0 else '📉',
                            'tipo': 'rate'
                        })
        
        return cambios
    
    def _get_significant_monetary_changes(self, variable, elaboracion, periodos, escenario, negocios):
        """Obtener cambios significativos en variables monetarias (>3%)"""
        cambios = []
        
        for negocio in negocios:
            # Solo comparar el último período con el primero (tendencia general)
            if len(periodos) >= 2:
                periodo_actual = periodos[0]  # Primer período (más reciente)
                periodo_anterior = periodos[-1]  # Último período (más antiguo)
                
                # Obtener valores
                valor_actual = self._get_monetary_value(variable, elaboracion, periodo_actual, escenario, negocio)
                valor_anterior = self._get_monetary_value(variable, elaboracion, periodo_anterior, escenario, negocio)
                
                if valor_actual is not None and valor_anterior is not None:
                    cambio = valor_actual - valor_anterior
                    porcentaje = (cambio / valor_anterior * 100) if valor_anterior != 0 else 0
                    
                    if abs(porcentaje) > 3:  # Cambio significativo
                        cambios.append({
                            'variable': variable,
                            'negocio': negocio,
                            'periodo': periodo_actual,
                            'periodo_anterior': periodo_anterior,
                            'magnitud': cambio,
                            'porcentaje': porcentaje,
                            'tendencia': 'creció' if cambio > 0 else 'decreció',
                            'emoji': '📈' if cambio > 0 else '📉',
                            'tipo': 'monetary'
                        })
        
        return cambios
    
    def _get_rate_value(self, variable, elaboracion, periodo, escenario, negocio):
        """Obtener valor de rate para un negocio específico"""
        filtro = (
            (self.df['Elaboracion'] == elaboracion) & 
            (self.df['Periodo'] == periodo) & 
            (self.df['Concepto'] == variable) &
            (self.df['Negocio'] == negocio)
        )
        
        if escenario:
            filtro = filtro & (self.df['Escenario'] == escenario)
        
        data = self.df[filtro]
        if len(data) > 0:
            # Para rates, agrupar por cohort y tomar el primer valor de cada cohort único
            grouped = data.groupby('Cohort_Act')['Valor'].first()
            return grouped.mean()
        return None
    
    def _get_monetary_value(self, variable, elaboracion, periodo, escenario, negocio):
        """Obtener valor monetario para un negocio específico"""
        filtro = (
            (self.df['Elaboracion'] == elaboracion) & 
            (self.df['Periodo'] == periodo) & 
            (self.df['Concepto'] == variable) &
            (self.df['Negocio'] == negocio)
        )
        
        if escenario:
            filtro = filtro & (self.df['Escenario'] == escenario)
        
        data = self.df[filtro]
        if len(data) > 0:
            return data['Valor'].sum()
        return None
    
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
            # Verificar si es una consulta específica de una sola variable (PRIORIDAD MÁS ALTA)
            if self.is_single_variable_query(user_message):
                single_analysis = self.analyze_single_variable(user_message)
                if single_analysis:
                    return single_analysis
            
            # Verificar si es una consulta de comparación rolling específica (PRIORIDAD ALTA)
            if 'comparame' in user_message.lower() and 'periodos' in user_message.lower() and 'elaboracion' in user_message.lower():
                rolling_analysis = self.analyze_rolling_comparison(user_message)
                if rolling_analysis:
                    return rolling_analysis
            
            # Verificar si es una consulta "como me fue" con comparación rolling (PRIORIDAD ALTA)
            if ('como me fue' in user_message.lower() or 'como nos fue' in user_message.lower()) and 'comparando' in user_message.lower():
                rolling_analysis = self.analyze_rolling_comparison(user_message)
                if rolling_analysis:
                    return rolling_analysis
            
            # Verificar si es una consulta de "últimos N meses" (PRIORIDAD MEDIA)
            if ('ultimos' in user_message.lower() or 'ultimo' in user_message.lower()) and 'meses' in user_message.lower():
                months_analysis = self.analyze_last_months_performance(user_message)
                if months_analysis:
                    return months_analysis
            
            # Verificar si es una consulta de "como nos fue" (comparación simple) - PRIORIDAD BAJA
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
        
        st.header("📈 Dashboard Rápido")
        if st.button("🔍 Análisis Completo de Últimos 3 Meses"):
            st.session_state.messages.append({"role": "user", "content": "¿Cómo me fue en los últimos 3 meses de elaboración 08-01-2025?"})
            st.rerun()
        if st.button("🚨 Detectar Anomalías"):
            st.session_state.messages.append({"role": "user", "content": "Detecta anomalías en los últimos 3 meses de elaboración 08-01-2025"})
            st.rerun()
        if st.button("📊 Visualizar Tendencias"):
            st.session_state.messages.append({"role": "user", "content": "Muestra las tendencias de Rate All In en los últimos 3 meses"})
            st.rerun()
    
    # Chat interface
    st.header("💬 Chat")
    
    # Mostrar mensajes anteriores
    for message in st.session_state.messages:
        with st.container():
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message">👤 **Tú:** {message["content"]}</div>', unsafe_allow_html=True)
            else:
                # Verificar si es un mensaje con gráficos
                if message["content"] == "CHARTS_ROLLING" and "chart_params" in message:
                    params = message["chart_params"]
                    st.markdown("---")
                    st.markdown("## 📊 **VISUALIZACIONES INTERACTIVAS**")
                    
                    # 1. Gráfico de comparación
                    st.markdown("### 📈 **Gráfico 1: Comparación Predicción vs Realidad por Variable**")
                    chatbot._create_rolling_comparison_chart(
                        params['elaboracion_prediccion'], 
                        params['elaboracion_realidad'], 
                        params['periodo'], 
                        params['separar_por_negocio'], 
                        params['negocios']
                    )
                    
                    # 2. Gráfico de precisión
                    st.markdown("### 🎯 **Gráfico 2: Precisión Predictiva por Segmento**")
                    chatbot._create_rolling_accuracy_chart(
                        params['elaboracion_prediccion'], 
                        params['elaboracion_realidad'], 
                        params['periodo'], 
                        params['separar_por_negocio'], 
                        params['negocios']
                    )
                    
                    # 3. Heatmap
                    st.markdown("### 🔥 **Gráfico 3: Heatmap de Desviaciones por Cohort**")
                    chatbot._create_rolling_heatmap_chart(
                        params['elaboracion_prediccion'], 
                        params['elaboracion_realidad'], 
                        params['periodo'], 
                        params['separar_por_negocio'], 
                        params['negocios']
                    )
                    
                    # 4. Gráfico de tendencias (solo si separar por negocio)
                    if params['separar_por_negocio']:
                        st.markdown("### 📊 **Gráfico 4: Tendencias por Segmento de Negocio**")
                        chatbot._create_rolling_trends_chart(
                            params['elaboracion_prediccion'], 
                            params['elaboracion_realidad'], 
                            params['periodo'], 
                            params['negocios']
                        )
                elif message["content"] == "CHARTS_LAST_MONTHS" and "chart_params" in message:
                    params = message["chart_params"]
                    st.markdown("---")
                    st.markdown("## 📊 **VISUALIZACIONES INTERACTIVAS**")
                    
                    # Regenerar cambios significativos para los gráficos
                    cambios_significativos = chatbot._get_significant_changes_for_charts(
                        params['elaboracion'],
                        params['periodos'],
                        params['escenario'],
                        params['negocios']
                    )
                    
                    # Generar gráficos de últimos meses
                    chatbot.generate_visualizations_streamlit(
                        cambios_significativos,
                        params['elaboracion'],
                        params['periodos'],
                        params['escenario']
                    )
                else:
                    # Renderizar markdown correctamente
                    st.markdown("🤖 **Bot:**")
                    # Procesar el contenido para convertir **texto** a markdown
                    content = message["content"]
                    st.markdown(content)
    
    # Input de usuario
    user_input = st.text_input("Escribe tu consulta:", key="user_input")
    
    if st.button("Enviar") and user_input:
        # Agregar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Obtener respuesta
        with st.spinner("Procesando..."):
            response = chatbot.get_chat_response(user_input)
        
        # Detectar si se deben generar gráficos
        if "**GENERATE_ROLLING_CHARTS:**" in response:
            # Extraer parámetros para rolling charts
            lines = response.split('\n')
            params = {}
            for line in lines:
                if '=' in line and not line.startswith('**'):
                    key, value = line.split('=', 1)
                    if key == 'negocios':
                        # Convertir string de lista a lista real
                        value = value.strip("[]").replace("'", "").split(', ')
                        value = [v.strip() for v in value if v.strip()]
                    elif value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    params[key] = value
            
            # Generar gráficos y agregar al mensaje
            if all(k in params for k in ['elaboracion_prediccion', 'elaboracion_realidad', 'periodo', 'separar_por_negocio', 'negocios']):
                # Limpiar el marcador de la respuesta
                clean_response = response.split("**GENERATE_ROLLING_CHARTS:**")[0].strip()
                
                # Agregar mensaje limpio
                st.session_state.messages.append({"role": "assistant", "content": clean_response})
                
                # Agregar gráficos como mensaje especial
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "CHARTS_ROLLING",
                    "chart_params": params
                })
            else:
                st.session_state.messages.append({"role": "assistant", "content": response})
        elif "**GENERATE_LAST_MONTHS_CHARTS:**" in response:
            # Extraer parámetros para last months charts
            lines = response.split('\n')
            params = {}
            for line in lines:
                if '=' in line and not line.startswith('**'):
                    key, value = line.split('=', 1)
                    if key in ['periodos', 'negocios']:
                        # Convertir string de lista a lista real
                        value = value.strip("[]").replace("'", "").split(', ')
                        value = [v.strip() for v in value if v.strip()]
                    elif value.lower() == 'true':
                        value = True
                    elif value.lower() == 'false':
                        value = False
                    elif value == 'None':
                        value = None
                    else:
                        params[key] = value
            
            # Generar gráficos y agregar al mensaje
            if all(k in params for k in ['elaboracion', 'periodos', 'escenario', 'negocios']):
                # Limpiar el marcador de la respuesta
                clean_response = response.split("**GENERATE_LAST_MONTHS_CHARTS:**")[0].strip()
                
                # Agregar mensaje limpio
                st.session_state.messages.append({"role": "assistant", "content": clean_response})
                
                # Agregar gráficos como mensaje especial
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "CHARTS_LAST_MONTHS",
                    "chart_params": params
                })
            else:
                st.session_state.messages.append({"role": "assistant", "content": response})
        else:
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
