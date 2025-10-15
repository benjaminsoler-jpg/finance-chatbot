#!/usr/bin/env python3
"""
Análisis completo del CSV para identificar todas las combinaciones posibles de preguntas
"""

import pandas as pd
import numpy as np

def analizar_csv():
    """Analizar completamente el CSV"""
    
    # Cargar datos
    df = pd.read_csv('dataset/Prueba-Chatbot - BBDD.csv', encoding='utf-8')
    df.columns = df.columns.str.strip()
    
    print('=' * 80)
    print('📊 ANÁLISIS COMPLETO DEL CSV - COMBINACIONES DE PREGUNTAS')
    print('=' * 80)
    print(f'Total de registros: {len(df):,}')
    print(f'Total de columnas: {len(df.columns)}')
    print()
    
    # Analizar cada columna
    columnas_analisis = {}
    
    for col in df.columns:
        print(f'🔍 === {col.upper()} ===')
        unique_values = df[col].unique()
        print(f'Valores únicos: {len(unique_values)}')
        
        # Guardar para análisis posterior
        columnas_analisis[col] = {
            'valores': unique_values,
            'total': len(unique_values)
        }
        
        if len(unique_values) <= 20:
            # Filtrar NaN y ordenar
            unique_clean = [val for val in unique_values if pd.notna(val)]
            for val in sorted(unique_clean):
                count = len(df[df[col] == val])
                print(f'  - {val}: {count:,} registros')
            
            # Mostrar NaN si existen
            nan_count = len(df[df[col].isna()])
            if nan_count > 0:
                print(f'  - (NaN): {nan_count:,} registros')
        else:
            print(f'  (Demasiados valores únicos para mostrar)')
            print(f'  Primeros 10: {list(unique_values[:10])}')
            print(f'  Últimos 10: {list(unique_values[-10:])}')
        print()
    
    # Análisis de combinaciones más comunes
    print('🎯 === COMBINACIONES MÁS COMUNES ===')
    
    # Combinaciones por fecha
    print('\n📅 Por Fecha (Elaboracion + Periodo):')
    fecha_combo = df.groupby(['Elaboracion', 'Periodo']).size().sort_values(ascending=False)
    print(f'Total combinaciones de fecha: {len(fecha_combo)}')
    for i, (combo, count) in enumerate(fecha_combo.head(10).items()):
        print(f'{i+1}. {combo[0]} + {combo[1]}: {count:,} registros')
    
    # Combinaciones por negocio + concepto
    print('\n🏢 Por Negocio + Concepto:')
    negocio_concepto = df.groupby(['Negocio', 'Concepto']).size().sort_values(ascending=False)
    print(f'Total combinaciones negocio-concepto: {len(negocio_concepto)}')
    for i, (combo, count) in enumerate(negocio_concepto.head(10).items()):
        print(f'{i+1}. {combo[0]} + {combo[1]}: {count:,} registros')
    
    # Combinaciones por cohorte + clasificación
    print('\n📈 Por Cohorte + Clasificación:')
    cohorte_clasif = df.groupby(['Cohort_Act', 'Clasificación']).size().sort_values(ascending=False)
    print(f'Total combinaciones cohorte-clasificación: {len(cohorte_clasif)}')
    for i, (combo, count) in enumerate(cohorte_clasif.head(10).items()):
        print(f'{i+1}. {combo[0]} + {combo[1]}: {count:,} registros')
    
    # Combinaciones completas más comunes
    print('\n🎯 Combinaciones Completas (Top 10):')
    combo_completa = df.groupby(['Elaboracion', 'Periodo', 'Pais', 'Negocio', 'Concepto', 'Escenario']).size().sort_values(ascending=False)
    print(f'Total combinaciones completas: {len(combo_completa):,}')
    for i, (combo, count) in enumerate(combo_completa.head(10).items()):
        print(f'{i+1}. {combo}: {count:,} registros')
    
    # Generar ejemplos de preguntas
    print('\n💡 === EJEMPLOS DE PREGUNTAS POSIBLES ===')
    
    # Preguntas por columna individual
    print('\n📊 Preguntas por Columna Individual:')
    for col, data in columnas_analisis.items():
        if data['total'] <= 10:
            print(f'\n{col}:')
            for val in data['valores']:
                print(f'  - "¿Cuál es el valor total de {col} = {val}?"')
        else:
            print(f'\n{col}: (Demasiados valores - usar filtros)')
            print(f'  - "¿Cuál es el valor total por {col}?"')
            print(f'  - "¿Cuáles son los valores únicos de {col}?"')
    
    # Preguntas por combinaciones
    print('\n🔗 Preguntas por Combinaciones:')
    
    # Fecha + Negocio
    print('\n📅 + 🏢 Fecha + Negocio:')
    for fecha in df['Elaboracion'].unique()[:3]:
        for negocio in df['Negocio'].unique():
            print(f'  - "¿Cuál es el valor de {negocio} en {fecha}?"')
    
    # Negocio + Concepto
    print('\n🏢 + 📋 Negocio + Concepto:')
    for negocio in df['Negocio'].unique():
        for concepto in df['Concepto'].unique()[:3]:
            print(f'  - "¿Cuál es el valor de {concepto} en {negocio}?"')
    
    # Cohorte + Clasificación
    print('\n📈 + 🏷️ Cohorte + Clasificación:')
    for cohorte in df['Cohort_Act'].unique()[:3]:
        for clasif in df['Clasificación'].unique()[:3]:
            print(f'  - "¿Cuál es el valor de {clasif} en cohorte {cohorte}?"')
    
    # Preguntas complejas
    print('\n🎯 Preguntas Complejas (Múltiples Filtros):')
    print('  - "¿Cuál es el valor de PYME en CL para 08-01-2025 en escenario Moderado?"')
    print('  - "¿Cuál es la Originación de CORP en 2024 para Chile?"')
    print('  - "¿Cuál es el valor total por negocio en el período 08-01-2025?"')
    print('  - "¿Cuáles son los valores de Active vs Old Active por cohorte?"')
    print('  - "¿Cuál es la distribución de valores por país y negocio?"')
    
    # Preguntas de análisis
    print('\n📊 Preguntas de Análisis:')
    print('  - "¿Cuál es el negocio con mayor valor?"')
    print('  - "¿Cuál es la cohorte más rentable?"')
    print('  - "¿Cuál es la tendencia por período?"')
    print('  - "¿Cuál es la distribución por clasificación?"')
    print('  - "¿Cuáles son los top 5 conceptos por valor?"')
    
    return columnas_analisis

if __name__ == "__main__":
    analizar_csv()
