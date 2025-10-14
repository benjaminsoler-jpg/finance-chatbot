#!/usr/bin/env python3
"""
Configuración para Replit - Chatbot Financiero
"""

import os
import subprocess
import sys

def install_requirements():
    """Instalar dependencias necesarias"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements_streamlit.txt"])
        print("✅ Dependencias instaladas correctamente")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar dependencias: {e}")

def setup_environment():
    """Configurar variables de entorno"""
    print("🔧 Configurando variables de entorno...")
    
    # Verificar si OpenAI API Key está configurada
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ OPENAI_API_KEY no está configurada")
        print("Configúrala en Replit Secrets:")
        print("1. Ve a la pestaña 'Secrets' en Replit")
        print("2. Agrega: OPENAI_API_KEY = tu-api-key-aqui")
    else:
        print("✅ OPENAI_API_KEY configurada")

def main():
    print("🚀 Configurando Chatbot Financiero para Replit")
    print("=" * 50)
    
    # Instalar dependencias
    install_requirements()
    
    # Configurar entorno
    setup_environment()
    
    print("\n🎉 Configuración completada!")
    print("\nPara ejecutar:")
    print("1. Streamlit: streamlit run app.py")
    print("2. Gradio: python gradio_app.py")
    print("\n¡Tu chatbot está listo para usar!")

if __name__ == "__main__":
    main()
