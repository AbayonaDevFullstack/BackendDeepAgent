from dotenv import load_dotenv
load_dotenv()

# Añadir el directorio src al path de Python para importar deepagents
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from deepagents import create_deep_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

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

# Herramientas para el agente
@tool
def web_search(query: str) -> str:
    """Busca información en la web. Nota: Funcionalidad limitada en modo de prueba."""
    return f"[MODO PRUEBA] Búsqueda simulada para: '{query}'\n\nEn modo completo, esto buscaría información real sobre tu consulta usando DuckDuckGo. Por ahora, basaré mi análisis en conocimiento interno y documentación específica."

@tool
def write_file(file_path: str, content: str) -> str:
    """Escribe contenido a un archivo. Útil para documentar investigaciones y análisis."""
    try:
        import os
        # Asegurar que el directorio existe
        os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else '.', exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"✅ Archivo '{file_path}' creado exitosamente con {len(content)} caracteres."
    except Exception as e:
        return f"❌ Error creando archivo '{file_path}': {str(e)}"

@tool  
def write_todos(todos: str) -> str:
    """Actualiza la lista de tareas pendientes para mostrar progreso al usuario."""
    # Esta herramienta simula la actualización de todos para el loud thinking
    return f"📋 Lista de tareas actualizada: {todos}"

@tool
def read_file(file_path: str) -> str:
    """Lee el contenido de un archivo existente."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"📖 Contenido del archivo '{file_path}':\n\n{content}"
    except FileNotFoundError:
        return f"❌ Archivo '{file_path}' no encontrado."
    except Exception as e:
        return f"❌ Error leyendo archivo '{file_path}': {str(e)}"

# Crear el agente con herramientas básicas
try:
    agent = create_deep_agent(
        tools=[web_search, write_file, write_todos, read_file],
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
            # Diccionario de herramientas disponibles
            self.tools = {
                'web_search': web_search,
                'write_file': write_file,
                'write_todos': write_todos,
                'read_file': read_file
            }
        
        def invoke(self, input_data, config=None):
            messages = input_data.get("messages", [])
            if messages:
                # Tomar el último mensaje del usuario
                user_message = messages[-1][1] if len(messages) > 0 else ""
                
                # Crear un prompt que incluya las herramientas disponibles
                tools_description = f"""

🔧 HERRAMIENTAS DISPONIBLES (NO uses otras):
1. web_search(query): Busca información específica en la web
2. write_file(file_path, content): Crea un archivo nuevo con contenido específico
3. write_todos(todos): Actualiza/crea lista de tareas (formato texto libre)
4. read_file(file_path): Lee contenido de un archivo existente

⚠️ FORMATO OBLIGATORIO para tool calls:
TOOL_CALL: nombre_herramienta
PARAMS: {{"parametro": "valor"}}

✅ EJEMPLOS CORRECTOS:
TOOL_CALL: web_search
PARAMS: {{"query": "límites gastos representación Colombia"}}

TOOL_CALL: write_file
PARAMS: {{"file_path": "investigacion_gastos.md", "content": "# Investigación\\n\\nContenido aquí"}}

TOOL_CALL: write_todos
PARAMS: {{"todos": "1. Investigar normativa\\n2. Documentar hallazgos\\n3. Crear reporte final"}}

❌ NO USES herramientas inexistentes como edit_file, update_file, etc.

