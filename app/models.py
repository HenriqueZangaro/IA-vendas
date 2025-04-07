from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .models_base import Base  # Agora importando Base de models_base.py

# Classe de "Thread" para armazenar as threads (conversas)
class Thread(Base):
    __tablename__ = "threads"
    
    thread_id = Column(Integer, primary_key=True, index=True)  # ID da thread
    whatsapp_number = Column(String(15), unique=True, nullable=False, index=True)
    external_thread_id = Column(Text, nullable=False)  # ID externo da thread
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relacionamento com a tabela Conversation
    conversations = relationship("Conversation", back_populates="thread")

    def __repr__(self):
        return f"<Thread(thread_id={self.thread_id}, whatsapp_number={self.whatsapp_number})>"

# Classe de "Conversation" para armazenar as conversas associadas a uma thread
class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(Integer, ForeignKey("threads.thread_id"), nullable=False)  # Relacionamento com a tabela threads
    status = Column(String, default="iniciado")  # Status da conversa, como "iniciado", "aguardando pagamento", etc.
    messages = Column(Text)  # Armazena o histórico das mensagens em texto
    
    # Relacionamento com a tabela Thread
    thread = relationship("Thread", back_populates="conversations")

    def __repr__(self):
        return f"<Conversation(thread_id={self.thread_id}, status={self.status})>"
