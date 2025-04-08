from pydantic import BaseModel
from typing import List

class MessageResponse(BaseModel):
    id: int  # ID da mensagem
    thread_id: int
    status: str
    messages: str  # Conteúdo da mensagem

    class Config:
        orm_mode = True  # Permite que o Pydantic converta objetos ORM em dicionários

class ConversationResponse(BaseModel):
    thread_id: int
    messages: List[MessageResponse]  # Lista de mensagens

    class Config:
        orm_mode = True