IMPORTANTE: Debes EJECUTAR herramientas reales para investigar, documentar y generar archivos."""

                # Generar respuesta inicial
                initial_response = self.model.invoke([HumanMessage(content=f"{instructions}\n{tools_description}\n\nUser: {user_message}")])
                
                # Procesar la respuesta para detectar y ejecutar herramientas
                response_text = initial_response.content
                
                # Buscar llamadas a herramientas en la respuesta
                import re
                tool_pattern = r'TOOL_CALL:\s*(\w+)\s*\nPARAMS:\s*(\{[^}]*\})'
                tool_matches = re.findall(tool_pattern, response_text, re.MULTILINE)
                
                # Ejecutar herramientas encontradas
                print(f"🔍 Tool matches found: {tool_matches}")
                
                for tool_name, params_str in tool_matches:
                    print(f"🔧 Processing tool: {tool_name} with params: {params_str}")
                    
                    if tool_name in self.tools:
                        try:
                            import json
                            params = json.loads(params_str)
                            print(f"✅ Executing {tool_name} with {params}")
                            tool_result = self.tools[tool_name](**params)
                            print(f"✅ Tool result: {tool_result}")
                            
                            # Reemplazar la llamada a herramienta con el resultado
                            old_call = f"TOOL_CALL: {tool_name}\nPARAMS: {params_str}"
                            new_call = f"🔧 **{tool_name}**: {tool_result}"
                            response_text = response_text.replace(old_call, new_call)
                        except Exception as e:
                            print(f"❌ Error ejecutando {tool_name}: {str(e)}")
                            error_msg = f"❌ Error ejecutando {tool_name}: {str(e)}"
                            old_call = f"TOOL_CALL: {tool_name}\nPARAMS: {params_str}"
                            response_text = response_text.replace(old_call, error_msg)
                    else:
                        print(f"❌ Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}")
                        error_msg = f"❌ Herramienta '{tool_name}' no disponible. Herramientas disponibles: {list(self.tools.keys())}"
                        old_call = f"TOOL_CALL: {tool_name}\nPARAMS: {params_str}"
                        response_text = response_text.replace(old_call, error_msg)
                
                return {
                    "messages": [
                        HumanMessage(content=user_message),
                        AIMessage(content=response_text)
                    ],
                    "todos": [
                        {
                            "content": "Análisis completado con herramientas",
                            "status": "completed",
                            "activeForm": "Completando análisis con herramientas"
                        }
                    ],
                    "files": {}
                }
            return {"messages": [], "todos": [], "files": {}}
    
    agent = SimpleAgent()
    print("Agente simplificado creado como fallback")

# Para deployment en Render, exponemos el agente como una app FastAPI
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
import asyncio
import logging
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importar módulos de base de datos
from database import async_init_database, ThreadService, get_database_stats, migrate_threads_from_langgraph

app = FastAPI(title="Lois Deep Agent API")

# Middleware de logging para debug
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Log de la petición entrante
    body = None
    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
        # Recrear el request para que funcione normalmente
        request._body = body
    
    logger.info(f"📨 {request.method} {request.url.path} - Headers: {dict(request.headers)} - Body: {body.decode() if body else 'None'}")
    
    response = await call_next(request)
    
    logger.info(f"📤 Response status: {response.status_code}")
    return response

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

# Inicializar base de datos al inicio
@app.on_event("startup")
async def startup_event():
    """Inicializar la base de datos al arrancar la aplicación"""
    await async_init_database()
    print("Base de datos SQLite lista para usar")
    
    # Intentar migrar threads desde LangGraph
    await migrate_threads_from_langgraph()

@app.get("/health")
async def health_check():
    """Health check endpoint para Render"""
    stats = await get_database_stats()
    return {
        "status": "healthy", 
        "service": "lois-agent-backend",
        "database": stats
    }

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
        
        # Obtener o crear thread en la base de datos
        thread = await ThreadService.get_or_create_thread(thread_id)
        
        # Crear mensaje del usuario en la base de datos
        user_message_data = {
            "id": str(uuid.uuid4()),
            "type": "human",
            "content": request.message
        }
        
        # Guardar mensaje del usuario en la base de datos
        await ThreadService.add_message(thread_id, user_message_data)
        
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
                                # Procesar content de manera más inteligente
                                if isinstance(msg.content, list):
                                    # Si es una lista, extraer solo el texto
                                    text_parts = []
                                    for item in msg.content:
                                        if isinstance(item, dict):
                                            if item.get('type') == 'text' and 'text' in item:
                                                text_parts.append(item['text'])
                                        elif isinstance(item, str):
                                            text_parts.append(item)
                                    content = ' '.join(text_parts) if text_parts else str(msg.content)
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
                            
                        # Crear datos del mensaje para la base de datos
                        message_data = {
                            "id": getattr(msg, 'id', str(uuid.uuid4())),
                            "type": msg_type,
                            "content": content,
                            "tool_calls": tool_calls,
                            "tool_call_id": tool_call_id
                        }
                        
                        # Guardar mensaje en la base de datos
                        db_message = await ThreadService.add_message(thread_id, message_data)
                        
                        # Crear objeto para respuesta
                        message_obj = Message(
                            id=db_message.id,
                            type=db_message.type,
                            content=db_message.content,
                            timestamp=db_message.timestamp.isoformat() + "Z",
                            tool_calls=db_message.tool_calls,
                            tool_call_id=db_message.tool_call_id
                        )
                        agent_messages.append(message_obj)
                    except Exception as msg_error:
                        print(f"Error procesando mensaje individual: {msg_error}")
                        continue
            except Exception as messages_error:
                print(f"Error procesando lista de mensajes: {messages_error}")
        
        # Extraer TODOs y archivos de los tool_calls y tool messages en agent_messages
        todos_data = []
        files_data = {}
        
        for msg in agent_messages:
            # Buscar tool calls de write_todos
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    if isinstance(tool_call, dict) and tool_call.get('name') == 'write_todos':
                        tool_input = tool_call.get('input', {})
                        if 'todos' in tool_input:
                            todos_text = tool_input['todos']
                            # Parsear todos del texto
                            todos_lines = [line.strip() for line in todos_text.split('\n') if line.strip()]
                            for i, line in enumerate(todos_lines):
                                # Determinar status basado en si tiene checkmark
                                if line.startswith('✅'):
                                    status = "completed"
                                    content = line.replace('✅', '').strip()
                                elif line.startswith(f'{i+1}.'):
                                    status = "pending"  
                                    content = line[2:].strip()  # Remove "1. "
                                else:
                                    status = "pending"
                                    content = line
                                
                                if content:
                                    todo_dict = {
                                        "content": content,
                                        "status": status,
                                        "activeForm": f"Working on {content.lower()}"
                                    }
                                    todos_data.append(todo_dict)
                        tools_used.append("write_todos")
                    
                    elif isinstance(tool_call, dict) and tool_call.get('name') == 'write_file':
                        tool_input = tool_call.get('input', {})
                        file_path = tool_input.get('file_path', '')
                        file_content = tool_input.get('content', '')
                        if file_path and file_content:
                            files_data[file_path] = file_content
                        tools_used.append("write_file")
        
        # Debug prints para verificar datos extraídos
        print(f"📋 TODOS extraídos: {len(todos_data)} items")
        for i, todo in enumerate(todos_data):
            print(f"  {i+1}. {todo}")
        
        print(f"📁 FILES extraídos: {len(files_data)} archivos")
        for filename, content_preview in files_data.items():
            print(f"  - {filename}: {len(content_preview)} chars")
        
        # Guardar todos y archivos en la base de datos
        if todos_data:
            await ThreadService.update_thread_todos(thread_id, todos_data)
            print(f"✅ Guardados {len(todos_data)} todos en DB")
        
        if files_data:
            await ThreadService.update_thread_files(thread_id, files_data)
            print(f"✅ Guardados {len(files_data)} archivos en DB")
        
        # Si no hay mensajes del agente, crear uno por defecto
        if not agent_messages:
            default_message = Message(
                id=str(uuid.uuid4()),
                type="ai", 
                content="Lo siento, no pude procesar tu consulta correctamente.",
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
            agent_messages.append(default_message)
        
        # Obtener thread actualizado de la base de datos
        updated_thread = await ThreadService.get_thread(thread_id)
        
        # Poblar todos_list y files_dict desde el thread actualizado
        if updated_thread:
            # Obtener todos del thread
            todos_list = [todo.to_dict() for todo in updated_thread.todos] if updated_thread.todos else []
            # Obtener archivos del thread
            files_dict = {file.filename: file.content for file in updated_thread.files} if updated_thread.files else {}
            
            print(f"📋 Thread actualizado - Todos: {len(todos_list)}, Files: {len(files_dict)}")
        else:
            print("❌ No se pudo obtener thread actualizado")
        
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
            "message_count": len(updated_thread.messages) if updated_thread else 0,
            "files_count": len(updated_thread.files) if updated_thread else 0,
            "todos_count": len(updated_thread.todos) if updated_thread else 0
        }
        
        # Combinar todos los mensajes para la respuesta
        all_messages = []
        if updated_thread:
            for db_msg in updated_thread.messages:
                msg_dict = db_msg.to_dict()
                msg_obj = Message(**msg_dict)
                all_messages.append(msg_obj)
        
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

@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Endpoint de streaming HÍBRIDO: 
    1. Llama a /chat para obtener respuesta completa  
    2. Hace streaming simulado de la respuesta
    """
    async def generate_response():
        import json
        
        try:
            # Enviar evento de inicio
            thread_id = request.thread_id or str(uuid.uuid4())
            yield f"data: {json.dumps({'type': 'start', 'thread_id': thread_id})}\n\n"
            
            print(f"🔄 STREAMING HÍBRIDO: Procesando {request.message[:50]}...")
            
            # Llamar directamente al endpoint /chat internamente
            # Simular la request para evitar llamada HTTP
            internal_request = ChatRequest(message=request.message, thread_id=thread_id)
            
            # Llamar directamente a la función chat_endpoint
            chat_result = await chat_endpoint(internal_request)
            
            # Convertir ChatResponse a dict
            chat_data = {
                "messages": [msg.dict() if hasattr(msg, 'dict') else msg for msg in chat_result.messages],
                "todos": [todo.dict() if hasattr(todo, 'dict') else todo for todo in chat_result.todos],  
                "files": chat_result.files,
                "thread_id": chat_result.thread_id,
                "metadata": chat_result.metadata
            }
            
            print(f"✅ Chat response received with {len(chat_data.get('messages', []))} messages")
            print(f"📋 Todos: {len(chat_data.get('todos', []))}")
            print(f"📄 Files: {len(chat_data.get('files', {}))}")
            
            # Extraer contenido de AI para streaming
            ai_content = ""
            
            for message in chat_data.get('messages', []):
                if message.get('type') == 'ai' and message.get('content'):
                    ai_content += message['content'] + "\n\n"
            
            print(f"🔤 Content to stream: {len(ai_content)} characters")
            
            # Streamear el contenido palabra por palabra
            if ai_content.strip():
                words = ai_content.split()
                chunk_size = 3
                
                for i in range(0, len(words), chunk_size):
                    chunk_words = words[i:i+chunk_size]
                    chunk_text = ' '.join(chunk_words)
                    
                    if i + chunk_size < len(words):
                        chunk_text += ' '
                    
                    chunk_data = {
                        'type': 'text_chunk',
                        'content': chunk_text,
                        'is_complete': i + chunk_size >= len(words)
                    }
                    
                    yield f"data: {json.dumps(chunk_data)}\n\n"
                    await asyncio.sleep(0.04)
            
            # Enviar evento de finalización con TODOS los datos
            completion_data = {
                'type': 'complete',
                'thread_id': chat_data.get('thread_id', thread_id),
                'todos': chat_data.get('todos', []),
                'files': chat_data.get('files', {}),
                'metadata': chat_data.get('metadata', {})
            }
            
            print(f"🏁 Enviando completion_data con {len(completion_data['todos'])} todos y {len(completion_data['files'])} files")
            
            yield f"data: {json.dumps(completion_data)}\n\n"
            
        except Exception as e:
            import traceback
            error_msg = f"Error en streaming híbrido: {str(e)}"
            error_trace = traceback.format_exc()
            print(f"❌ STREAM ERROR: {error_msg}")
            print(f"❌ STACK TRACE: {error_trace}")
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
    
    
    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
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
    """Lógica común para búsqueda de threads usando SQLite"""
    try:
        # Buscar threads en la base de datos
        db_threads = await ThreadService.search_threads(limit, offset, sort_by, sort_order)
        
        # Convertir threads de DB a formato compatible con LangGraph API
        thread_list = []
        for db_thread in db_threads:
            # Convertir mensajes
            messages = []
            for db_msg in db_thread.messages:
                messages.append(db_msg.to_dict())
            
            # Convertir todos
            todos = []
            for db_todo in db_thread.todos:
                todos.append(db_todo.to_dict())
            
            # Convertir archivos a diccionario
            files = {}
            for db_file in db_thread.files:
                files[db_file.filename] = db_file.content
            
            thread_list.append({
                "thread_id": db_thread.id,
                "created_at": db_thread.created_at.isoformat() + "Z" if db_thread.created_at else None,
                "updated_at": db_thread.updated_at.isoformat() + "Z" if db_thread.updated_at else None,
                "values": {
                    "messages": messages,
                    "todos": todos,
                    "files": files
                },
                "metadata": {
                    "message_count": len(messages),
                    "files_count": len(files),
                    "todos_count": len(todos)
                },
                "status": "idle",
                "config": {
                    "recursion_limit": 100,
                    "configurable": {}
                }
            })
        
        return thread_list
        
    except Exception as e:
        print(f"Error en /threads/search: {e}")
        import traceback
        traceback.print_exc()
        return []

