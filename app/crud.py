from .models import threads
from .database import database
import re

async def get_thread_by_number(whatsapp_number: str):
    # Remove caracteres não numéricos do número
    cleaned_number = re.sub(r'\D', '', whatsapp_number)
    
    # Certifique-se de que o número tenha pelo menos o DDD e o número
    if len(cleaned_number) < 10:
        raise ValueError("Número de WhatsApp inválido")
    
    # Mantém apenas o DDD e o número
    if len(cleaned_number) > 11:  # Caso inclua código do país (ex: +55)
        cleaned_number = cleaned_number[-11:]
    
    query = threads.select().where(threads.c.whatsapp_number == cleaned_number)
    return await database.fetch_one(query)

async def create_thread(whatsapp_number: str):
    query = threads.insert().values(whatsapp_number=whatsapp_number)
    return await database.execute(query)
