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
try:
    agent = create_deep_agent(
        tools=[web_search],  # Solo herramientas básicas por ahora
        instructions=instructions,
    ).with_config({"recursion_limit": 100})
    print("Agente creado exitosamente")
except Exception as e:
    print(f"Error creando agente: {e}")
    # Crear agente simplificado como fallback
    from langchain_anthropic import ChatAnthropic
    from langchain.schema import HumanMessage, AIMessage
    
    class SimpleAgent:
        def __init__(self):
            self.model = ChatAnthropic(
                model_name="claude-3-5-haiku-20241022",
                max_tokens=8192,
                temperature=0.3
            )
        
        def invoke(self, input_data, config=None):
            messages = input_data.get("messages", [])
            if messages:
                # Tomar el último mensaje del usuario
                user_message = messages[-1][1] if len(messages) > 0 else ""
                
                # Generar respuesta usando Claude directamente
                response = self.model.invoke([HumanMessage(content=f"{instructions}\n\nUser: {user_message}")])
                
                return {
                    "messages": [
                        HumanMessage(content=user_message),
                        AIMessage(content=response.content)
                    ],
                    "todos": [
                        {
                            "content": "Análisis completado",
                            "status": "completed",
                            "activeForm": "Completando análisis"
                        }
                    ],
                    "files": {}
                }
            return {"messages": [], "todos": [], "files": {}}
    
    agent = SimpleAgent()
    print("Agente simplificado creado como fallback")

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

# Modelos para requests y responses compatibles con LangGraph API
from datetime import datetime

class Message(BaseModel):
    id: str
    type: str  # "human" | "ai" | "tool"
    content: str
    timestamp: str
    tool_calls: Optional[list] = None
    tool_call_id: Optional[str] = None

class TodoItem(BaseModel):
    content: str
    status: str  # "pending" | "in_progress" | "completed"
    activeForm: str

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None

