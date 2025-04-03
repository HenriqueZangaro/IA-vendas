from sqlalchemy.orm import Session
from .models import threads
import re
from sqlalchemy import insert, select

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
    
    query = select(threads).where(threads.c.whatsapp_number == cleaned_number)
    result = db.execute(query).fetchone()  # ✅ Usa `fetchone()` diretamente para obter a linha
    
    if result:
        return {"whatsapp_number": result.whatsapp_number, "thread_id": result.thread_id}
    
    return None

def create_thread(db: Session, whatsapp_number: str, thread_id: str):
    """ Cria uma nova thread no banco de dados. """
    cleaned_number = clean_whatsapp_number(whatsapp_number)
    
    stmt = insert(threads).values(
        whatsapp_number=cleaned_number,
        thread_id=thread_id  # ✅ Agora inclui o `thread_id`
    )
    
    db.execute(stmt)
    db.commit()  # ✅ Necessário para salvar a alteração no banco
