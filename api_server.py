#!/usr/bin/env python3
"""
API REST para el chatbot financiero
Integración con n8n AI Agent
"""

import os
import sys
import json
from typing import Dict, Any, List
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import requests
from colorama import init, Fore

# Inicializar colorama
init(autoreset=True)

# Cargar configuración
load_dotenv("config.env")

app = Flask(__name__)
CORS(app)  # Permitir CORS para n8n

class FinanceChatbotAPI:
    def __init__(self):
        """Inicializar el chatbot API"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
        self.system_prompt = os.getenv("SYSTEM_PROMPT", "Eres un asistente financiero experto.")
        
        # Configurar OpenAI
        openai.api_key = self.api_key
        try:
            self.client = openai.OpenAI(api_key=self.api_key)
        except Exception as e:
            print(f"{Fore.YELLOW}Advertencia: No se pudo crear cliente OpenAI: {e}")
            self.client = None
    
    def get_chat_response(self, user_message: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Obtener respuesta del chatbot"""
        try:
            # Preparar historial de conversación
            if conversation_history is None:
                conversation_history = []
            
            # Agregar mensaje del usuario
            conversation_history.append({"role": "user", "content": user_message})
            
            # Preparar mensajes para la API
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(conversation_history)
            
            # Llamar a la API de OpenAI
            if self.client:
                # Usar cliente de OpenAI (v1.0+)
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                bot_response = response.choices[0].message.content
            else:
                # Usar requests directamente como fallback
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens
                }
                
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    bot_response = result["choices"][0]["message"]["content"]
                else:
                    raise Exception(f"API Error: {response.status_code} - {response.text}")
            
            # Agregar respuesta del bot al historial
            conversation_history.append({"role": "assistant", "content": bot_response})
            
            return {
                "success": True,
                "response": bot_response,
                "conversation_history": conversation_history,
                "model": self.model,
                "temperature": self.temperature
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": f"Error al procesar la consulta: {str(e)}"
            }

# Inicializar chatbot
chatbot = FinanceChatbotAPI()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Finance Chatbot API",
        "model": chatbot.model,
        "temperature": chatbot.temperature
    })

@app.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint principal para chat
    Formato esperado por n8n:
    {
        "message": "Tu consulta aquí",
        "conversation_history": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No se proporcionó JSON válido"
            }), 400
        
        message = data.get('message', '')
        conversation_history = data.get('conversation_history', [])
        
        if not message:
            return jsonify({
                "success": False,
                "error": "El campo 'message' es requerido"
            }), 400
        
        # Obtener respuesta del chatbot
        result = chatbot.get_chat_response(message, conversation_history)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error interno del servidor: {str(e)}"
        }), 500

@app.route('/chat/simple', methods=['POST'])
def chat_simple():
    """
    Endpoint simplificado para n8n
    Solo requiere el mensaje, sin historial
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "El campo 'message' es requerido"
            }), 400
        
        message = data['message']
        
        # Obtener respuesta del chatbot
        result = chatbot.get_chat_response(message)
        
        # Formato simplificado para n8n
        return jsonify({
            "success": result["success"],
            "response": result["response"],
            "error": result.get("error")
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error interno del servidor: {str(e)}"
        }), 500

@app.route('/config', methods=['GET'])
def get_config():
    """Obtener configuración actual"""
    return jsonify({
        "model": chatbot.model,
        "temperature": chatbot.temperature,
        "max_tokens": chatbot.max_tokens,
        "system_prompt": chatbot.system_prompt[:100] + "..." if len(chatbot.system_prompt) > 100 else chatbot.system_prompt
    })

@app.route('/config', methods=['POST'])
def update_config():
    """Actualizar configuración"""
    try:
        data = request.get_json()
        
        if 'temperature' in data:
            chatbot.temperature = float(data['temperature'])
        if 'max_tokens' in data:
            chatbot.max_tokens = int(data['max_tokens'])
        if 'model' in data:
            chatbot.model = data['model']
        if 'system_prompt' in data:
            chatbot.system_prompt = data['system_prompt']
        
        return jsonify({
            "success": True,
            "message": "Configuración actualizada",
            "config": {
                "model": chatbot.model,
                "temperature": chatbot.temperature,
                "max_tokens": chatbot.max_tokens
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error al actualizar configuración: {str(e)}"
        }), 500

if __name__ == '__main__':
    print(f"{Fore.CYAN}🚀 Iniciando Finance Chatbot API...")
    print(f"{Fore.GREEN}Modelo: {chatbot.model}")
    print(f"{Fore.GREEN}Temperatura: {chatbot.temperature}")
    print(f"{Fore.CYAN}Endpoints disponibles:")
    print(f"{Fore.YELLOW}  GET  /health - Health check")
    print(f"{Fore.YELLOW}  POST /chat - Chat completo con historial")
    print(f"{Fore.YELLOW}  POST /chat/simple - Chat simplificado")
    print(f"{Fore.YELLOW}  GET  /config - Obtener configuración")
    print(f"{Fore.YELLOW}  POST /config - Actualizar configuración")
    print(f"{Fore.CYAN}Servidor ejecutándose en: http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
