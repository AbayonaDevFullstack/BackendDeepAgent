"""
Configuración y funciones de base de datos SQLite
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from models import Base, Thread, Message, ThreadFile, ThreadTodo
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///threads.db")
ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")

# Motores de base de datos
engine = create_engine(DATABASE_URL, echo=False)
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)

# Sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(async_engine)

def init_database():
    """Inicializar la base de datos creando todas las tablas"""
    Base.metadata.create_all(bind=engine)
    print("Base de datos SQLite inicializada correctamente")

async def async_init_database():
    """Inicializar la base de datos de forma asíncrona"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Base de datos SQLite inicializada correctamente (async)")

class ThreadService:
    """Servicio para manejar operaciones de threads en la base de datos"""
    
    @staticmethod
    async def create_thread(thread_id: Optional[str] = None) -> Thread:
        """Crear un nuevo thread"""
        async with AsyncSessionLocal() as session:
            thread = Thread(id=thread_id) if thread_id else Thread()
            session.add(thread)
            await session.commit()
            await session.refresh(thread)
            return thread
    
    @staticmethod
    async def get_thread(thread_id: str) -> Optional[Thread]:
        """Obtener un thread por ID"""
        async with AsyncSessionLocal() as session:
            from sqlalchemy.orm import selectinload
            from sqlalchemy import select
            
            stmt = select(Thread).options(
                selectinload(Thread.messages),
                selectinload(Thread.files),
                selectinload(Thread.todos)
            ).where(Thread.id == thread_id)
            
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    @staticmethod
    async def get_or_create_thread(thread_id: str) -> Thread:
        """Obtener un thread existente o crear uno nuevo"""
        thread = await ThreadService.get_thread(thread_id)
        if not thread:
            thread = await ThreadService.create_thread(thread_id)
        return thread
    
    @staticmethod
    async def search_threads(limit: int = 30, offset: int = 0, 
                           sort_by: str = "created_at", sort_order: str = "desc") -> List[Thread]:
        """Buscar threads con paginación y ordenamiento"""
        async with AsyncSessionLocal() as session:
            from sqlalchemy.orm import selectinload
            from sqlalchemy import select, desc, asc
            
            # Debug: Contar threads totales primero
            from sqlalchemy import func
            count_stmt = select(func.count(Thread.id))
            count_result = await session.execute(count_stmt)
            total_count = count_result.scalar()
            print(f"🔍 DEBUG: Total threads in DB: {total_count}")
            
            stmt = select(Thread).options(
                selectinload(Thread.messages),
                selectinload(Thread.files),
                selectinload(Thread.todos)
            )
            
            # Aplicar ordenamiento
            if sort_by == "created_at":
                if sort_order == "desc":
                    stmt = stmt.order_by(desc(Thread.created_at))
                else:
                    stmt = stmt.order_by(asc(Thread.created_at))
            elif sort_by == "updated_at":
                if sort_order == "desc":
                    stmt = stmt.order_by(desc(Thread.updated_at))
                else:
                    stmt = stmt.order_by(asc(Thread.updated_at))
            
            # Aplicar paginación
            stmt = stmt.offset(offset).limit(limit)
            
            result = await session.execute(stmt)
            threads = result.scalars().all()
            print(f"🔍 DEBUG: Found {len(threads)} threads with query")
            
            return threads
    
    @staticmethod
    async def add_message(thread_id: str, message_data: Dict[str, Any]) -> Message:
        """Agregar un mensaje a un thread"""
        async with AsyncSessionLocal() as session:
            # Asegurar que el thread existe
            await ThreadService.get_or_create_thread(thread_id)
            
            message = Message(
                id=message_data.get("id"),
                thread_id=thread_id,
                type=message_data.get("type"),
                content=message_data.get("content"),
                tool_calls=message_data.get("tool_calls"),
                tool_call_id=message_data.get("tool_call_id")
            )
            
            session.add(message)
            
            # Actualizar timestamp del thread
            from sqlalchemy import select
            stmt = select(Thread).where(Thread.id == thread_id)
            result = await session.execute(stmt)
            thread = result.scalar_one()
            thread.updated_at = datetime.utcnow()
            
            await session.commit()
            await session.refresh(message)
            return message
    
    @staticmethod
    async def update_thread_files(thread_id: str, files_dict: Dict[str, str]):
        """Actualizar archivos de un thread"""
        async with AsyncSessionLocal() as session:
            # Limpiar archivos existentes
            from sqlalchemy import delete
            await session.execute(delete(ThreadFile).where(ThreadFile.thread_id == thread_id))
            
            # Agregar nuevos archivos
            for filename, content in files_dict.items():
                file_obj = ThreadFile(
                    thread_id=thread_id,
                    filename=filename,
                    content=content
                )
                session.add(file_obj)
            
            await session.commit()
    
    @staticmethod
    async def update_thread_todos(thread_id: str, todos_list: List[Dict[str, Any]]):
        """Actualizar todos de un thread"""
        async with AsyncSessionLocal() as session:
            # Limpiar todos existentes
            from sqlalchemy import delete
            await session.execute(delete(ThreadTodo).where(ThreadTodo.thread_id == thread_id))
            
            # Agregar nuevos todos
            for todo_data in todos_list:
                todo_obj = ThreadTodo(
                    thread_id=thread_id,
                    content=todo_data.get("content"),
                    status=todo_data.get("status"),
                    active_form=todo_data.get("activeForm")
                )
                session.add(todo_obj)
            
            await session.commit()
    
    @staticmethod
    async def delete_thread(thread_id: str) -> bool:
        """Eliminar un thread y todos sus datos relacionados"""
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            
            stmt = select(Thread).where(Thread.id == thread_id)
            result = await session.execute(stmt)
            thread = result.scalar_one_or_none()
            
            if thread:
                await session.delete(thread)
                await session.commit()
                return True
            return False

