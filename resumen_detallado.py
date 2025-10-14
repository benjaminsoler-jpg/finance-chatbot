#!/usr/bin/env python3
"""
Resumen detallado del Resultado Comercial
"""

import pandas as pd
from colorama import Fore, Style

def main():
    print(f"{Fore.GREEN}🤖 RESUMEN DETALLADO - RESULTADO COMERCIAL{Style.RESET_ALL}")
    print(f"{Fore.GREEN}==========================================={Style.RESET_ALL}")
    print(f"📅 Elaboración: 08-01-2025")
    print(f"📅 Período: 08-01-2025")
    print(f"🌍 País: CL (Chile)")
    print(f"📊 Escenario: Moderado")
    print(f"{Fore.GREEN}{'='*50}{Style.RESET_ALL}")
    
    # Cargar datos
    df = pd.read_csv('dataset/Prueba-Chatbot - BBDD.csv')
    df.columns = df.columns.str.strip()
    
    # Convertir Valor a numérico
    df['Valor'] = df['Valor'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
    df.dropna(subset=['Valor'], inplace=True)
    
    # Filtrar datos específicos
    filtro = (
        (df['Elaboracion'] == '08-01-2025') &
        (df['Periodo'] == '08-01-2025') &
        (df['Pais'] == 'CL') &
        (df['Escenario'] == 'Moderado')
    )
    
    datos = df[filtro]
    
    # Análisis por Negocio y Cohort_Act
    resultado = datos.groupby(['Negocio', 'Cohort_Act'])['Valor'].sum().reset_index()
    resultado = resultado.sort_values(['Negocio', 'Valor'], ascending=[True, False])
    
    total_general = datos['Valor'].sum()
    print(f"\n{Fore.CYAN}💰 VALOR TOTAL: ${total_general:,.2f}{Style.RESET_ALL}")
    print(f"📊 Total de registros: {len(datos):,}")
    
    # Análisis por negocio
    print(f"\n{Fore.MAGENTA}📊 ANÁLISIS POR NEGOCIO{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*40}{Style.RESET_ALL}")
    
    for negocio in resultado['Negocio'].unique():
        negocio_data = resultado[resultado['Negocio'] == negocio]
        total_negocio = negocio_data['Valor'].sum()
        porcentaje_negocio = (total_negocio / total_general) * 100
        
        print(f"\n{Fore.CYAN}🏢 {negocio}{Style.RESET_ALL}")
        print(f"💰 Total: ${total_negocio:,.2f} ({porcentaje_negocio:.1f}% del total)")
        
        for _, row in negocio_data.iterrows():
            cohorte = row['Cohort_Act'] if pd.notna(row['Cohort_Act']) else 'Sin cohorte'
            valor = row['Valor']
            porcentaje = (valor / total_negocio) * 100 if total_negocio > 0 else 0
            print(f"  📈 {cohorte}: ${valor:,.2f} ({porcentaje:.1f}%)")
    
    # Análisis por cohorte
    print(f"\n{Fore.BLUE}📊 ANÁLISIS POR COHORTE{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{'='*30}{Style.RESET_ALL}")
    
    cohorte_analysis = datos.groupby('Cohort_Act')['Valor'].sum().sort_values(ascending=False)
    for cohorte, valor in cohorte_analysis.items():
        porcentaje = (valor / total_general) * 100 if total_general > 0 else 0
        print(f"📈 {cohorte}: ${valor:,.2f} ({porcentaje:.1f}%)")
    
    # Análisis por concepto
    print(f"\n{Fore.YELLOW}📋 ANÁLISIS POR CONCEPTO{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'='*30}{Style.RESET_ALL}")
    
    concepto_analysis = datos.groupby('Concepto')['Valor'].sum().sort_values(ascending=False)
    for concepto, valor in concepto_analysis.items():
        porcentaje = (valor / total_general) * 100 if total_general > 0 else 0
        print(f"📊 {concepto}: ${valor:,.2f} ({porcentaje:.1f}%)")
    
    # Análisis por clasificación
    print(f"\n{Fore.MAGENTA}📋 ANÁLISIS POR CLASIFICACIÓN{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*30}{Style.RESET_ALL}")
    
    clasificacion_analysis = datos.groupby('Clasificación')['Valor'].sum().sort_values(ascending=False)
    for clasificacion, valor in clasificacion_analysis.items():
        porcentaje = (valor / total_general) * 100 if total_general > 0 else 0
        print(f"📊 {clasificacion}: ${valor:,.2f} ({porcentaje:.1f}%)")
    
    print(f"\n{Fore.GREEN}✅ Análisis completado{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