@app.get("/threads/{thread_id}")
async def get_thread(thread_id: str):
    """Obtener historial de un thread específico - Compatible con LangGraph API"""
    db_thread = await ThreadService.get_thread(thread_id)
    if not db_thread:
        raise HTTPException(status_code=404, detail="Thread no encontrado")
    
    # Convertir mensajes
    messages = []
    for db_msg in db_thread.messages:
        messages.append(db_msg.to_dict())
    
    # Convertir todos
    todos = []
    for db_todo in db_thread.todos:
        todos.append(db_todo.to_dict())
    
    # Convertir archivos
    files = {}
    for db_file in db_thread.files:
        files[db_file.filename] = db_file.content
    
    return {
        "thread_id": thread_id,
        "created_at": db_thread.created_at.isoformat() + "Z" if db_thread.created_at else None,
        "updated_at": db_thread.updated_at.isoformat() + "Z" if db_thread.updated_at else None,
        "metadata": db_thread.thread_metadata or {},
        "status": "idle",  # Para compatibilidad con LangGraph
        "values": {
            "messages": messages,
            "todos": todos,
            "files": files
        },
        "config": {
            "recursion_limit": 100,
            "configurable": {}
        }
    }

# Endpoint adicional para compatibilidad completa con LangGraph API
@app.post("/threads")
async def create_thread():
    """Crear un nuevo thread - Compatible con LangGraph API"""
    db_thread = await ThreadService.create_thread()
    
    return {
        "thread_id": db_thread.id,
        "created_at": db_thread.created_at.isoformat() + "Z" if db_thread.created_at else None,
        "metadata": db_thread.thread_metadata or {}
    }

