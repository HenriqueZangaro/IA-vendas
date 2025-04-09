from sqlalchemy.orm import Session
from .models import Thread, Conversation  # Importando as classes ORM
from sqlalchemy.exc import IntegrityError
import re
import logging

# Configuração do Logger
logger = logging.getLogger(__name__)

def clean_whatsapp_number(whatsapp_number: str) -> str:
    """ Limpa e formata o número de WhatsApp, mantendo apenas o DDD e o número. """
    cleaned_number = re.sub(r'\D', '', whatsapp_number)  # Remove caracteres não numéricos
    if len(cleaned_number) < 10:
        raise ValueError("Número de WhatsApp inválido")
    if len(cleaned_number) > 11:  # Se incluir código do país (ex: +55)
        cleaned_number = cleaned_number[-11:]
    return cleaned_number

def get_thread_by_number(db: Session, whatsapp_number: str):
    """ Busca uma thread pelo número de WhatsApp. """
    cleaned_number = clean_whatsapp_number(whatsapp_number)
    # Usando ORM para consultar a tabela 'Thread'
    thread = db.query(Thread).filter(Thread.whatsapp_number == cleaned_number).first()
    if thread:
        return {"thread_id": thread.thread_id, "whatsapp_number": thread.whatsapp_number, "external_thread_id": thread.external_thread_id, "messages": thread.messages}
    return None

def create_thread(db: Session, whatsapp_number: str, external_thread_id: str):
    """ Cria uma nova thread no banco de dados usando o external_thread_id recebido. """
    cleaned_number = clean_whatsapp_number(whatsapp_number)
    # Verificar se o número de WhatsApp já existe antes de criar a thread
    existing_thread = db.query(Thread).filter(Thread.whatsapp_number == cleaned_number).first()
    if existing_thread:
        raise ValueError("Thread already exists for this WhatsApp number")
    
    # Criar uma nova instância da classe Thread e adicioná-la ao banco de dados
    new_thread = Thread(
        whatsapp_number=cleaned_number,
        external_thread_id=external_thread_id  # Usando o external_thread_id recebido
    )
    db.add(new_thread)
    db.commit()  # Necessário para salvar a alteração no banco
    db.refresh(new_thread)  # Atualiza a instância com os dados do banco, incluindo o ID gerado
    return new_thread

def create_conversation(db: Session, external_thread_id: str, status: str, messages: str):
    """ Cria uma nova conversa no banco de dados e associa ao external_thread_id. """
    # Verificar se o external_thread_id existe na tabela 'threads'
    thread = db.query(Thread).filter(Thread.external_thread_id == external_thread_id).first()
    if not thread:
        logger.error(f"Thread not found for external_thread_id={external_thread_id}")
        raise ValueError("Thread not found")

    logger.debug(f"Thread found for external_thread_id={external_thread_id}, thread_id={thread.thread_id}")

    # Atualizando o campo 'messages' diretamente na Thread
    thread.messages = (thread.messages or "") + messages  # Concatenando a mensagem à mensagem anterior

    try:
        db.commit()  # Commit para salvar a conversa no banco
        db.refresh(thread)  # Atualiza a instância com os dados do banco
        logger.debug(f"Conversation created for external_thread_id={external_thread_id}")
    except IntegrityError:
        db.rollback()  # Caso já exista uma conversa com o mesmo external_thread_id
        logger.error(f"Conversation already exists for external_thread_id={external_thread_id}")
        raise ValueError("Conversation already exists for this external_thread_id")

    return thread

def get_conversations_by_external_thread_id(db: Session, external_thread_id: str):
    """ Recupera as mensagens associadas ao external_thread_id. """
    # Busca a thread pelo external_thread_id
    thread = db.query(Thread).filter(Thread.external_thread_id == external_thread_id).first()
    if not thread:
        return None
    
    # Retorna as mensagens da thread
    return {"status": "success", "messages": thread.messages}