# Funciones de conveniencia
async def get_database_stats() -> Dict[str, Any]:
    """Obtener estadísticas de la base de datos"""
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select, func
        
        # Contar threads
        threads_count = await session.execute(select(func.count(Thread.id)))
        threads_total = threads_count.scalar()
        
        # Contar mensajes
        messages_count = await session.execute(select(func.count(Message.id)))
        messages_total = messages_count.scalar()
        
        # Contar archivos
        files_count = await session.execute(select(func.count(ThreadFile.id)))
        files_total = files_count.scalar()
        
        return {
            "threads_count": threads_total,
            "messages_count": messages_total,
            "files_count": files_total,
            "database_url": DATABASE_URL
        }

async def migrate_threads_from_langgraph():
    """Migrar threads existentes desde LangGraph Server a SQLite"""
    try:
        import httpx
        import asyncio
        from datetime import datetime
        
        # Verificar si ya hay threads en SQLite
        stats = await get_database_stats()
        if stats["threads_count"] > 0:
            print(f"SQLite ya tiene {stats['threads_count']} threads, saltando migracion")
            return
        
        print("Iniciando migracion de threads desde LangGraph...")
        
        # Intentar conectar a LangGraph Server
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    "http://127.0.0.1:2024/threads/search",
                    json={"limit": 100, "offset": 0},
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 200:
                    print(f"LangGraph Server no disponible (status: {response.status_code})")
                    return
                
                langgraph_threads = response.json()
                print(f"📥 Encontrados {len(langgraph_threads)} threads en LangGraph")
                
                if not langgraph_threads:
                    print("No hay threads para migrar")
                    return
                
                # Migrar cada thread
                migrated_count = 0
                for lg_thread in langgraph_threads:
                    try:
                        thread_id = lg_thread.get("thread_id")
                        if not thread_id:
                            continue
                        
                        # Verificar si ya existe
                        existing = await ThreadService.get_thread(thread_id)
                        if existing:
                            continue
                        
                        # Crear thread en SQLite
                        thread = await ThreadService.create_thread(thread_id)
                        
                        # Migrar mensajes
                        values = lg_thread.get("values", {})
                        messages = values.get("messages", [])
                        
                        for msg in messages:
                            if isinstance(msg, dict):
                                # Adaptar formato de mensaje
                                msg_data = {
                                    "id": msg.get("id", str(uuid.uuid4())),
                                    "type": msg.get("type", "ai"),
                                    "content": str(msg.get("content", "")),
                                    "tool_calls": msg.get("tool_calls"),
                                    "tool_call_id": msg.get("tool_call_id")
                                }
                                await ThreadService.add_message(thread_id, msg_data)
                        
                        # Migrar archivos
                        files = values.get("files", {})
                        if files:
                            await ThreadService.update_thread_files(thread_id, files)
                        
                        # Migrar todos
                        todos = values.get("todos", [])
                        if todos:
                            await ThreadService.update_thread_todos(thread_id, todos)
                        
                        migrated_count += 1
                        print(f"Migrado thread {thread_id} ({migrated_count}/{len(langgraph_threads)})")
                        
                    except Exception as e:
                        print(f"Error migrando thread {lg_thread.get('thread_id', 'unknown')}: {e}")
                        continue
                
                print(f"Migracion completada: {migrated_count} threads migrados a SQLite")
                
            except httpx.ConnectError:
                print("LangGraph Server no esta ejecutandose en puerto 2024")
                print("   Para migrar threads históricos, ejecuta: langgraph dev")
            except httpx.TimeoutException:
                print("Timeout conectando a LangGraph Server")
            except Exception as e:
                print(f"Error durante migracion: {e}")
                
    except ImportError:
        print("httpx no disponible, saltando migracion")
    except Exception as e:
        print(f"Error inesperado en migracion: {e}")