# 🤖 Chatbot Financiero - Deployment Online

## 🚀 **DEPLOYMENT RÁPIDO (5 minutos)**

### **Opción 1: Streamlit Cloud (Recomendado)**
```bash
# 1. Subir a GitHub
git add .
git commit -m "Deploy chatbot"
git push

# 2. Ir a share.streamlit.io
# 3. Conectar GitHub
# 4. Seleccionar repositorio
# 5. Deploy!
```

### **Opción 2: Gradio Spaces**
```bash
# 1. Crear Space en huggingface.co/spaces
# 2. Subir archivos
# 3. Configurar OPENAI_API_KEY
# 4. Deploy automático!
```

### **Opción 3: Replit**
```bash
# 1. Crear Repl en replit.com
# 2. Subir archivos
# 3. Ejecutar: python replit_config.py
# 4. Ejecutar: streamlit run app.py
```

---

## 📁 **ARCHIVOS NECESARIOS**

### **Para Streamlit:**
- `app.py` - Aplicación principal
- `requirements_streamlit.txt` - Dependencias
- `dataset/Prueba-Chatbot - BBDD.csv` - Datos
- `.streamlit/secrets.toml` - Variables de entorno

### **Para Gradio:**
- `gradio_app.py` - Aplicación principal
- `requirements.txt` - Dependencias
- `dataset/Prueba-Chatbot - BBDD.csv` - Datos

### **Para Replit:**
- `app.py` o `gradio_app.py` - Aplicación
- `requirements.txt` - Dependencias
- `replit_config.py` - Configuración
- `dataset/Prueba-Chatbot - BBDD.csv` - Datos

---

## 🔧 **CONFIGURACIÓN**

### **Variables de entorno necesarias:**
```
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.5
```

### **Dependencias principales:**
```
streamlit>=1.28.0
pandas>=1.5.0
openai>=1.3.0
plotly>=5.15.0
gradio>=4.0.0
```

---

## 🎯 **FUNCIONALIDADES**

### **Análisis de datos CSV:**
- ✅ Análisis por negocio
- ✅ Análisis por país
- ✅ Análisis por concepto
- ✅ Análisis por cohorte
- ✅ Resultado Comercial específico
- ✅ Resumen general

### **Chat con OpenAI:**
- ✅ Consultas financieras generales
- ✅ Estrategias de inversión
- ✅ Asesoramiento económico
- ✅ Análisis de mercado

### **Visualizaciones:**
- ✅ Gráficos interactivos
- ✅ Distribuciones por categorías
- ✅ Métricas en tiempo real

---

## 🚀 **COMANDOS DE DEPLOYMENT**

### **Streamlit local:**
```bash
pip install -r requirements_streamlit.txt
streamlit run app.py
```

### **Gradio local:**
```bash
pip install gradio pandas openai python-dotenv
python gradio_app.py
```

### **Replit:**
```bash
python replit_config.py
streamlit run app.py
```

---

## 📊 **OPTIMIZACIONES**

### **Para datos grandes:**
1. Comprimir CSV a Parquet
2. Usar `@st.cache_data` para caching
3. Filtrar datos temprano
4. Usar paginación

### **Para performance:**
1. Cargar datos solo cuando sea necesario
2. Usar índices en DataFrames
3. Optimizar consultas
4. Usar conexiones de base de datos

---

## 🎉 **¡LISTO PARA DEPLOYMENT!**

Tu chatbot financiero está optimizado para:
- ✅ **Streamlit Cloud** - Análisis avanzado
- ✅ **Gradio Spaces** - Chat simple
- ✅ **Replit** - Desarrollo rápido
- ✅ **Railway** - Producción

**¡Elige tu plataforma favorita y deploya en minutos!** 🚀
