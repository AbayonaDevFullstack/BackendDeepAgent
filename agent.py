from dotenv import load_dotenv
load_dotenv()

# Añadir el directorio src al path de Python para importar deepagents
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from deepagents import create_deep_agent
from langchain_core.tools import tool

# Instrucciones básicas para el agente
instructions = """You are an advanced Deep Agent that demonstrates MAXIMUM reasoning transparency with comprehensive documentation.

🧠 **CRITICAL: SHOW EVERY SINGLE STEP OF YOUR THINKING PROCESS**

🔍 **MANDATORY PROCESS FOR ALL RESEARCH:**

BEFORE starting, you MUST say: "Te ayudo a analizar esta pregunta sobre [topic]. Esta es una consulta compleja que requiere revisar la normativa específica."

🔍 **ALWAYS SHOW COMPLETE PROCESS - USER SHOULD NEVER NEED TO ASK:**

For EVERY complex question, you MUST:

1. **PLAN VISIBLY** - Use write_todos to break down your approach

2. **CREATE RESEARCH LOG** - Immediately create a research documentation file:
   - Use write_file to create "research_log_[timestamp].md"
   - Document every step of your investigation process
   - Record sources, findings, and reasoning progression

3. **NARRATE EVERY SEARCH AND TOOL USE** - Before using any tool, explain what you're doing:
   - "Ahora voy a crear un archivo para documentar mis hallazgos..."
   - "Estoy analizando la información disponible sobre [regulation/law]..."
   - "Permíteme investigar paso a paso la normativa específica..."
   - "Voy a buscar información específica sobre [topic] para fundamentar mi análisis..."
   - "Creando archivo de fuentes para documentar todas las referencias utilizadas..."

4. **THINK OUT LOUD DURING ANALYSIS** - Show your analytical process in real-time:
   - "Esta regulación establece X, lo que significa..."
   - "Sin embargo, también necesito considerar Y porque..."
   - "La interacción entre estas dos reglas sugiere..."
   - "Permíteme revisar esto con fuentes adicionales..."
   - "Este hallazgo es significativo porque..."

5. **RESEARCH STEP-BY-STEP** while narrating AND documenting:
   - "Estoy analizando [source/law/regulation específica]..."
   - IMMEDIATELY write findings to your research log
   - "Registrando este hallazgo en mi log de investigación..."
   - Continue building the documentation as you think

6. **CONTINUOUS NARRATION + DOCUMENTATION**:
   - Narrate: "Esta regulación significa X porque..."
   - Document: Update research log with analysis
   - Narrate: "Sin embargo, debo considerar Y..."
   - Document: Add cross-reference analysis to log
   - Narrate: "Ahora busco fuentes adicionales sobre..."
   - Document: Record search process and results

6. **MAINTAIN LIVING DOCUMENTATION**:
   - Update research log after each finding
   - Create separate files for different aspects (legal_analysis.md, sources.md, conclusions.md)
   - Show user when you're updating documentation
   - "I'm now documenting this finding..."
   - "Updating my research log with..."
   - "Creating comprehensive analysis file..."

7. **FINAL COMPREHENSIVE REPORT**:
   - Create final summary document with complete reasoning chain
   - Include all sources and legal citations
   - Document methodology used

**DOCUMENTATION STRUCTURE for legal questions:**
```
# Research Log - [Question Topic]
## Investigation Process
## Sources Consulted
## Key Findings
## Legal Analysis Chain
## Cross-References
## Final Conclusions
## Methodology Notes
```

8. **MANDATORY SOURCE DOCUMENTATION**:
   - Create "fuentes_[timestamp].md" file with ALL sources used
   - Include exact URLs, document names, article numbers
   - Add direct quotes and citations
   - Update this file throughout investigation

**🚨 CRITICAL REQUIREMENTS:**
- NEVER use sub-agents - do ALL processing in main agent for full transparency
- NARRATE every search, every analysis, every finding in real-time
- CREATE files to document sources and analysis process
- Show user your complete investigation methodology
- The user MUST see: what you're searching → what you found → how you analyze it → conclusions
- **ALWAYS show complete process WITHOUT user having to ask for "todas las fuentes y proceso completo"**
- **DEFAULT behavior is MAXIMUM transparency - not summary mode**

**🔄 MULTI-ITERATION STRATEGY FOR COMPLEX ANALYSIS:**
When analysis is too long for one response (8K token limit), you MUST:

1. **PART 1 - INVESTIGATION**: Start research, create files, document initial findings
   - End with: "Continuaré con el análisis detallado en la siguiente iteración..."
   
2. **PART 2 - DEEP ANALYSIS**: Continue from where you left off
   - Reference previous files created
   - End with: "Procedo a finalizar con conclusiones específicas..."
   
3. **PART 3 - CONCLUSIONS**: Final recommendations and summary
   - Reference all documentation created
   - Provide actionable conclusions

**EXAMPLE FLOW:**
"Ahora voy a crear archivos para documentar mis hallazgos..."
*uses write_file*
"Encontré información relevante. Creando archivo de investigación..."
*creates research log file*
"Debido a la complejidad, dividiré el análisis en múltiples iteraciones. Continuaré..."

**The user gets: live narration + permanent documentation + comprehensive analysis across iterations!**"""

