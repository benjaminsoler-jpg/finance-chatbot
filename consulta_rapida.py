#!/usr/bin/env python3
"""
Script simple para hacer consultas rápidas al chatbot financiero
"""

import requests
import json
import sys

def consultar_chatbot(pregunta):
    """Hacer una consulta al chatbot"""
    try:
        url = "https://finance-chat.loca.lt/chat/simple"
        data = {"message": pregunta}
        
        print(f"🤔 Consultando: {pregunta}")
        print("⏳ Procesando...")
        
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"\n🤖 Respuesta:\n{result['response']}")
                return True
            else:
                print(f"❌ Error: {result.get('error', 'Error desconocido')}")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False

def main():
    """Función principal"""
    print("🤖 Chatbot Financiero - Consulta Rápida")
    print("=" * 50)
    
    # Si se proporciona una pregunta como argumento
    if len(sys.argv) > 1:
        pregunta = " ".join(sys.argv[1:])
        consultar_chatbot(pregunta)
    else:
        # Preguntas de ejemplo
        preguntas_ejemplo = [
            "¿Cuáles son las mejores estrategias de inversión para principiantes?",
            "¿Cómo crear un presupuesto personal efectivo?",
            "¿Qué es la diversificación en inversiones?",
            "¿Cómo ahorrar dinero de manera inteligente?",
            "¿Qué son los fondos indexados?"
        ]
        
        print("📋 Preguntas de ejemplo:")
        for i, pregunta in enumerate(preguntas_ejemplo, 1):
            print(f"{i}. {pregunta}")
        
        print(f"\n💡 Uso: python3 consulta_rapida.py 'Tu pregunta aquí'")
        print("💡 Ejemplo: python3 consulta_rapida.py '¿Cómo invertir en la bolsa?'")

if __name__ == "__main__":
    main()