# Modelo para historial de thread
class ThreadHistoryRequest(BaseModel):
    limit: int = 1000

@app.post("/threads/{thread_id}/history")
async def get_thread_history(thread_id: str, request: ThreadHistoryRequest):
    """Obtener historial de un thread - Compatible con LangGraph API"""
    db_thread = await ThreadService.get_thread(thread_id)
    if not db_thread:
        raise HTTPException(status_code=404, detail="Thread no encontrado")
    
    # Convertir mensajes
    messages = []
    for db_msg in db_thread.messages:
        messages.append(db_msg.to_dict())
    
    # Convertir todos
    todos = []
    for db_todo in db_thread.todos:
        todos.append(db_todo.to_dict())
    
    # Convertir archivos
    files = {}
    for db_file in db_thread.files:
        files[db_file.filename] = db_file.content
    
    # Limitar mensajes según el request
    limited_messages = messages[-request.limit:] if request.limit < len(messages) else messages
    
    return {
        "values": {
            "messages": limited_messages,
            "todos": todos,
            "files": files
        },
        "metadata": {
            "message_count": len(limited_messages),
            "files_count": len(files),
            "todos_count": len(todos)
        },
        "thread_id": thread_id
    }

@app.get("/threads/{thread_id}/history")
async def get_thread_history_simple(thread_id: str):
    """Obtener solo mensajes como array - Para compatibilidad con SDK"""
    db_thread = await ThreadService.get_thread(thread_id)
    if not db_thread:
        return []  # Devolver array vacío si no existe
    
    # Convertir solo mensajes a array
    messages = []
    for db_msg in db_thread.messages:
        messages.append(db_msg.to_dict())
    
    return messages

@app.get("/threads/{thread_id}/state")
async def get_thread_state(thread_id: str):
    """Obtener estado actual de un thread - Compatible con LangGraph API"""
    db_thread = await ThreadService.get_thread(thread_id)
    if not db_thread:
        raise HTTPException(status_code=404, detail="Thread no encontrado")
    
    # Convertir mensajes
    messages = []
    for db_msg in db_thread.messages:
        messages.append(db_msg.to_dict())
    
    # Convertir todos
    todos = []
    for db_todo in db_thread.todos:
        todos.append(db_todo.to_dict())
    
    # Convertir archivos
    files = {}
    for db_file in db_thread.files:
        files[db_file.filename] = db_file.content
    
    return {
        "values": {
            "messages": messages,
            "todos": todos,
            "files": files
        },
        "next": [],  # Para compatibilidad con LangGraph
        "metadata": {
            "message_count": len(messages),
            "files_count": len(files),
            "todos_count": len(todos)
        },
        "created_at": db_thread.created_at.isoformat() + "Z" if db_thread.created_at else None,
        "updated_at": db_thread.updated_at.isoformat() + "Z" if db_thread.updated_at else None,
        "thread_id": thread_id
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("agent:app", host="0.0.0.0", port=port, reload=True)