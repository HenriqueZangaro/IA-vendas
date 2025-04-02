from .models import threads
from .database import database

async def get_thread_by_number(whatsapp_number: str):
    query = threads.select().where(threads.c.whatsapp_number == whatsapp_number)
    return await database.fetch_one(query)

async def create_thread(whatsapp_number: str):
    query = threads.insert().values(whatsapp_number=whatsapp_number)
    return await database.execute(query)