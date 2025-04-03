from fastapi import FastAPI, HTTPException
from .database import engine, database
from .models import metadata
from .crud import get_thread_by_number, create_thread

app = FastAPI()

@app.on_event("startup")
async def startup():
    metadata.create_all(engine)
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/threads/{whatsapp_number}")
async def read_thread(whatsapp_number: str):
    thread = await get_thread_by_number(whatsapp_number)
    if thread:
        return thread
    raise HTTPException(status_code=404, detail="Thread not found")

@app.post("/threads/")
async def create_new_thread(whatsapp_number: str):
    thread = await get_thread_by_number(whatsapp_number)
    if thread:
        return thread
    await create_thread(whatsapp_number)
    return {"message": "Thread created successfully"}