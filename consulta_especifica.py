#!/usr/bin/env python3
"""
Script específico para consultar Resultado Comercial por elaboración, periodo, país, negocio y cohortes
"""

import pandas as pd
import os
from colorama import Fore, Style

def analizar_resultado_comercial():
    """Analizar Resultado Comercial específico"""
    csv_file = "dataset/Prueba-Chatbot - BBDD.csv"
    
    try:
        # Cargar datos
        print(f"{Fore.CYAN}📊 Cargando datos del CSV...{Style.RESET_ALL}")
        df = pd.read_csv(csv_file, encoding='utf-8')
        
        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip()
        
        # Convertir Valor a numérico
        df['Valor'] = df['Valor'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
        df.dropna(subset=['Valor'], inplace=True)
        
        print(f"{Fore.GREEN}✅ Datos cargados: {len(df)} registros{Style.RESET_ALL}")
        
        # Filtrar datos específicos
        print(f"{Fore.YELLOW}🔍 Filtrando datos para la consulta específica...{Style.RESET_ALL}")
        
        # Filtrar por elaboración 08-01-2025, periodo 08-01-2025, país CL, escenario Moderado
        filtro = (
            (df['Elaboracion'] == '08-01-2025') &
            (df['Periodo'] == '08-01-2025') &
            (df['Pais'] == 'CL') &
            (df['Escenario '] == 'Moderado')
        )
        
        datos_filtrados = df[filtro]
        
        if len(datos_filtrados) == 0:
            print(f"{Fore.RED}❌ No se encontraron datos con los filtros especificados{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}📋 Valores únicos disponibles:{Style.RESET_ALL}")
            print(f"Elaboración: {df['Elaboracion'].unique()}")
            print(f"Período: {df['Periodo'].unique()}")
            print(f"País: {df['Pais'].unique()}")
            print(f"Escenario: {df['Escenario '].unique()}")
            return
        
        print(f"{Fore.GREEN}✅ Datos filtrados: {len(datos_filtrados)} registros{Style.RESET_ALL}")
        
        # Análisis por Negocio y Cohort_Act
        print(f"\n{Fore.MAGENTA}📊 RESULTADO COMERCIAL POR NEGOCIO Y COHORTE{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
        
        # Agrupar por Negocio y Cohort_Act
        resultado = datos_filtrados.groupby(['Negocio', 'Cohort_Act'])['Valor'].sum().reset_index()
        resultado = resultado.sort_values(['Negocio', 'Valor'], ascending=[True, False])
        
        # Mostrar resultados por negocio
        for negocio in resultado['Negocio'].unique():
            print(f"\n{Fore.CYAN}🏢 NEGOCIO: {negocio}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'-'*40}{Style.RESET_ALL}")
            
            negocio_data = resultado[resultado['Negocio'] == negocio]
            total_negocio = negocio_data['Valor'].sum()
            
            for _, row in negocio_data.iterrows():
                cohorte = row['Cohort_Act'] if pd.notna(row['Cohort_Act']) else 'Sin cohorte'
                valor = row['Valor']
                porcentaje = (valor / total_negocio) * 100 if total_negocio > 0 else 0
                print(f"  📈 {cohorte}: ${valor:,.2f} ({porcentaje:.1f}%)")
            
            print(f"  {Fore.YELLOW}💰 TOTAL {negocio}: ${total_negocio:,.2f}{Style.RESET_ALL}")
        
        # Resumen general
        print(f"\n{Fore.GREEN}📊 RESUMEN GENERAL{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*40}{Style.RESET_ALL}")
        
        total_general = datos_filtrados['Valor'].sum()
        print(f"💰 Valor total: ${total_general:,.2f}")
        print(f"📊 Total de registros: {len(datos_filtrados):,}")
        
        # Análisis por concepto
        print(f"\n{Fore.BLUE}📋 ANÁLISIS POR CONCEPTO{Style.RESET_ALL}")
        print(f"{Fore.BLUE}{'-'*30}{Style.RESET_ALL}")
        concepto_analysis = datos_filtrados.groupby('Concepto')['Valor'].sum().sort_values(ascending=False)
        for concepto, valor in concepto_analysis.items():
            porcentaje = (valor / total_general) * 100 if total_general > 0 else 0
            print(f"  📊 {concepto}: ${valor:,.2f} ({porcentaje:.1f}%)")
        
        # Análisis por clasificación
        print(f"\n{Fore.MAGENTA}📋 ANÁLISIS POR CLASIFICACIÓN{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'-'*30}{Style.RESET_ALL}")
        clasificacion_analysis = datos_filtrados.groupby('Clasificación')['Valor'].sum().sort_values(ascending=False)
        for clasificacion, valor in clasificacion_analysis.items():
            porcentaje = (valor / total_general) * 100 if total_general > 0 else 0
            print(f"  📊 {clasificacion}: ${valor:,.2f} ({porcentaje:.1f}%)")
        
    except FileNotFoundError:
        print(f"{Fore.RED}❌ Error: El archivo CSV no se encontró{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    print(f"{Fore.GREEN}🤖 Análisis Específico de Resultado Comercial{Style.RESET_ALL}")
    print(f"{Fore.GREEN}============================================{Style.RESET_ALL}")
    analizar_resultado_comercial()
