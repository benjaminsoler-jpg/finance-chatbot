#!/usr/bin/env python3
"""
Test de los nuevos patrones regex
"""

import re

# Consulta de prueba
query = "Dame la Originacion Elaboracion 06-01-2025 y periodo 07-01-2025, en PYME"
query_lower = query.lower()

print("=== TEST DE PATRONES MEJORADOS ===")
print(f"Consulta: {query}")
print()

# Test Elaboracion
if 'elaboracion' in query_lower:
    elaboracion_match = re.search(r'elaboracion\s+(\d{2})-01-2025', query_lower)
    if elaboracion_match:
        elaboracion = elaboracion_match.group(1) + '-01-2025'
        print(f"✅ Elaboracion encontrada: {elaboracion}")
    else:
        print("❌ No se encontró Elaboracion")
else:
    print("ℹ️ No se menciona Elaboracion")

# Test Periodo
if 'periodo' in query_lower:
    periodo_match = re.search(r'periodo\s+(\d{2})-01-2025', query_lower)
    if periodo_match:
        periodo = periodo_match.group(1) + '-01-2025'
        print(f"✅ Periodo encontrado: {periodo}")
    else:
        print("❌ No se encontró Periodo")
else:
    print("ℹ️ No se menciona Periodo")

# Test Cohort_Act (no debería extraer)
if 'cohorte' in query_lower or 'cohort' in query_lower:
    print("ℹ️ Se menciona cohorte - se extraería")
else:
    print("✅ No se menciona cohorte - NO se extraerá")

print()
print("=== RESULTADO ESPERADO ===")
print("Elaboracion: 06-01-2025")
print("Periodo: 07-01-2025")
print("Negocio: PYME")
print("Concepto: Originacion")
print("Cohort_Act: NO (no se menciona)")
