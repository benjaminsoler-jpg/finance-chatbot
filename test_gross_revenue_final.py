#!/usr/bin/env python3
"""
Test final para la consulta de Gross Revenue con última funcionalidad
"""

import re

# Consulta de prueba
query = "dame el gross revenue de los ultimos 3 periodos de la elaboracion 07-01-2025"
query_lower = query.lower()

print("=== TEST FINAL GROSS REVENUE ===")
print(f"Consulta: {query}")
print()

# Simular la extracción de filtros
filters = {}

# Test Elaboracion
if 'elaboracion' in query_lower:
    elaboracion_match = re.search(r'elaboracion\s+(\d{2})-01-2025', query_lower)
    if elaboracion_match:
        elaboracion = elaboracion_match.group(1) + '-01-2025'
        filters['Elaboracion'] = elaboracion
        print(f"✅ Elaboracion: {elaboracion}")

# Test Concepto
conceptos = re.findall(r'\b(Originacion|Resultado Comercial|Churn|Clientes|AD Rate|AD Revenue|Cost of Fund|Cost of Risk|Fund Rate|Gross Revenue|Int Rate|Interest Revenue|Margen Financiero|NTR|Originacion Prom|Rate All In|Risk Rate|Spread|Term)\b', query, re.IGNORECASE)
if conceptos:
    filters['Concepto'] = conceptos[0]
    print(f"✅ Concepto: {conceptos[0]}")

# Test "últimos N períodos"
if 'ultimos' in query_lower and ('periodos' in query_lower or 'períodos' in query_lower):
    ultimos_match = re.search(r'ultimos?\s+(\d+)\s+periodos?', query_lower)
    if ultimos_match:
        filters['ultimos_periodos'] = int(ultimos_match.group(1))
        print(f"✅ Últimos períodos: {ultimos_match.group(1)}")

# Simular cálculo de períodos anteriores
def get_periodos_anteriores(elaboracion, cantidad):
    mes_elaboracion = int(elaboracion.split('-')[0])
    periodos = []
    for i in range(cantidad):
        mes_anterior = mes_elaboracion - i - 1
        if mes_anterior <= 0:
            mes_anterior += 12
        periodos.append(f"{mes_anterior:02d}-01-2025")
    return periodos

if 'Elaboracion' in filters and 'ultimos_periodos' in filters:
    periodos = get_periodos_anteriores(filters['Elaboracion'], filters['ultimos_periodos'])
    print(f"✅ Períodos calculados: {periodos}")

print()
print("=== RESULTADO ESPERADO ===")
print("El chatbot debería:")
print("1. Filtrar por Elaboracion: 07-01-2025")
print("2. Filtrar por Concepto: Gross Revenue")
print("3. Filtrar por los últimos 3 períodos: 06-01-2025, 05-01-2025, 04-01-2025")
print("4. Mostrar análisis agrupado por período")
print("5. Mostrar valores de Gross Revenue para cada período")
