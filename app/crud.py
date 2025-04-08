from sqlalchemy.orm import Session
from .models import Thread, Conversation  # Importando as classes ORM
from sqlalchemy.exc import IntegrityError
import re

def clean_whatsapp_number(whatsapp_number: str) -> str:
    """ Limpa e formata o número de WhatsApp, mantendo apenas o DDD e o número. """
    cleaned_number = re.sub(r'\D', '', whatsapp_number)  # Remove caracteres não numéricos
    if len(cleaned_number) < 10:
        raise ValueError("Número de WhatsApp inválido")
    if len(cleaned_number) > 11:  # Se incluir código do país (ex: +55)
        cleaned_number = cleaned_number[-11:]
    return cleaned_number

def get_thread_by_number(db: Session, whatsapp_number: str):
    """ Busca uma thread pelo número do WhatsApp. """
    cleaned_number = clean_whatsapp_number(whatsapp_number)
    # Usando ORM para consultar a tabela 'Thread'
    thread = db.query(Thread).filter(Thread.whatsapp_number == cleaned_number).first()
    if thread:
        return {"thread_id": thread.thread_id, "whatsapp_number": thread.whatsapp_number, "external_thread_id": thread.external_thread_id}
    return None

def create_thread(db: Session, whatsapp_number: str, external_thread_id: str):
    """ Cria uma nova thread no banco de dados. """
    cleaned_number = clean_whatsapp_number(whatsapp_number)
    # Verificar se o número de WhatsApp já existe antes de criar a thread
    existing_thread = db.query(Thread).filter(Thread.whatsapp_number == cleaned_number).first()
    if existing_thread:
        raise ValueError("Thread already exists for this WhatsApp number")
    
    # Criar uma nova instância da classe Thread e adicioná-la ao banco de dados
    new_thread = Thread(
        whatsapp_number=cleaned_number,
        external_thread_id=external_thread_id
    )
    db.add(new_thread)
    db.commit()  # Necessário para salvar a alteração no banco
    db.refresh(new_thread)  # Atualiza a instância com os dados do banco, incluindo o ID gerado
    return new_thread

def get_conversations_by_thread_id(db: Session, thread_id: str):
    """ Recupera o histórico completo de conversas associadas ao thread_id. """
    # Busca todas as conversas para o thread_id
    conversations = db.query(Conversation).filter(Conversation.thread_id == thread_id).all()
    
    if conversations:
        # Retorna todas as conversas
        return [
            {"status": conversation.status, "messages": conversation.messages}
            for conversation in conversations
        ]
    return None

def get_conversation_by_thread_id(db: Session, thread_id: str):
    """ Recupera o histórico completo de conversa associado ao thread_id. """
    return get_conversations_by_thread_id(db, thread_id)

def create_conversation(db: Session, thread_id: str, status: str, messages: str):
    """ Cria uma nova conversa no banco de dados. """
    # Verificar se o thread_id existe na tabela 'threads'
    thread = db.query(Thread).filter(Thread.thread_id == thread_id).first()
    if not thread:
        raise ValueError("Thread not found")
    
    new_conversation = Conversation(
        thread_id=thread_id,
        status=status,
        messages=messages  # Armazenando o histórico das mensagens
    )
    try:
        db.add(new_conversation)
        db.commit()  # Commit para salvar a conversa no banco
        db.refresh(new_conversation)  # Atualiza a instância com os dados do banco
    except IntegrityError:
        db.rollback()  # Caso já exista uma conversa com o mesmo thread_id
        raise ValueError("Conversation already exists for this thread_id")
    
    return new_conversation

def update_conversation_status(db: Session, thread_id: str, status: str):
    """ Atualiza o status da conversa para um determinado thread_id. """
    # Verificar se o thread_id existe na tabela 'threads'
    thread = db.query(Thread).filter(Thread.thread_id == thread_id).first()
    if not thread:
        raise ValueError(f"No thread found for thread_id {thread_id}")
    
    # Usando ORM para atualizar o status da conversa
    conversation = db.query(Conversation).filter(Conversation.thread_id == thread_id).first()
    if conversation:
        conversation.status = status
        db.commit()
        return status
    
    raise ValueError(f"No conversation found for thread_id {thread_id}")