class ChatResponse(BaseModel):
    messages: list[Message]
    todos: list[TodoItem]
    files: dict[str, str]
    thread_id: str
    metadata: dict

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
    Compatible con LangGraph API format.
    
    - **message**: Tu pregunta o consulta
    - **thread_id**: (Opcional) ID del hilo de conversación para continuar
    """
    start_time = datetime.utcnow()
    
    try:
        # Generar thread_id si no se proporciona
        thread_id = request.thread_id or str(uuid.uuid4())
        
        # Obtener o crear estado del thread
        if thread_id not in threads:
            threads[thread_id] = {
                "messages": [],
                "files": {},
                "todos": []
            }
        
        # Crear mensaje del usuario
        user_message = Message(
            id=str(uuid.uuid4()),
            type="human",
            content=request.message,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
        # Agregar mensaje del usuario al thread
        threads[thread_id]["messages"].append(user_message)
        
        # Configuración del agente para este thread
        config = {
            "configurable": {
                "thread_id": thread_id
            },
            "recursion_limit": 100
        }
        
        # Invocar el agente con mejor manejo de errores
        try:
            agent_response = await asyncio.to_thread(
                agent.invoke,
                {"messages": [("user", request.message)]},
                config
            )
            print(f"Agent response keys: {list(agent_response.keys()) if isinstance(agent_response, dict) else 'Not a dict'}")
            print(f"Agent response type: {type(agent_response)}")
        except Exception as agent_error:
            print(f"Error específico del agente: {agent_error}")
            print(f"Tipo de error: {type(agent_error)}")
            
            # Crear respuesta por defecto si el agente falla
            agent_response = {
                "messages": [],
                "todos": [],
                "files": {}
            }
        
        # Extraer datos del agente response
        agent_messages = []
        todos_list = []
        files_dict = {}
        tools_used = []
        
        # Procesar mensajes del agente de forma más segura
        if "messages" in agent_response and agent_response["messages"]:
            try:
                for msg in agent_response["messages"]:
                    try:
                        # Determinar tipo de mensaje de forma más segura
                        msg_type = "ai"  # Por defecto
                        content = ""
                        tool_calls = None
                        tool_call_id = None
                        
                        if hasattr(msg, 'content'):
                            # Si el contenido es una lista (tool calls + texto)
                            if isinstance(msg.content, list):
                                text_parts = []
                                tool_parts = []
                                
                                for part in msg.content:
                                    if isinstance(part, dict):
                                        if part.get('type') == 'text':
                                            text_parts.append(part.get('text', ''))
                                        elif part.get('type') == 'tool_use':
                                            tool_parts.append({
                                                'id': part.get('id'),
                                                'name': part.get('name'),
                                                'input': part.get('input')
                                            })
                                
                                content = ' '.join(text_parts)
                                if tool_parts:
                                    tool_calls = tool_parts
                            else:
                                content = str(msg.content)
                        else:
                            content = str(msg)
                            
                        if hasattr(msg, '__class__'):
                            class_name = msg.__class__.__name__.lower()
                            if "human" in class_name:
                                msg_type = "human"
                            elif "tool" in class_name:
                                msg_type = "tool"
                                tools_used.append("tool_call")
                        
                        # Skip el mensaje del usuario (ya lo agregamos)
                        if msg_type == "human":
                            continue
                            
                        message_obj = Message(
                            id=getattr(msg, 'id', str(uuid.uuid4())),
                            type=msg_type,
                            content=content,
                            timestamp=datetime.utcnow().isoformat() + "Z",
                            tool_calls=tool_calls,
                            tool_call_id=tool_call_id
                        )
                        agent_messages.append(message_obj)
                    except Exception as msg_error:
                        print(f"Error procesando mensaje individual: {msg_error}")
                        continue
            except Exception as messages_error:
                print(f"Error procesando lista de mensajes: {messages_error}")
        
        # Extraer TODOs si están disponibles
        if "todos" in agent_response:
            for todo in agent_response["todos"]:
                if isinstance(todo, dict):
                    todo_obj = TodoItem(
                        content=todo.get("content", ""),
                        status=todo.get("status", "completed"),
                        activeForm=todo.get("activeForm", todo.get("content", ""))
                    )
                    todos_list.append(todo_obj)
                    tools_used.append("write_todos")
        
        # Extraer archivos si están disponibles
        if "files" in agent_response:
            files_dict = agent_response["files"]
            if files_dict:
                tools_used.append("write_file")
        
        # Si no hay mensajes del agente, crear uno por defecto
        if not agent_messages:
            default_message = Message(
                id=str(uuid.uuid4()),
                type="ai", 
                content="Lo siento, no pude procesar tu consulta correctamente.",
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
            agent_messages.append(default_message)
        
        # Agregar mensajes del agente al thread
        threads[thread_id]["messages"].extend(agent_messages)
        threads[thread_id]["files"].update(files_dict)
        threads[thread_id]["todos"] = todos_list
        
        # Calcular metadata
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Estimar tokens (aproximación)
        total_content = request.message + "".join([msg.content for msg in agent_messages])
        estimated_tokens = len(total_content.split()) * 1.3  # Aproximación
        
        metadata = {
            "model_used": "claude-3-5-haiku-20241022",
            "estimated_tokens": int(estimated_tokens),
            "processing_time_seconds": round(processing_time, 2),
            "tools_used": list(set(tools_used)) if tools_used else [],
            "message_count": len(threads[thread_id]["messages"]),
            "files_count": len(files_dict),
            "todos_count": len(todos_list)
        }
        
        # Combinar todos los mensajes para la respuesta
        all_messages = threads[thread_id]["messages"]
        
        return ChatResponse(
            messages=all_messages,
            todos=todos_list,
            files=files_dict,
            thread_id=thread_id,
            metadata=metadata
        )
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"ERROR EN /chat: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando la consulta: {str(e)}"
        )

# Modelo para búsqueda de threads
class ThreadSearchRequest(BaseModel):
    limit: int = 30
    offset: int = 0
    sort_by: str = "created_at"
    sort_order: str = "desc"

@app.get("/threads/search")
async def search_threads_get(limit: int = 30, sortBy: str = "created_at", sortOrder: str = "desc"):
    """Buscar threads - GET Compatible con LangGraph API"""
    return await search_threads_logic(limit, 0, sortBy, sortOrder)

@app.post("/threads/search")
async def search_threads_post(request: ThreadSearchRequest):
    """Buscar threads - POST Compatible con LangGraph API"""
    return await search_threads_logic(request.limit, request.offset, request.sort_by, request.sort_order)

async def search_threads_logic(limit: int, offset: int, sort_by: str, sort_order: str):
    """Lógica común para búsqueda de threads"""
    try:
        # Convertir threads a lista para poder ordenar
        thread_list = []
        for thread_id, thread_data in threads.items():
            messages = thread_data.get("messages", [])
            created_at = messages[0].timestamp if messages else datetime.utcnow().isoformat() + "Z"
            
            thread_list.append({
                "thread_id": thread_id,
                "created_at": created_at,
                "values": {
                    "messages": messages,
                    "todos": thread_data.get("todos", []),
                    "files": thread_data.get("files", {})
                },
                "metadata": {
                    "message_count": len(messages),
                    "files_count": len(thread_data.get("files", {})),
                    "todos_count": len(thread_data.get("todos", []))
                }
            })
        
        # Ordenar por fecha
        if sort_by == "created_at":
            thread_list.sort(
                key=lambda x: x["created_at"], 
                reverse=(sort_order == "desc")
            )
        
        # Aplicar offset y limit
        start_index = offset
        end_index = offset + limit
        return thread_list[start_index:end_index]
        
    except Exception as e:
        print(f"Error en /threads/search: {e}")
        return []

@app.get("/threads/{thread_id}")
async def get_thread(thread_id: str):
    """Obtener historial de un thread específico - Compatible con LangGraph API"""
    if thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread no encontrado")
    
    thread_data = threads[thread_id]
    
    return {
        "messages": thread_data.get("messages", []),
        "todos": thread_data.get("todos", []),
        "files": thread_data.get("files", {}),
        "thread_id": thread_id,
        "metadata": {
            "message_count": len(thread_data.get("messages", [])),
            "files_count": len(thread_data.get("files", {})),
            "todos_count": len(thread_data.get("todos", [])),
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
    }

# Endpoint adicional para compatibilidad completa con LangGraph API
@app.post("/threads")
async def create_thread():
    """Crear un nuevo thread - Compatible con LangGraph API"""
    thread_id = str(uuid.uuid4())
    threads[thread_id] = {
        "messages": [],
        "files": {},
        "todos": []
    }
    
    return {
        "thread_id": thread_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "metadata": {}
    }

# Modelo para historial de thread
class ThreadHistoryRequest(BaseModel):
    limit: int = 1000

@app.post("/threads/{thread_id}/history")
async def get_thread_history(thread_id: str, request: ThreadHistoryRequest):
    """Obtener historial de un thread - Compatible con LangGraph API"""
    if thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread no encontrado")
    
    thread_data = threads[thread_id]
    messages = thread_data.get("messages", [])
    
    # Limitar mensajes según el request
    limited_messages = messages[-request.limit:] if request.limit < len(messages) else messages
    
    return {
        "values": {
            "messages": limited_messages,
            "todos": thread_data.get("todos", []),
            "files": thread_data.get("files", {})
        },
        "metadata": {
            "message_count": len(limited_messages),
            "files_count": len(thread_data.get("files", {})),
            "todos_count": len(thread_data.get("todos", []))
        },
        "thread_id": thread_id
    }

@app.get("/threads/{thread_id}/state")
async def get_thread_state(thread_id: str):
    """Obtener estado actual de un thread - Compatible con LangGraph API"""
    if thread_id not in threads:
        raise HTTPException(status_code=404, detail="Thread no encontrado")
    
    thread_data = threads[thread_id]
    
    return {
        "values": {
            "messages": thread_data.get("messages", []),
            "todos": thread_data.get("todos", []),
            "files": thread_data.get("files", {})
        },
        "next": [],  # Para compatibilidad con LangGraph
        "metadata": {
            "message_count": len(thread_data.get("messages", [])),
            "files_count": len(thread_data.get("files", {})),
            "todos_count": len(thread_data.get("todos", []))
        },
        "created_at": thread_data.get("messages", [{}])[0].get("timestamp") if thread_data.get("messages") else datetime.utcnow().isoformat() + "Z",
        "thread_id": thread_id
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("agent:app", host="0.0.0.0", port=port, reload=True)