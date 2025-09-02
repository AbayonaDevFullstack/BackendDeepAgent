#!/usr/bin/env python3
"""
Startup script para Render deployment
Este script inicializa el servidor LangGraph API para el agente Lois
"""
import os
import sys
from agent import agent

def main():
    """Función principal para inicializar el servidor"""
    # Configurar variables de entorno por defecto
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    os.environ.setdefault("LANGCHAIN_PROJECT", "deepagents")
    
    # Verificar que las variables críticas estén configuradas
    required_vars = ["ANTHROPIC_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ ERROR: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your Render service configuration.")
        sys.exit(1)
    
    print("✅ Environment variables configured successfully")
    print(f"📊 LangSmith tracing: {os.getenv('LANGCHAIN_TRACING_V2', 'false')}")
    print(f"📁 LangChain project: {os.getenv('LANGCHAIN_PROJECT', 'default')}")
    print("🚀 Starting Lois Deep Agent...")
    
    # El agente ya está configurado en agent.py
    print("✅ Agent initialized successfully")
    
    return agent

if __name__ == "__main__":
    agent = main()
    print("🎯 Agent ready for deployment!")