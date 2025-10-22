#!/usr/bin/env python3
"""
Script de debug para probar la función analyze_last_months_performance
"""

import pandas as pd
import re
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('config.env')

# Cargar datos
print("📊 Cargando datos...")
df = pd.read_csv('dataset/Prueba-Chatbot - BBDD.csv')
df.columns = df.columns.str.strip()
df['Valor'] = df['Valor'].astype(str).str.replace(',', '')
df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0).astype(int)
df.dropna(subset=['Valor'], inplace=True)

print(f"✅ Datos cargados: {len(df):,} registros")

# Función de debug
def debug_analyze_last_months_performance(query: str) -> str:
    """Debug de la función analyze_last_months_performance"""
    print(f"\n🔍 DEBUGGING QUERY: '{query}'")
    
    # Extraer elaboración y cantidad de meses
    elaboracion_match = re.search(r'elaboraci[oó]n\s+(\d{2})-01-2025', query.lower())
    meses_match = re.search(r'ultimos?\s+(\d+)\s+meses?', query.lower())
    
    print(f"📅 Elaboracion match: {elaboracion_match}")
    print(f"📅 Meses match: {meses_match}")
    
    if not elaboracion_match:
        print("❌ NO SE ENCONTRÓ ELABORACIÓN - RETORNANDO None")
        return None
    
    elaboracion = elaboracion_match.group(1) + '-01-2025'
    meses = int(meses_match.group(1)) if meses_match else 3
    
    print(f"📅 Elaboración extraída: {elaboracion}")
    print(f"📅 Meses extraídos: {meses}")
    
    # Extraer filtros adicionales
    escenario = None
    if 'moderado' in query.lower():
        escenario = 'Moderado'
    elif 'ambicion' in query.lower():
        escenario = 'Ambicion'
    
    print(f"🎯 Escenario detectado: {escenario}")
    
    # Calcular períodos anteriores
    mes_actual = int(elaboracion.split('-')[0])
    periodos = []
    for i in range(meses):
        mes_anterior = mes_actual - i - 1
        if mes_anterior <= 0:
            mes_anterior += 12
        periodos.append(f"{mes_anterior:02d}-01-2025")
    
    print(f"📅 Períodos calculados: {periodos}")
    
    # Verificar si hay datos para estos períodos
    for periodo in periodos:
        data = df[
            (df['Elaboracion'] == elaboracion) & 
            (df['Periodo'] == periodo)
        ]
        print(f"📊 Datos para {periodo}: {len(data)} registros")
    
    return "✅ FUNCIÓN EJECUTADA CORRECTAMENTE"

# Probar diferentes consultas
test_queries = [
    "Como me fue los 3 ultimo meses en la ELaboracion 08-01-2025? en Escenario Moderado",
    "ultimos 3 meses elaboracion 08-01-2025",
    "como me fue los ultimos 3 meses de elaboracion 08-01-2025",
    "ultimos 3 meses de elaboracion 08-01-2025 en escenario moderado"
]

for query in test_queries:
    result = debug_analyze_last_months_performance(query)
    print(f"\n{'='*60}")
    print(f"RESULTADO: {result}")
    print(f"{'='*60}\n")
