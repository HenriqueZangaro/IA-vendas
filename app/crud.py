from sqlalchemy.orm import Session
from .models import threads, conversations  # Adicionamos a importação de conversations
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError

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
    
    query = select(threads.c.thread_id, threads.c.whatsapp_number, threads.c.external_thread_id).where(
        threads.c.whatsapp_number == cleaned_number
    )
    result = db.execute(query).fetchone()  # ✅ Obtém a linha da query
    
    if result:
        return {"thread_id": result[0], "whatsapp_number": result[1], "external_thread_id": result[2]}  # Correção na indexação da tupla
    
    return None

def create_thread(db: Session, whatsapp_number: str, external_thread_id: str):
    """ Cria uma nova thread no banco de dados. """
    cleaned_number = clean_whatsapp_number(whatsapp_number)
    
    stmt = insert(threads).values(
        whatsapp_number=cleaned_number,
        external_thread_id=external_thread_id  # Corrigido para `external_thread_id`
    )
    
    db.execute(stmt)
    db.commit()  # Necessário para salvar a alteração no banco

def get_conversation_by_thread_id(db: Session, thread_id: str):
    """ Recupera o histórico de conversa associado ao thread_id. """
    query = select(conversations.c.status, conversations.c.messages).where(
        conversations.c.thread_id == thread_id
    )
    result = db.execute(query).fetchone()
    
    if result:
        return {"status": result[0], "messages": result[1]}  # Retorna o status e as mensagens da conversa
    return None

def create_conversation(db: Session, thread_id: str, status: str, messages: str):
    """ Cria uma nova conversa no banco de dados. """
    stmt = insert(conversations).values(
        thread_id=thread_id,
        status=status,
        messages=messages  # Armazenando o histórico das mensagens
    )
    
    try:
        db.execute(stmt)
        db.commit()  # Commit para salvar a conversa no banco
    except IntegrityError:
        db.rollback()  # Caso já exista uma conversa com o mesmo thread_id
        raise ValueError("Conversation already exists for this thread_id")

def update_conversation_status(db: Session, thread_id: str, status: str):
    """ Atualiza o status da conversa para um determinado thread_id. """
    stmt = update(conversations).where(conversations.c.thread_id == thread_id).values(
        status=status
    )
    
    result = db.execute(stmt)
    db.commit()
    
    if result.rowcount == 0:
        raise ValueError(f"No conversation found for thread_id {thread_id}")
    return status
