"""
Modelos de base de datos SQLAlchemy para persistencia de threads
"""
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Thread(Base):
    __tablename__ = "threads"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    thread_metadata = Column(JSON, default=dict)
    
    # Relaciones
    messages = relationship("Message", back_populates="thread", cascade="all, delete-orphan")
    files = relationship("ThreadFile", back_populates="thread", cascade="all, delete-orphan")
    todos = relationship("ThreadTodo", back_populates="thread", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "thread_id": self.id,
            "created_at": self.created_at.isoformat() + "Z" if self.created_at else None,
            "updated_at": self.updated_at.isoformat() + "Z" if self.updated_at else None,
            "metadata": self.thread_metadata or {}
        }

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    thread_id = Column(String, ForeignKey("threads.id"))
    type = Column(String)  # 'human', 'ai', 'tool'
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    tool_calls = Column(JSON, default=list)
    tool_call_id = Column(String, nullable=True)
    
    # Relación
    thread = relationship("Thread", back_populates="messages")
    
    def to_dict(self):
        # Limpiar el contenido si está en formato JSON stringificado
        content = self.content
        if isinstance(content, str):
            try:
                import json
                import ast
                # Intentar parsear como JSON primero, luego como Python literal
                try:
                    parsed = json.loads(content)
                except json.JSONDecodeError:
                    # Si falla JSON, intentar ast.literal_eval para Python literals
                    parsed = ast.literal_eval(content)
                if isinstance(parsed, list):
                    # Si es una lista, extraer solo texto
                    text_parts = []
                    for item in parsed:
                        if isinstance(item, dict):
                            if item.get('type') == 'text':
                                # Buscar el texto en diferentes campos posibles
                                text_content = item.get('text', '')
                                if text_content:
                                    text_parts.append(text_content)
                            elif item.get('type') == 'tool_use':
                                # Ignorar tool_use ya que no es contenido de texto visible
                                continue
                        elif isinstance(item, str):
                            text_parts.append(item)
                    content = '\n\n'.join(text_parts) if text_parts else content
                elif isinstance(parsed, dict) and parsed.get('type') == 'text':
                    content = parsed.get('text', content)
            except (json.JSONDecodeError, ValueError, SyntaxError):
                # Si no es JSON válido, mantener el contenido original
                pass
        
        return {
            "id": self.id,
            "type": self.type,
            "content": content,
            "timestamp": self.timestamp.isoformat() + "Z" if self.timestamp else None,
            "tool_calls": self.tool_calls,
            "tool_call_id": self.tool_call_id
        }

class ThreadFile(Base):
    __tablename__ = "thread_files"
    
    id = Column(Integer, primary_key=True)
    thread_id = Column(String, ForeignKey("threads.id"))
    filename = Column(String)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relación
    thread = relationship("Thread", back_populates="files")
    
    def to_dict(self):
        return {
            "filename": self.filename,
            "content": self.content,
            "created_at": self.created_at.isoformat() + "Z" if self.created_at else None
        }

class ThreadTodo(Base):
    __tablename__ = "thread_todos"
    
    id = Column(Integer, primary_key=True)
    thread_id = Column(String, ForeignKey("threads.id"))
    content = Column(String)
    status = Column(String)
    active_form = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relación
    thread = relationship("Thread", back_populates="todos")
    
    def to_dict(self):
        return {
            "content": self.content,
            "status": self.status,
            "activeForm": self.active_form
        }