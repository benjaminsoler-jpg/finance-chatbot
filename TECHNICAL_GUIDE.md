# 🔧 Guía Técnica - Chatbot Financiero

## 📋 Arquitectura del Sistema

### **Componentes Principales**

1. **FinancialChatbot Class**
   - `load_data()`: Carga y procesamiento de CSV
   - `get_chat_response()`: Orquestador principal de respuestas
   - `analyze_last_months_performance()`: Análisis de últimos N meses
   - `analyze_performance_comparison()`: Comparación predicción vs realidad

2. **Módulo de Análisis**
   - `_get_significant_rate_changes()`: Cambios significativos en rates
   - `_get_significant_monetary_changes()`: Cambios significativos monetarios
   - `_generate_storytelling()`: Análisis narrativo experto

3. **Módulo de Visualizaciones**
   - `generate_visualizations()`: Orquestador de gráficos
   - `_create_top_changes_chart()`: Gráfico de barras
   - `_create_trends_chart()`: Gráfico de líneas
   - `_create_segment_distribution_chart()`: Gráfico de torta
   - `_create_heatmap_chart()`: Heatmap

4. **Módulo de Detección de Anomalías**
   - `detect_anomalies()`: Orquestador de detección
   - `_detect_rate_anomalies()`: Anomalías en rates
   - `_detect_monetary_anomalies()`: Anomalías monetarias

## 🔍 Flujo de Procesamiento

### **1. Carga de Datos**
```python
def load_data(self):
    # Cargar CSV
    # Limpiar columnas
    # Convertir tipos de datos
    # Validar estructura
```

### **2. Procesamiento de Consultas**
```python
def get_chat_response(self, user_message):
    # Detectar tipo de consulta
    # Aplicar filtros automáticos
    # Ejecutar análisis específico
    # Generar respuesta
```

### **3. Análisis de Datos**
```python
def analyze_last_months_performance(self, query):
    # Extraer filtros de la consulta
    # Obtener datos filtrados
    # Calcular cambios significativos
    # Generar visualizaciones
    # Detectar anomalías
    # Crear storytelling
```

## 📊 Estructura de Datos

### **DataFrame Principal**
```python
columns = [
    'Elaboracion', 'Periodo', 'Pais', 'Negocio', 'Concepto',
    'Clasificacion', 'Cohort_Act', 'Escenario', 'Valor'
]
```

### **Filtros Automáticos**
```python
filters = {
    'elaboracion': '08-01-2025',
    'periodo': ['06-01-2025', '05-01-2025', '04-01-2025'],
    'escenario': 'Moderado',
    'negocios': ['PYME', 'CORP', 'Brokers', 'WK']
}
```

### **Cambios Significativos**
```python
cambio = {
    'variable': 'Rate All In',
    'negocio': 'PYME',
    'periodo': '06-01-2025',
    'valor_anterior': 0.0174,
    'valor_actual': 0.0189,
    'magnitud': 0.0015,
    'porcentaje': 8.6,
    'tendencia': 'subió',
    'tipo': 'rate'
}
```

## 🎯 Algoritmos de Análisis

### **Detección de Cambios Significativos**

#### **Para Rates (>0.1pp)**
```python
def _get_significant_rate_changes(self, variable, elaboracion, periodos, escenario, negocios):
    # Obtener valores por período
    # Calcular diferencia entre último y primer período
    # Aplicar umbral de 0.1pp
    # Retornar cambios significativos
```

#### **Para Variables Monetarias (>3%)**
```python
def _get_significant_monetary_changes(self, variable, elaboracion, periodos, escenario, negocios):
    # Obtener valores por período
    # Calcular diferencia entre último y primer período
    # Aplicar umbral de 3%
    # Retornar cambios significativos
```

### **Detección de Anomalías**

#### **Z-Score para Rates**
```python
def _detect_rate_anomalies(self, variable, elaboracion, periodos, escenario, negocios):
    # Calcular media y desviación estándar
    # Aplicar Z-score = |valor - media| / desviación
    # Umbral: Z-score > 2.0
    # Scoring: Alta (>3), Media (2-3), Baja (2-2.5)
```

#### **Z-Score Logarítmico para Monetarias**
```python
def _detect_monetary_anomalies(self, variable, elaboracion, periodos, escenario, negocios):
    # Aplicar logaritmo a valores
    # Calcular media y desviación estándar logarítmicas
    # Aplicar Z-score en escala logarítmica
    # Umbral: Z-score > 2.0
```

## 📈 Visualizaciones

