# 🤖 Chatbot Financiero con Análisis de Datos CSV

## 📊 **Descripción**
Chatbot financiero inteligente que combina análisis de datos CSV con consultas generales de finanzas usando OpenAI GPT-3.5-turbo.

## 🚀 **Funcionalidades**
- ✅ Análisis completo de datos financieros CSV
- ✅ Chat inteligente con OpenAI
- ✅ Visualizaciones interactivas
- ✅ Interfaz web moderna y responsive
- ✅ Análisis por negocio, país, concepto y cohorte

## 📁 **Estructura del Proyecto**
```
finance-agent/
├── app.py                    # Aplicación Streamlit principal
├── gradio_app.py            # Aplicación Gradio alternativa
├── requirements_streamlit.txt # Dependencias para Streamlit
├── dataset/
│   └── Prueba-Chatbot - BBDD.csv
├── .streamlit/
│   └── secrets.toml         # Variables de entorno
└── README.md
```

## 🚀 **Deployment en Streamlit Cloud**

### **Paso 1: Fork este repositorio**
1. Haz fork de este repositorio
2. Clona tu fork localmente

### **Paso 2: Configurar variables de entorno**
1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Conecta tu cuenta de GitHub
3. Selecciona este repositorio
4. En "Advanced settings", agrega:
   - `OPENAI_API_KEY`: Tu API key de OpenAI
   - `OPENAI_MODEL`: gpt-3.5-turbo
   - `OPENAI_TEMPERATURE`: 0.5

### **Paso 3: Deploy**
1. Haz clic en "Deploy"
2. ¡Tu chatbot estará online en minutos!

## 💻 **Uso Local**

### **Streamlit:**
```bash
pip install -r requirements_streamlit.txt
streamlit run app.py
```

### **Gradio:**
```bash
pip install gradio pandas openai python-dotenv
python gradio_app.py
```

## 📊 **Análisis Disponibles**
- **Por Negocio**: PYME, CORP, Brokers, WK
- **Por País**: Chile (CL)
- **Por Concepto**: Clientes, Churn, Term, etc.
- **Por Cohorte**: <2024, 2024, 2025
- **Resultado Comercial específico**: 08-01-2025

## 🔧 **Configuración**
- **Modelo**: GPT-3.5-turbo
- **Temperatura**: 0.5
- **Max Tokens**: 1000
- **Sistema**: Asistente financiero experto

## 📞 **Soporte**
Si tienes problemas:
1. Revisa que el archivo CSV esté en la carpeta `dataset/`
2. Verifica que la API key de OpenAI esté configurada
3. Asegúrate de que todas las dependencias estén instaladas

## 🎉 **¡Disfruta tu chatbot financiero!**