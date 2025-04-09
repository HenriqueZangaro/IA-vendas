from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Definindo a estrutura base para a Thread
class ThreadBase(BaseModel):
    whatsapp_number: str = Field(..., min_length=1, max_length=20)
    external_thread_id: Optional[str] = None  # O external_thread_id será passado da OpenAI

# Classe para criação de uma nova Thread
class ThreadCreate(ThreadBase):
    pass

# Classe para resposta de uma Thread
class ThreadResponse(ThreadBase):
    thread_id: int  # O thread_id é o ID gerado internamente pelo banco de dados
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Utilizando os dados do banco como atributos do modelo

# Definindo a estrutura básica para a Conversation (conversa)
class ConversationBase(BaseModel):
    thread_id: int  # Relacionando a conversa com a Thread via thread_id
    status: str = "iniciado"  # Status da conversa, pode ser alterado conforme necessário
    messages: Optional[str] = None  # Mensagens da conversa, pode ser um texto

# Classe para criação de uma nova Conversation
class ConversationCreate(ConversationBase):
    pass

# Classe para resposta de uma Conversation (como será retornado no endpoint)
class ConversationResponse(ConversationBase):
    id: int  # O ID da conversa, gerado automaticamente pelo banco de dados

    class Config:
        from_attributes = True  # Utilizando os dados do banco como atributos do modelo
