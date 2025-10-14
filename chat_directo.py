#!/usr/bin/env python3
"""
Script para usar el chatbot financiero directamente via API
"""

import requests
import json
import sys

def chat_with_bot(message):
    """Enviar mensaje al chatbot y obtener respuesta"""
    try:
        url = "https://finance-chat.loca.lt/chat/simple"
        data = {"message": message}
        
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return result["response"]
            else:
                return f"Error: {result.get('error', 'Error desconocido')}"
        else:
            return f"Error HTTP: {response.status_code}"
            
    except Exception as e:
        return f"Error de conexión: {str(e)}"

def main():
    """Función principal"""
    print("🤖 Chatbot Financiero - Modo Directo")
    print("=" * 50)
    print("Escribe tu consulta financiera (o 'salir' para terminar)")
    print("=" * 50)
    
    while True:
        try:
            # Obtener input del usuario
            user_input = input("\n💬 Tú: ").strip()
            
            # Verificar si quiere salir
            if user_input.lower() in ['salir', 'exit', 'quit', 'q']:
                print("\n👋 ¡Hasta luego!")
                break
            
            # Verificar que no esté vacío
            if not user_input:
                print("⚠️  Por favor, escribe una consulta.")
                continue
            
            # Obtener respuesta del chatbot
            print("🤔 Procesando...")
            response = chat_with_bot(user_input)
            
            # Mostrar respuesta
            print(f"\n🤖 Asistente: {response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()
