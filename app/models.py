from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .models_base import Base

class Thread(Base):
    __tablename__ = "threads"
    
    thread_id = Column(Integer, primary_key=True, index=True)
    whatsapp_number = Column(String(15), unique=True, nullable=False)
    external_thread_id = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relacionamento com a tabela Conversation
    conversations = relationship("Conversation", back_populates="thread", cascade="all, delete-orphan")
    
    # Índices adicionais
    __table_args__ = (
        Index('idx_whatsapp_number', 'whatsapp_number'),
    )
    
    def __repr__(self):
        return f"<Thread(thread_id={self.thread_id}, whatsapp_number={self.whatsapp_number})>"

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(Integer, ForeignKey("threads.thread_id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), default="iniciado")
    messages = Column(Text)
    
    # Relacionamento com a tabela Thread
    thread = relationship("Thread", back_populates="conversations")
    
    # Índices adicionais
    __table_args__ = (
        Index('idx_thread_id', 'thread_id'),
        Index('idx_status', 'status'),
    )
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, thread_id={self.thread_id}, status={self.status})>"
