#!/usr/bin/env python3
"""
Test del regex mejorado
"""

import re

test_queries = [
    "Como me fue los 3 ultimo meses en la ELaboracion 08-01-2025? en Escenario Moderado",
    "ultimos 3 meses elaboracion 08-01-2025",
    "como me fue los ultimos 3 meses de elaboracion 08-01-2025",
    "ultimos 3 meses de elaboracion 08-01-2025 en escenario moderado"
]

for query in test_queries:
    print(f"\n🔍 QUERY: '{query}'")
    
    # Regex original
    meses_match_old = re.search(r'ultimos?\s+(\d+)\s+meses?', query.lower())
    print(f"📅 Regex OLD: {meses_match_old}")
    
    # Regex mejorado
    meses_match_new = re.search(r'ultimos?\s*(\d+)\s*meses?', query.lower())
    print(f"📅 Regex NEW: {meses_match_new}")
    
    if meses_match_new:
        print(f"✅ Meses extraídos: {meses_match_new.group(1)}")
    else:
        print("❌ NO MATCH")
