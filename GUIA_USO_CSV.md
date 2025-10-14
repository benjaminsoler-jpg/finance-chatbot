# 🤖 Guía de Uso del Chatbot con Análisis de Datos CSV

## 📊 **Resumen de Datos**
- **Total de registros:** 52,454
- **Valor total:** $9.6 billones
- **País:** Chile (CL)
- **Negocios:** PYME, CORP, Brokers, WK
- **Conceptos:** 19 diferentes (Originacion, Clientes, etc.)

## 🚀 **Cómo usar el chatbot con análisis de datos**

### **Opción 1: Analizador completo (Recomendado)**
```bash
# Resumen ejecutivo
python3 analizador_csv.py resumen

# Análisis por negocio
python3 analizador_csv.py negocio

# Análisis por país
python3 analizador_csv.py pais

# Análisis por concepto
python3 analizador_csv.py concepto

# Análisis de clientes
python3 analizador_csv.py clientes

# Top 20 registros por valor
python3 analizador_csv.py top 20
```

### **Opción 2: Chatbot con análisis automático**
```bash
# Análisis automático basado en palabras clave
python3 chatbot_csv.py "¿Cuál es el valor total por país?"
python3 chatbot_csv.py "Analiza la distribución por negocio"
python3 chatbot_csv.py "¿Cuáles son los top conceptos por valor?"
```

### **Opción 3: Consultas generales (sin análisis de datos)**
```bash
# Consultas financieras generales
python3 consulta_rapida.py "¿Cuáles son las mejores estrategias de inversión?"
python3 consulta_rapida.py "¿Cómo crear un presupuesto personal?"
```

## 📈 **Insights Clave de los Datos**

### **Por Negocio:**
1. **PYME:** $6.29 billones (65.5% del total)
2. **CORP:** $2.37 billones (24.7% del total)
3. **Brokers:** $715.4 millones (7.4% del total)
4. **WK:** $218.5 millones (2.3% del total)

### **Por Concepto:**
1. **Originacion:** $8.69 billones (90.5% del total)
2. **Clientes:** $1.36 millones (0.01% del total)
3. **Otros conceptos:** Varios

### **Por Clasificación de Clientes:**
1. **Active:** 421,010 clientes
2. **Old Active:** 381,774 clientes
3. **Total Operados:** 280,598 clientes
4. **Old Operados:** 239,014 clientes

## 🎯 **Ejemplos de Consultas Útiles**

### **Análisis de Negocio:**
```bash
python3 analizador_csv.py negocio
```

### **Análisis de Clientes:**
```bash
python3 analizador_csv.py clientes
```

### **Top Registros:**
```bash
python3 analizador_csv.py top 50
```

### **Resumen Ejecutivo:**
```bash
python3 analizador_csv.py resumen
```

## 🔧 **Archivos del Proyecto**

- `analizador_csv.py` - Analizador completo de datos CSV
- `chatbot_csv.py` - Chatbot con análisis automático
- `consulta_rapida.py` - Consultas generales
- `dataset/Prueba-Chatbot - BBDD.csv` - Datos financieros

## 💡 **Consejos de Uso**

1. **Para análisis rápido:** Usa `analizador_csv.py`
2. **Para consultas específicas:** Usa `chatbot_csv.py`
3. **Para consultas generales:** Usa `consulta_rapida.py`
4. **Para explorar datos:** Empieza con `resumen` y luego profundiza

## 🎉 **¡Tu chatbot financiero está listo!**

Ahora puedes hacer análisis completos de tus datos financieros y consultas generales sobre finanzas. ¡Disfruta explorando tus datos! 🚀
