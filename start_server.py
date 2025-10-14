#!/usr/bin/env python3
"""
Script para iniciar el servidor API del chatbot financiero
"""

import subprocess
import sys
import time
import requests
from colorama import init, Fore

init(autoreset=True)

def check_dependencies():
    """Verificar que las dependencias estén instaladas"""
    try:
        import flask
        import flask_cors
        import openai
        import requests
        import colorama
        from dotenv import load_dotenv
        print(f"{Fore.GREEN}✅ Todas las dependencias están instaladas")
        return True
    except ImportError as e:
        print(f"{Fore.RED}❌ Dependencia faltante: {e}")
        print(f"{Fore.YELLOW}Ejecuta: pip3 install -r requirements.txt")
        return False

def check_config():
    """Verificar configuración"""
    try:
        from dotenv import load_dotenv
        load_dotenv("config.env")
        
        import os
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key or api_key == "your_openai_api_key_here":
            print(f"{Fore.RED}❌ OPENAI_API_KEY no está configurada")
            print(f"{Fore.YELLOW}Edita config.env y configura tu API key")
            return False
        
        print(f"{Fore.GREEN}✅ Configuración válida")
        return True
    except Exception as e:
        print(f"{Fore.RED}❌ Error en configuración: {e}")
        return False

def start_server():
    """Iniciar el servidor API"""
    try:
        print(f"{Fore.CYAN}🚀 Iniciando servidor API...")
        print(f"{Fore.YELLOW}Presiona Ctrl+C para detener el servidor")
        print(f"{Fore.CYAN}{'='*50}")
        
        # Iniciar servidor
        subprocess.run([sys.executable, "api_server.py"])
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Servidor detenido")
    except Exception as e:
        print(f"{Fore.RED}❌ Error al iniciar servidor: {e}")

def main():
    """Función principal"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}{'FINANCE CHATBOT API SERVER'}")
    print(f"{Fore.CYAN}{'='*60}")
    
    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)
    
    # Verificar configuración
    if not check_config():
        sys.exit(1)
    
    # Iniciar servidor
    start_server()

if __name__ == "__main__":
    main()
