#!/usr/bin/env python3
"""
Test de conversión a enteros
"""

import pandas as pd

# Cargar datos
df = pd.read_csv('dataset/Prueba-Chatbot - BBDD.csv')

print("=== TEST CONVERSIÓN A ENTEROS ===")
print(f"Total de registros: {len(df):,}")
print()

# Mostrar valores originales
print("📊 VALORES ORIGINALES (primeros 10):")
for i, valor in enumerate(df['Valor'].head(10)):
    print(f"  {i+1:2d}. {valor}")

print()

# Convertir a enteros como en el código (CORREGIDO)
df['Valor'] = df['Valor'].astype(str).str.replace(',', '')
df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce').fillna(0).astype(int)

print("📊 VALORES CONVERTIDOS A ENTEROS (primeros 10):")
for i, valor in enumerate(df['Valor'].head(10)):
    print(f"  {i+1:2d}. {valor:,}")

print()

# Estadísticas
print("📈 ESTADÍSTICAS:")
print(f"  - Suma total: ${df['Valor'].sum():,}")
print(f"  - Promedio: ${df['Valor'].mean():.0f}")
print(f"  - Máximo: ${df['Valor'].max():,}")
print(f"  - Mínimo: ${df['Valor'].min():,}")
print(f"  - Valores cero: {(df['Valor'] == 0).sum():,}")

print()

# Verificar conceptos específicos
print("🎯 CONCEPTOS ESPECÍFICOS:")
conceptos_importantes = ['Margen Financiero', 'Gross Revenue', 'Originacion', 'Clientes']
for concepto in conceptos_importantes:
    concepto_data = df[df['Concepto'] == concepto]
    if len(concepto_data) > 0:
        suma = concepto_data['Valor'].sum()
        print(f"  - {concepto}: ${suma:,} ({len(concepto_data):,} registros)")
    else:
        print(f"  - {concepto}: No encontrado")
