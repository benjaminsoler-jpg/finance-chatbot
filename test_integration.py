#!/usr/bin/env python3
"""
Script para probar la integración completa del chatbot financiero con n8n
"""

import requests
import json
import time

def test_local_server():
    """Probar servidor local"""
    print("🔍 Probando servidor local...")
    try:
        response = requests.get("http://localhost:5000/health", timeout=10)
        if response.status_code == 200:
            print("✅ Servidor local funcionando")
            return True
        else:
            print(f"❌ Servidor local error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Servidor local error: {e}")
        return False

def test_tunnel():
    """Probar túnel localtunnel"""
    print("🔍 Probando túnel localtunnel...")
    try:
        response = requests.get("https://finance-chat.loca.lt/health", timeout=10)
        if response.status_code == 200:
            print("✅ Túnel funcionando")
            return True
        else:
            print(f"❌ Túnel error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Túnel error: {e}")
        return False

def test_chatbot_via_tunnel():
    """Probar chatbot a través del túnel"""
    print("🔍 Probando chatbot a través del túnel...")
    try:
        data = {"message": "Hola, ¿cómo estás?"}
        response = requests.post(
            "https://finance-chat.loca.lt/chat/simple",
            json=data,
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Chatbot funcionando a través del túnel")
                print(f"   Respuesta: {result['response'][:100]}...")
                return True
            else:
                print(f"❌ Chatbot error: {result.get('error')}")
                return False
        else:
            print(f"❌ Chatbot error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Chatbot error: {e}")
        return False

def test_n8n_webhook():
    """Probar webhook de n8n"""
    print("🔍 Probando webhook de n8n...")
    try:
        data = {"message": "¿Cuáles son las mejores estrategias de inversión?"}
        response = requests.post(
            "https://n8n.prd.mx.xepelin.tech/webhook/finance-chat",
            json=data,
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            print("✅ Webhook de n8n funcionando")
            print(f"   Respuesta: {result.get('message', 'No message')[:100]}...")
            return True
        else:
            print(f"❌ Webhook error: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de integración...")
    print("=" * 50)
    
    # Pruebas
    tests = [
        ("Servidor Local", test_local_server),
        ("Túnel Localtunnel", test_tunnel),
        ("Chatbot via Túnel", test_chatbot_via_tunnel),
        ("Webhook n8n", test_n8n_webhook)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n📋 {name}:")
        result = test_func()
        results.append((name, result))
        time.sleep(1)
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS:")
    print("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! La integración está funcionando.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
    
    print("\n🔗 URLs importantes:")
    print("   - Servidor local: http://localhost:5000")
    print("   - Túnel público: https://finance-chat.loca.lt")
    print("   - Webhook n8n: https://n8n.prd.mx.xepelin.tech/webhook/finance-chat")
    print("   - Workflow actualizado: n8n_complete_workflow.json")

if __name__ == "__main__":
    main()
