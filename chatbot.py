#!/usr/bin/env python3
"""
Chatbot financiero con OpenAI - Versión corregida
Configuración desde archivo .env
"""

import os
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv
import openai
from colorama import init, Fore, Style, Back

# Inicializar colorama para colores en terminal
init(autoreset=True)

class FinanceChatbot:
    def __init__(self, env_file: str = "config.env"):
        """Inicializar el chatbot con configuración desde archivo .env"""
        self.load_config(env_file)
        self.setup_openai()
        self.conversation_history: List[Dict[str, str]] = []
        
    def load_config(self, env_file: str):
        """Cargar configuración desde archivo .env"""
        if not os.path.exists(env_file):
            print(f"{Fore.RED}Error: No se encontró el archivo {env_file}")
            print(f"{Fore.YELLOW}Por favor, crea el archivo {env_file} con tu configuración de OpenAI")
            sys.exit(1)
            
        load_dotenv(env_file)
        
        # Cargar variables de entorno
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
        self.system_prompt = os.getenv("SYSTEM_PROMPT", "Eres un asistente financiero experto.")
        
        # Validar configuración
        if not self.api_key or self.api_key == "your_openai_api_key_here":
            print(f"{Fore.RED}Error: OPENAI_API_KEY no está configurada correctamente")
            print(f"{Fore.YELLOW}Por favor, configura tu API key en {env_file}")
            sys.exit(1)
    
    def setup_openai(self):
        """Configurar cliente de OpenAI"""
        # Configurar API key globalmente
        openai.api_key = self.api_key
        
        # Crear cliente con configuración básica
        try:
            self.client = openai.OpenAI(api_key=self.api_key)
        except Exception as e:
            print(f"{Fore.YELLOW}Advertencia: No se pudo crear cliente OpenAI: {e}")
            self.client = None
    
    def get_chat_response(self, user_message: str) -> str:
        """Obtener respuesta del chatbot"""
        try:
            # Agregar mensaje del usuario al historial
            self.conversation_history.append({"role": "user", "content": user_message})
            
            # Preparar mensajes para la API
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(self.conversation_history)
            
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
                import requests
                import json
                
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
            self.conversation_history.append({"role": "assistant", "content": bot_response})
            
            return bot_response
            
        except Exception as e:
            error_msg = f"Error al comunicarse con OpenAI: {str(e)}"
            print(f"{Fore.RED}{error_msg}")
            return error_msg
    
    def print_welcome(self):
        """Mostrar mensaje de bienvenida"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}{'CHATBOT FINANCIERO - OPENAI'}")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.GREEN}Modelo: {self.model}")
        print(f"{Fore.GREEN}Temperatura: {self.temperature}")
        print(f"{Fore.GREEN}Max tokens: {self.max_tokens}")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.YELLOW}Escribe 'salir', 'quit' o 'exit' para terminar")
        print(f"{Fore.YELLOW}Escribe 'limpiar' o 'clear' para limpiar el historial")
        print(f"{Fore.YELLOW}Escribe 'config' para ver la configuración actual")
        print(f"{Fore.CYAN}{'='*60}\n")
    
    def print_config(self):
        """Mostrar configuración actual"""
        print(f"\n{Fore.CYAN}--- CONFIGURACIÓN ACTUAL ---")
        print(f"{Fore.GREEN}Modelo: {self.model}")
        print(f"{Fore.GREEN}Temperatura: {self.temperature}")
        print(f"{Fore.GREEN}Max tokens: {self.max_tokens}")
        print(f"{Fore.GREEN}Mensajes en historial: {len(self.conversation_history)}")
        print(f"{Fore.CYAN}--- FIN CONFIGURACIÓN ---\n")
    
    def clear_history(self):
        """Limpiar historial de conversación"""
        self.conversation_history = []
        print(f"{Fore.GREEN}Historial de conversación limpiado.\n")
    
    def run(self):
        """Ejecutar el chatbot en modo interactivo"""
        self.print_welcome()
        
        while True:
            try:
                # Obtener entrada del usuario
                user_input = input(f"{Fore.BLUE}Tú: {Style.RESET_ALL}").strip()
                
                # Comandos especiales
                if user_input.lower() in ['salir', 'quit', 'exit']:
                    print(f"{Fore.YELLOW}¡Hasta luego! 👋")
                    break
                elif user_input.lower() in ['limpiar', 'clear']:
                    self.clear_history()
                    continue
                elif user_input.lower() == 'config':
                    self.print_config()
                    continue
                elif not user_input:
                    continue
                
                # Mostrar indicador de procesamiento
                print(f"{Fore.YELLOW}Procesando...")
                
                # Obtener respuesta del bot
                bot_response = self.get_chat_response(user_input)
                
                # Mostrar respuesta del bot
                print(f"\n{Fore.GREEN}Bot: {Style.RESET_ALL}{bot_response}\n")
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}¡Hasta luego! 👋")
                break
            except Exception as e:
                print(f"{Fore.RED}Error inesperado: {str(e)}")
                print(f"{Fore.YELLOW}Continuando...\n")

def main():
    """Función principal"""
    try:
        chatbot = FinanceChatbot()
        chatbot.run()
    except Exception as e:
        print(f"{Fore.RED}Error al inicializar el chatbot: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
