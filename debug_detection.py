#!/usr/bin/env python3
"""
Debug de la detección de keywords
"""

def is_financial_query(query: str) -> bool:
    """Detectar si la consulta es financiera o general"""
    financial_keywords = [
        'originacion', 'originación', 'gross revenue', 'margen financiero',
        'resultado comercial', 'churn', 'clientes', 'ad rate', 'ad revenue',
        'cost of fund', 'cost of risk', 'fund rate', 'int rate', 'interest revenue',
        'ntr', 'rate all in', 'risk rate', 'spread', 'term', 'elaboracion', 'elaboración',
        'periodo', 'período', 'negocio', 'concepto', 'clasificación', 'cohort',
        'escenario', 'pais', 'país', 'valor', 'análisis', 'analisis', 'datos',
        'financiero', 'financiera', 'comercial', 'ventas', 'ingresos', 'costos',
        'margen', 'rentabilidad', 'inversión', 'inversion', 'como me fue', 'como nos fue',
        'ultimos', 'últimos', 'meses', 'comparar', 'predicción', 'prediccion'
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in financial_keywords)

def debug_detection(query: str):
    """Debug de la detección"""
    print(f"\n🔍 QUERY: '{query}'")
    
    # 1. Verificar si es financiera
    is_financial = is_financial_query(query)
    print(f"💰 Es financiera: {is_financial}")
    
    if is_financial:
        # 2. Verificar "ultimos" y "meses"
        has_ultimos = 'ultimos' in query.lower()
        has_meses = 'meses' in query.lower()
        print(f"📅 Tiene 'ultimos': {has_ultimos}")
        print(f"📅 Tiene 'meses': {has_meses}")
        print(f"📅 Condición 'ultimos' AND 'meses': {has_ultimos and has_meses}")
        
        # 3. Verificar "como me fue"
        has_como_me_fue = 'como me fue' in query.lower()
        has_como_nos_fue = 'como nos fue' in query.lower()
        print(f"🤔 Tiene 'como me fue': {has_como_me_fue}")
        print(f"🤔 Tiene 'como nos fue': {has_como_nos_fue}")
        print(f"🤔 Condición 'como me fue' OR 'como nos fue': {has_como_me_fue or has_como_nos_fue}")
        
        # 4. Verificar "elaboracion"
        has_elaboracion = 'elaboracion' in query.lower()
        print(f"📊 Tiene 'elaboracion': {has_elaboracion}")
        print(f"📊 Condición completa: {(has_como_me_fue or has_como_nos_fue) and has_elaboracion}")

# Probar la consulta problemática
test_query = "Como me fue los 3 ultimo meses en la Elaboracion 08-01-2025? en Escenario Moderado y que este distribuida por Negocio la Respuesta"

debug_detection(test_query)
