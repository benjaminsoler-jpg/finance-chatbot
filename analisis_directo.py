#!/usr/bin/env python3
"""
Análisis directo del Resultado Comercial
"""

import pandas as pd
from colorama import Fore, Style

def main():
    print(f"{Fore.GREEN}🤖 Análisis de Resultado Comercial{Style.RESET_ALL}")
    print(f"{Fore.GREEN}==================================={Style.RESET_ALL}")
    
    # Cargar datos
    df = pd.read_csv('dataset/Prueba-Chatbot - BBDD.csv')
    df.columns = df.columns.str.strip()
    
    # Convertir Valor a numérico
    df['Valor'] = df['Valor'].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
    df.dropna(subset=['Valor'], inplace=True)
    
    print(f"✅ Datos cargados: {len(df)} registros")
    
    # Filtrar datos específicos
    filtro = (
        (df['Elaboracion'] == '08-01-2025') &
        (df['Periodo'] == '08-01-2025') &
        (df['Pais'] == 'CL') &
        (df['Escenario'] == 'Moderado')
    )
    
    datos = df[filtro]
    print(f"✅ Datos filtrados: {len(datos)} registros")
    
    if len(datos) == 0:
        print("❌ No hay datos para los filtros especificados")
        return
    
    # Análisis por Negocio y Cohort_Act
    print(f"\n{Fore.MAGENTA}📊 RESULTADO COMERCIAL POR NEGOCIO Y COHORTE{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    
    resultado = datos.groupby(['Negocio', 'Cohort_Act'])['Valor'].sum().reset_index()
    resultado = resultado.sort_values(['Negocio', 'Valor'], ascending=[True, False])
    
    total_general = datos['Valor'].sum()
    print(f"💰 Valor total: ${total_general:,.2f}")
    
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

if __name__ == "__main__":
    main()
