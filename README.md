# 🤖 Chatbot Financiero Inteligente

## 📋 Descripción

Chatbot financiero avanzado con análisis de datos, visualizaciones interactivas y detección de anomalías. Desarrollado con Streamlit y optimizado para deployment en la nube.

## ✨ Características Principales

### 🧠 **Análisis Inteligente**
- **Análisis de Últimos N Meses:** Comparación temporal de indicadores clave
- **Predicción vs Realidad:** Comparación de elaboraciones con períodos
- **Análisis por Segmento:** PYME, CORP, Brokers, WK
- **Filtrado Inteligente:** Detección automática de filtros en consultas naturales

### 📊 **Visualizaciones Interactivas**
- **Gráficos de Barras:** Top 10 cambios más significativos
- **Gráficos de Líneas:** Tendencias temporales por variable y negocio
- **Gráficos de Torta:** Distribución de cambios por segmento
- **Heatmap:** Matriz de cambios por variable y negocio

### 🚨 **Detección de Anomalías**
- **Análisis Estadístico:** Detección de outliers usando Z-score
- **Scoring de Severidad:** Alta/Media/Baja basado en desviaciones
- **Recomendaciones:** Acciones específicas para cada anomalía
- **Alertas Automáticas:** Identificación de valores anómalos

### 💬 **Chat Inteligente**
- **Persona Dual:** Serio para finanzas, amigable para consultas generales
- **Análisis Automático:** Storytelling experto con términos en negrita
- **Filtrado de Cambios:** Solo muestra diferencias significativas (>3% monetario, >0.1pp rates)
- **Análisis Comparativo:** Enfoque en diferencias entre períodos

## 🚀 Instalación y Uso

### **Requisitos**
```bash
pip install streamlit pandas plotly openai python-dotenv numpy
```

### **Configuración**
1. Crear archivo `.env` con tu API key de OpenAI:
```env
OPENAI_API_KEY=tu-api-key-aqui
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.5
OPENAI_MAX_TOKENS=1000
```

2. Colocar tu archivo CSV en la carpeta `dataset/`

### **Ejecución**
```bash
streamlit run app.py
```

## 📊 Variables Analizadas

### **Variables Monetarias**
- **Originacion Prom:** Promedio de originación por cliente
- **New Active:** Nuevos clientes activos
- **Churn Bruto:** Clientes que abandonaron el servicio
- **Resucitados:** Clientes que regresaron al servicio

### **Variables de Rate**
- **Rate All In:** Tasa total del producto
- **Risk Rate:** Tasa de riesgo
- **Fund Rate:** Tasa de fondeo
- **Term:** Plazo promedio

## 🔍 Tipos de Consultas Soportadas

### **Análisis Temporal**
- "¿Cómo me fue en los últimos 3 meses de elaboración 08-01-2025?"
- "¿Cuál fue el Resultado Comercial de la elaboración 07-01-2025?"

### **Comparaciones**
- "¿Cómo me fue en la elaboración 08-01-2025 vs 07-01-2025?"
- "Compara PYME vs CORP en Rate All In"

### **Análisis por Segmento**
- "¿Cuál fue la Originación Promedio en PYME para el período 06-01-2025?"
- "Muestra el Churn Bruto por negocio"

### **Detección de Anomalías**
- "Detecta anomalías en los últimos 3 meses"
- "¿Hay valores anómalos en Risk Rate?"

### **Consultas Generales**
- "¿Qué día es hoy?"
- "¿Cuál es la temperatura en Santiago?"

## 📈 Dashboard Rápido

El sidebar incluye botones de acceso rápido para:
- **🔍 Análisis Completo:** Últimos 3 meses con visualizaciones
- **🚨 Detectar Anomalías:** Identificación automática de outliers
- **📊 Visualizar Tendencias:** Gráficos interactivos

## 🎯 Filtros Automáticos

El chatbot detecta automáticamente:
- **Elaboración:** Fechas de elaboración (ej: "08-01-2025")
- **Período:** Fechas de período (ej: "06-01-2025")
- **Escenario:** Moderado/Ambición
- **Negocio:** PYME/CORP/Brokers/WK
- **País:** CL/CO/MX/PE
- **Cohorte:** <2024/2024/2025