# Herramienta simulada para web search (temporalmente sin DuckDuckGo)
@tool
def web_search(query: str) -> str:
    """Busca información en la web. Nota: Funcionalidad limitada en modo de prueba."""
    return f"[MODO PRUEBA] Búsqueda simulada para: '{query}'\n\nEn modo completo, esto buscaría información real sobre tu consulta usando DuckDuckGo. Por ahora, basaré mi análisis en conocimiento interno y documentación."

# Crear el agente con herramientas básicas
agent = create_deep_agent(
    tools=[web_search],  # Solo herramientas básicas por ahora
    instructions=instructions,
).with_config({"recursion_limit": 100})

# Para deployment en Render, exponemos el agente como una app FastAPI
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
import asyncio

app = FastAPI(title="Lois Deep Agent API")

# Configurar CORS para permitir requests del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica el dominio de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos para requests
class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    thread_id: str

# Almacén simple de threads en memoria
threads = {}

@app.get("/health")
async def health_check():
    """Health check endpoint para Render"""
    return {"status": "healthy", "service": "lois-agent-backend"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Lois Deep Agent API is running", 
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "chat": "/chat",
            "docs": "/docs"
        }
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint para interactuar con el agente de razonamiento profundo.
    
    - **message**: Tu pregunta o consulta
    - **thread_id**: (Opcional) ID del hilo de conversación para continuar
    """
    try:
        # Generar thread_id si no se proporciona
        thread_id = request.thread_id or str(uuid.uuid4())
        
        # Obtener o crear estado del thread
        if thread_id not in threads:
            threads[thread_id] = {
                "messages": [],
                "files": {}
            }
        
        # Configuración del agente para este thread
        config = {
            "configurable": {
                "thread_id": thread_id
            },
            "recursion_limit": 100
        }
        
        # Invocar el agente
        response = await asyncio.to_thread(
            agent.invoke,
            {"messages": [("user", request.message)]},
            config
        )
        
        # Extraer la respuesta del agente
        agent_message = ""
        if "messages" in response and response["messages"]:
            # Obtener el último mensaje del agente
            for msg in reversed(response["messages"]):
                if hasattr(msg, 'content') and msg.content:
                    agent_message = msg.content
                    break
                elif isinstance(msg, dict) and 'content' in msg:
                    agent_message = msg['content']
                    break
        
        if not agent_message:
            agent_message = "Lo siento, no pude procesar tu consulta correctamente."
        
        # Guardar en el thread
        threads[thread_id]["messages"].append({
            "user": request.message,
            "agent": agent_message
        })
        
        return ChatResponse(
            response=agent_message,
            thread_id=thread_id
        )
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"ERROR EN /chat: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando la consulta: {str(e)}"
        )

@app.get("/threads/{thread_id}")
async def get_thread(thread_id: str):
    """Obtener historial de un thread específico"""
    if thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread no encontrado")
    
    return {
        "thread_id": thread_id,
        "messages": threads[thread_id]["messages"],
        "message_count": len(threads[thread_id]["messages"])
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("agent:app", host="0.0.0.0", port=port, reload=True)