### **Gráfico de Barras - Top Cambios**
```python
def _create_top_changes_chart(self, cambios_significativos):
    # Ordenar por magnitud absoluta
    # Tomar top 10
    # Crear gráfico horizontal
    # Color-coded por tendencia
```

### **Gráfico de Líneas - Tendencias**
```python
def _create_trends_chart(self, cambios_significativos, elaboracion, periodos, escenario):
    # Agrupar por variable y negocio
    # Crear series temporales
    # Aplicar colores únicos
    # Solo mostrar series con múltiples puntos
```

### **Gráfico de Torta - Distribución**
```python
def _create_segment_distribution_chart(self, cambios_significativos):
    # Contar cambios por negocio
    # Separar positivos y negativos
    # Aplicar colores basados en proporción
    # Incluir conteo en etiquetas
```

### **Heatmap - Matriz de Cambios**
```python
def _create_heatmap_chart(self, cambios_significativos):
    # Crear matriz variables x negocios
    # Llenar con valores de magnitud
    # Aplicar escala de colores RdBu
    # Mostrar valores en celdas
```

## 🎨 Storytelling

### **Análisis por Variable**
```python
def _analyze_originacion_prom(self, cambios):
    # Separar cambios positivos y negativos
    # Analizar tendencias generales
    # Proporcionar contexto estratégico
    # Generar recomendaciones específicas
```

### **Análisis por Segmento**
```python
def _analyze_business_segment(self, negocio, cambios):
    # Contexto específico del segmento
    # Análisis de tendencias (positiva/negativa/mixta)
    # Detalle de cambios más importantes
    # Recomendaciones diferenciadas
```

## 🔧 Configuración y Personalización

### **Umbrales de Cambios Significativos**
```python
# Rates
RATE_THRESHOLD = 0.1  # puntos porcentuales

# Variables Monetarias
MONETARY_THRESHOLD = 3.0  # porcentaje
```

### **Umbrales de Anomalías**
```python
# Z-score
ANOMALY_THRESHOLD = 2.0

# Severidad
HIGH_SEVERITY = 3.0
MEDIUM_SEVERITY = 2.0
```

### **Variables Clave**
```python
VARIABLES_CLAVE = [
    'Rate All In', 'New Active', 'Churn Bruto', 'Resucitados',
    'Originacion Prom', 'Term', 'Risk Rate', 'Fund Rate'
]

RATE_VARIABLES = ['Rate All In', 'Risk Rate', 'Fund Rate', 'Term']
```

## 🚀 Optimizaciones

### **Caching de Datos**
```python
@st.cache_data
def load_data():
    # Cargar y procesar datos una sola vez
    # Reutilizar en consultas posteriores
```

### **Procesamiento Paralelo**
```python
# Análisis por variable en paralelo
# Cálculos de anomalías independientes
# Generación de visualizaciones concurrente
```

### **Lazy Loading**
```python
# Cargar visualizaciones solo cuando se necesiten
# Generar gráficos bajo demanda
# Optimizar memoria y rendimiento
```

## 🧪 Testing

### **Tests Unitarios**
```python
def test_load_data():
    # Verificar carga correcta de CSV
    # Validar tipos de datos
    # Comprobar estructura

def test_detect_anomalies():
    # Verificar detección de outliers
    # Validar scoring de severidad
    # Comprobar recomendaciones
```

### **Tests de Integración**
```python
def test_full_analysis():
    # Probar flujo completo
    # Verificar generación de visualizaciones
    # Validar storytelling
```

## 📊 Métricas de Rendimiento

### **Tiempo de Respuesta**
- Carga de datos: <2 segundos
- Análisis básico: <5 segundos
- Visualizaciones: <3 segundos
- Detección de anomalías: <2 segundos

### **Uso de Memoria**
- DataFrame: ~50MB para 50K registros
- Visualizaciones: ~10MB por gráfico
- Cache: ~100MB total

## 🔒 Seguridad

### **Validación de Entrada**
```python
def validate_query(query):
    # Sanitizar entrada del usuario
    # Validar formato de fechas
    # Verificar rangos de valores
```

### **Manejo de Errores**
```python
try:
    # Procesamiento principal
except Exception as e:
    # Log del error
    # Respuesta de fallback
    # Notificación al usuario
```

## 📈 Escalabilidad

### **Horizontal**
- Múltiples instancias de Streamlit
- Load balancer para distribución
- Cache compartido (Redis)

### **Vertical**
- Optimización de consultas SQL
- Indexación de datos
- Compresión de visualizaciones

---

**Esta guía técnica proporciona una visión completa de la arquitectura y funcionamiento interno del chatbot financiero.**