## 📊 Visualizaciones

### **Gráfico 1: Top Cambios por Magnitud**
- Barras horizontales con los 10 cambios más significativos
- Color-coded: Verde para positivos, rojo para negativos
- Valores en millones para variables monetarias

### **Gráfico 2: Tendencias Temporales**
- Líneas de tendencia por variable y negocio
- Múltiples colores para diferenciar series
- Solo muestra series con múltiples puntos

### **Gráfico 3: Distribución por Segmento**
- Torta con distribución de cambios por negocio
- Colores basados en proporción de positivos/negativos
- Incluye conteo de cambios por segmento

### **Gráfico 4: Heatmap de Cambios**
- Matriz de variables vs negocios
- Escala de colores RdBu (rojo-azul)
- Valores de magnitud de cambio

## 🚨 Detección de Anomalías

### **Método Estadístico**
- **Z-score > 2.0:** Umbral de anomalía
- **Análisis Logarítmico:** Para variables monetarias
- **Análisis Directo:** Para variables de rate

### **Niveles de Severidad**
- **🔴 Alta:** >3 desviaciones estándar
- **🟡 Media:** 2-3 desviaciones estándar
- **🟠 Baja:** 2-2.5 desviaciones estándar

### **Recomendaciones Automáticas**
- Revisar datos de origen
- Investigar causas raíz
- Implementar alertas automáticas
- Validar procesos de carga

## 🎨 Storytelling Experto

### **Análisis por Variable**
- **Originacion Prom:** Análisis de capacidad de adquisición
- **Rate All In:** Análisis de competitividad y pricing
- **Term:** Análisis de preferencias de plazo
- **Risk Rate:** Análisis de gestión de riesgo
- **Fund Rate:** Análisis de costos de fondeo

### **Análisis por Segmento**
- **PYME:** Núcleo del negocio, sostenibilidad operativa
- **CORP:** Motor de crecimiento, resultados consolidados
- **Brokers:** Canal de distribución, eficiencia de canal
- **WK:** Oportunidad de crecimiento, diversificación

### **Recomendaciones Estratégicas**
- Diferenciadas por segmento de negocio
- Basadas en tendencias y cambios significativos
- Enfoque en acciones específicas y medibles

## 🔧 Arquitectura Técnica

### **Frontend**
- **Streamlit:** Interfaz web interactiva
- **Plotly:** Visualizaciones interactivas
- **CSS Personalizado:** Estilos para mejor UX

### **Backend**
- **Pandas:** Manipulación de datos
- **NumPy:** Cálculos estadísticos
- **OpenAI API:** Generación de respuestas inteligentes

### **Análisis de Datos**
- **Regex:** Extracción de filtros de consultas naturales
- **Estadística:** Z-score, desviaciones estándar
- **Agregaciones:** Groupby, sumas, promedios

## 📁 Estructura del Proyecto

```
finance-agent/
├── app.py                 # Aplicación principal Streamlit
├── config.env            # Configuración de OpenAI
├── requirements.txt      # Dependencias Python
├── README.md            # Documentación
└── dataset/
    └── Prueba-Chatbot - BBDD.csv  # Datos financieros
```

## 🚀 Deployment

### **Streamlit Cloud**
1. Subir código a GitHub
2. Conectar con Streamlit Cloud
3. Configurar variables de entorno
4. Deploy automático

### **Variables de Entorno**
- `OPENAI_API_KEY`: Tu API key de OpenAI
- `OPENAI_MODEL`: Modelo a usar (gpt-3.5-turbo)
- `OPENAI_TEMPERATURE`: Creatividad (0.5)
- `OPENAI_MAX_TOKENS`: Máximo de tokens (1000)

## 🤝 Contribuciones

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o preguntas:
- Crear un issue en GitHub
- Contactar al equipo de desarrollo

---

**Desarrollado con ❤️ para análisis financiero inteligente**