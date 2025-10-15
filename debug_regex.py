#!/usr/bin/env python3
"""
Debug del patrón regex para fechas y períodos
"""

import re

# Patrones actuales
fechas_pattern = r'\b(0[7-9]|10)-01-2025\b'
periodos_pattern = r'\b(0[1-9]|1[0-2])-01-2025\b'

# Consulta de prueba
query = "Dame la Originacion Elaboracion 07-01-2025 y periodo 06-01-2025, en PYME"

print("=== DEBUG REGEX ===")
print(f"Consulta: {query}")
print()

# Probar fechas
fechas = re.findall(fechas_pattern, query)
print(f"Fechas encontradas: {fechas}")

# Probar períodos
periodos = re.findall(periodos_pattern, query)
print(f"Períodos encontrados: {periodos}")

print()
print("=== ANÁLISIS ===")
print("El patrón de fechas busca: 07-01-2025, 08-01-2025, 09-01-2025, 10-01-2025")
print("El patrón de períodos busca: 01-01-2025 a 12-01-2025")
print()
print("En la consulta:")
print("- '07-01-2025' coincide con el patrón de fechas ✅")
print("- '06-01-2025' coincide con el patrón de períodos ✅")
print()
print("PROBLEMA: Ambos patrones están capturando fechas, no distingue entre Elaboracion y Periodo")
