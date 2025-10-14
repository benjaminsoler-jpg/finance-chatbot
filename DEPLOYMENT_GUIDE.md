# 🚀 Guía de Deployment - Chatbot Financiero

## 📋 **PLATAFORMAS RECOMENDADAS**

### **1. Streamlit Cloud (Recomendado)**
- ✅ **Gratuito** con límites generosos
- ✅ **Fácil deployment** desde GitHub
- ✅ **Perfecto para análisis de datos**
- ✅ **Soporte nativo para Pandas**

### **2. Gradio Spaces (Hugging Face)**
- ✅ **Completamente gratuito**
- ✅ **Interfaz de chat perfecta**
- ✅ **Deployment automático**

### **3. Replit**
- ✅ **Gratuito** con límites
- ✅ **IDE online completo**
- ✅ **Base de datos incluida**

---

## 🚀 **DEPLOYMENT EN STREAMLIT CLOUD**

### **Paso 1: Preparar el repositorio**
```bash
# Crear repositorio en GitHub
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/tu-usuario/finance-chatbot.git
git push -u origin main
```

### **Paso 2: Archivos necesarios**
```
finance-chatbot/
├── app.py                    # Aplicación Streamlit
├── requirements_streamlit.txt # Dependencias
├── dataset/
│   └── Prueba-Chatbot - BBDD.csv
├── .streamlit/
│   └── secrets.toml         # Variables de entorno
└── README.md
```

### **Paso 3: Configurar secrets**
Crear `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "tu-api-key-aqui"
```

### **Paso 4: Deploy en Streamlit Cloud**
1. Ir a [share.streamlit.io](https://share.streamlit.io)
2. Conectar con GitHub
3. Seleccionar repositorio
4. Configurar:
   - **Main file path:** `app.py`
   - **Requirements file:** `requirements_streamlit.txt`
5. Deploy!

---

## 🚀 **DEPLOYMENT EN GRADIO SPACES**

### **Paso 1: Crear Space en Hugging Face**
1. Ir a [huggingface.co/spaces](https://huggingface.co/spaces)
2. Crear nuevo Space
3. Seleccionar "Gradio" como SDK

### **Paso 2: Archivos necesarios**
```
finance-chatbot/
├── gradio_app.py            # Aplicación Gradio
├── requirements.txt         # Dependencias
├── dataset/
│   └── Prueba-Chatbot - BBDD.csv
└── README.md
```

### **Paso 3: requirements.txt**
```
gradio>=4.0.0
pandas>=1.5.0
openai>=1.3.0
python-dotenv>=1.0.0
```

### **Paso 4: Configurar variables de entorno**
En el Space, ir a Settings > Variables:
```
OPENAI_API_KEY=tu-api-key-aqui
```

---

## 🚀 **DEPLOYMENT EN REPLIT**

### **Paso 1: Crear nuevo Repl**
1. Ir a [replit.com](https://replit.com)
2. Crear nuevo Repl
3. Seleccionar "Python"

### **Paso 2: Subir archivos**
1. Subir `app.py` o `gradio_app.py`
2. Subir `requirements.txt`
3. Subir archivo CSV a la carpeta `dataset/`

### **Paso 3: Configurar variables de entorno**
En Repl, ir a Secrets:
```
OPENAI_API_KEY=tu-api-key-aqui
```

### **Paso 4: Instalar dependencias**
```bash
pip install -r requirements.txt
```

### **Paso 5: Ejecutar**
```bash
# Para Streamlit
streamlit run app.py

# Para Gradio
python gradio_app.py
```

---

## 🚀 **DEPLOYMENT EN RAILWAY**

### **Paso 1: Crear proyecto**
1. Ir a [railway.app](https://railway.app)
2. Crear nuevo proyecto
3. Conectar con GitHub

### **Paso 2: Archivos necesarios**
```
finance-chatbot/
├── app.py
├── requirements.txt
├── Procfile
├── dataset/
│   └── Prueba-Chatbot - BBDD.csv
└── README.md
```

### **Paso 3: Procfile**
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

### **Paso 4: Configurar variables**
En Railway, ir a Variables:
```
OPENAI_API_KEY=tu-api-key-aqui
```

---

## 📊 **OPTIMIZACIONES PARA DATOS CSV**

### **1. Compresión de datos**
```python
# Comprimir CSV antes de subir
import pandas as pd
df = pd.read_csv('dataset/Prueba-Chatbot - BBDD.csv')
df.to_parquet('dataset/data.parquet', compression='gzip')
```

### **2. Carga lazy**
```python
# Cargar datos solo cuando sea necesario
@st.cache_data
def load_data():
    return pd.read_csv('dataset/data.parquet')
```

### **3. Filtrado temprano**
```python
# Filtrar datos antes de procesar
def get_filtered_data(filters):
    df = load_data()
    for column, value in filters.items():
        df = df[df[column] == value]
    return df
```

---

## 🔧 **CONFIGURACIÓN DE VARIABLES DE ENTORNO**

### **Streamlit Cloud**
```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "sk-..."
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_TEMPERATURE = "0.5"
```

### **Gradio Spaces**
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.5
```

### **Replit**
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.5
```

---

## 🎯 **RECOMENDACIONES FINALES**

### **Para datos grandes:**
1. **Streamlit Cloud** - Mejor para análisis complejos
2. **Gradio Spaces** - Mejor para interfaces de chat
3. **Replit** - Mejor para desarrollo y testing

### **Para datos pequeños:**
1. **Gradio Spaces** - Más simple y rápido
2. **Streamlit Cloud** - Más funcionalidades
3. **Replit** - Más control

### **Para producción:**
1. **Railway** - Más estable
2. **Streamlit Cloud** - Más confiable
3. **Gradio Spaces** - Más económico

---

## 🚀 **COMANDOS RÁPIDOS**

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
pip install -r requirements.txt
python app.py
```

---

## 📞 **SOPORTE**

Si tienes problemas con el deployment:
1. Revisa los logs de la plataforma
2. Verifica las variables de entorno
3. Asegúrate de que el archivo CSV esté en la ubicación correcta
4. Revisa que todas las dependencias estén instaladas

**¡Tu chatbot financiero estará online en minutos!** 🎉
