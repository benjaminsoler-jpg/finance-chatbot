#!/usr/bin/env python3
"""
Analizador de datos CSV financieros - Versión completa sin dependencias externas
"""

import pandas as pd
import sys
import os

class AnalizadorCSV:
    def __init__(self):
        self.csv_path = "dataset/Prueba-Chatbot - BBDD.csv"
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Cargar datos del CSV"""
        try:
            print("📊 Cargando datos del CSV...")
            self.df = pd.read_csv(self.csv_path)
            # Limpiar datos
            self.df['Valor'] = pd.to_numeric(self.df['Valor'].astype(str).str.replace(',', ''), errors='coerce')
            print(f"✅ Datos cargados: {len(self.df)} registros")
            print(f"📋 Columnas: {list(self.df.columns)}")
        except Exception as e:
            print(f"❌ Error cargando CSV: {e}")
            self.df = None
    
    def analisis_general(self):
        """Análisis general de los datos"""
        if self.df is None:
            return "❌ No se pudieron cargar los datos del CSV"
        
        analysis = []
        
        # Estadísticas básicas
        total_valor = self.df['Valor'].sum()
        analysis.append(f"💰 **VALOR TOTAL:** ${total_valor:,.2f}")
        
        # Por país
        pais_stats = self.df.groupby('Pais')['Valor'].sum().sort_values(ascending=False)
        analysis.append(f"\n🌍 **POR PAÍS:**\n{pais_stats.to_string()}")
        
        # Por negocio
        negocio_stats = self.df.groupby('Negocio')['Valor'].sum().sort_values(ascending=False)
        analysis.append(f"\n🏢 **POR NEGOCIO:**\n{negocio_stats.to_string()}")
        
        # Por concepto
        concepto_stats = self.df.groupby('Concepto')['Valor'].sum().sort_values(ascending=False)
        analysis.append(f"\n📊 **POR CONCEPTO:**\n{concepto_stats.to_string()}")
        
        # Por escenario
        escenario_stats = self.df.groupby('Escenario ')['Valor'].sum().sort_values(ascending=False)
        analysis.append(f"\n🎯 **POR ESCENARIO:**\n{escenario_stats.to_string()}")
        
        return "\n".join(analysis)
    
    def analisis_pais(self):
        """Análisis detallado por país"""
        if self.df is None:
            return "❌ No se pudieron cargar los datos del CSV"
        
        analysis = []
        
        # Análisis por país
        pais_analysis = self.df.groupby('Pais').agg({
            'Valor': ['sum', 'count', 'mean'],
            'Negocio': 'nunique',
            'Concepto': 'nunique'
        }).round(2)
        
        pais_analysis.columns = ['Valor_Total', 'Cantidad_Registros', 'Valor_Promedio', 'Negocios_Unicos', 'Conceptos_Unicos']
        pais_analysis = pais_analysis.sort_values('Valor_Total', ascending=False)
        
        analysis.append("🌍 **ANÁLISIS DETALLADO POR PAÍS:**")
        analysis.append(pais_analysis.to_string())
        
        return "\n".join(analysis)
    
    def analisis_negocio(self):
        """Análisis detallado por negocio"""
        if self.df is None:
            return "❌ No se pudieron cargar los datos del CSV"
        
        analysis = []
        
        # Análisis por negocio
        negocio_analysis = self.df.groupby('Negocio').agg({
            'Valor': ['sum', 'count', 'mean'],
            'Pais': 'nunique',
            'Concepto': 'nunique'
        }).round(2)
        
        negocio_analysis.columns = ['Valor_Total', 'Cantidad_Registros', 'Valor_Promedio', 'Paises_Unicos', 'Conceptos_Unicos']
        negocio_analysis = negocio_analysis.sort_values('Valor_Total', ascending=False)
        
        analysis.append("🏢 **ANÁLISIS DETALLADO POR NEGOCIO:**")
        analysis.append(negocio_analysis.to_string())
        
        return "\n".join(analysis)
    
    def analisis_concepto(self):
        """Análisis detallado por concepto"""
        if self.df is None:
            return "❌ No se pudieron cargar los datos del CSV"
        
        analysis = []
        
        # Análisis por concepto
        concepto_analysis = self.df.groupby('Concepto').agg({
            'Valor': ['sum', 'count', 'mean'],
            'Pais': 'nunique',
            'Negocio': 'nunique'
        }).round(2)
        
        concepto_analysis.columns = ['Valor_Total', 'Cantidad_Registros', 'Valor_Promedio', 'Paises_Unicos', 'Negocios_Unicos']
        concepto_analysis = concepto_analysis.sort_values('Valor_Total', ascending=False)
        
        analysis.append("📊 **ANÁLISIS DETALLADO POR CONCEPTO:**")
        analysis.append(concepto_analysis.to_string())
        
        return "\n".join(analysis)
    
    def top_registros(self, n=20):
        """Top N registros por valor"""
        if self.df is None:
            return "❌ No se pudieron cargar los datos del CSV"
        
        analysis = []
        
        # Top registros
        top_registros = self.df.nlargest(n, 'Valor')[['Pais', 'Negocio', 'Concepto', 'Valor']]
        
        analysis.append(f"🔝 **TOP {n} REGISTROS POR VALOR:**")
        analysis.append(top_registros.to_string())
        
        return "\n".join(analysis)
    
    def analisis_clientes(self):
        """Análisis específico de clientes"""
        if self.df is None:
            return "❌ No se pudieron cargar los datos del CSV"
        
        analysis = []
        
        # Filtrar datos de clientes
        clientes_data = self.df[self.df['Concepto'].str.contains('Cliente', case=False, na=False)]
        
        if not clientes_data.empty:
            # Análisis por país y negocio
            clientes_analysis = clientes_data.groupby(['Pais', 'Negocio'])['Valor'].sum().sort_values(ascending=False)
            analysis.append("👥 **ANÁLISIS DE CLIENTES POR PAÍS Y NEGOCIO:**")
            analysis.append(clientes_analysis.to_string())
            
            # Análisis por clasificación
            clasificacion_analysis = clientes_data.groupby('Clasificación')['Valor'].sum().sort_values(ascending=False)
            analysis.append(f"\n📋 **CLIENTES POR CLASIFICACIÓN:**\n{clasificacion_analysis.to_string()}")
            
            # Análisis por cohorte
            cohorte_analysis = clientes_data.groupby('Cohort_Act')['Valor'].sum().sort_values(ascending=False)
            analysis.append(f"\n📅 **CLIENTES POR COHORTE:**\n{cohorte_analysis.to_string()}")
        else:
            analysis.append("❌ No se encontraron datos de clientes")
        
        return "\n".join(analysis)
    
    def resumen_ejecutivo(self):
        """Resumen ejecutivo de los datos"""
        if self.df is None:
            return "❌ No se pudieron cargar los datos del CSV"
        
        analysis = []
        
        # Estadísticas clave
        total_valor = self.df['Valor'].sum()
        total_registros = len(self.df)
        valor_promedio = self.df['Valor'].mean()
        
        # País con mayor valor
        pais_top = self.df.groupby('Pais')['Valor'].sum().idxmax()
        valor_pais_top = self.df.groupby('Pais')['Valor'].sum().max()
        
        # Negocio con mayor valor
        negocio_top = self.df.groupby('Negocio')['Valor'].sum().idxmax()
        valor_negocio_top = self.df.groupby('Negocio')['Valor'].sum().max()
        
        # Concepto con mayor valor
        concepto_top = self.df.groupby('Concepto')['Valor'].sum().idxmax()
        valor_concepto_top = self.df.groupby('Concepto')['Valor'].sum().max()
        
        analysis.append("📈 **RESUMEN EJECUTIVO:**")
        analysis.append(f"💰 Valor total: ${total_valor:,.2f}")
        analysis.append(f"📊 Total de registros: {total_registros:,}")
        analysis.append(f"📊 Valor promedio: ${valor_promedio:,.2f}")
        analysis.append(f"🌍 País líder: {pais_top} (${valor_pais_top:,.2f})")
        analysis.append(f"🏢 Negocio líder: {negocio_top} (${valor_negocio_top:,.2f})")
        analysis.append(f"📊 Concepto líder: {concepto_top} (${valor_concepto_top:,.2f})")
        
        return "\n".join(analysis)

def main():
    """Función principal"""
    print("🤖 Analizador de Datos CSV Financieros")
    print("=" * 50)
    
    analizador = AnalizadorCSV()
    
    if len(sys.argv) > 1:
        comando = sys.argv[1].lower()
        
        if comando == "general":
            print(analizador.analisis_general())
        elif comando == "pais":
            print(analizador.analisis_pais())
        elif comando == "negocio":
            print(analizador.analisis_negocio())
        elif comando == "concepto":
            print(analizador.analisis_concepto())
        elif comando == "clientes":
            print(analizador.analisis_clientes())
        elif comando == "resumen":
            print(analizador.resumen_ejecutivo())
        elif comando == "top":
            n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            print(analizador.top_registros(n))
        else:
            print("❌ Comando no reconocido")
    else:
        print("📋 Comandos disponibles:")
        print("  general    - Análisis general de todos los datos")
        print("  pais       - Análisis detallado por país")
        print("  negocio    - Análisis detallado por negocio")
        print("  concepto   - Análisis detallado por concepto")
        print("  clientes   - Análisis específico de clientes")
        print("  resumen    - Resumen ejecutivo")
        print("  top [N]    - Top N registros por valor (ej: top 10)")
        print("\n💡 Uso: python3 analizador_csv.py [comando]")

if __name__ == "__main__":
    main()
