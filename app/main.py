from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import engine, database, get_db
from .models import metadata
from .routes import router
from .crud import get_thread_by_number, create_thread

app = FastAPI()

app.include_router(router)

# ✅ Criar tabelas no banco ao iniciar a API
@app.on_event("startup")
async def startup():
    print("🔄 Criando tabelas no banco de dados...")
    metadata.create_all(engine)
    await database.connect()
    print("✅ Banco de dados conectado!")

@app.on_event("shutdown")
async def shutdown():
    print("🛑 Desconectando do banco de dados...")
    await database.disconnect()
    print("✅ Banco de dados desconectado!")

@app.get("/threads/{whatsapp_number}")
async def read_thread(whatsapp_number: str, db: Session = Depends(get_db)):
    thread = get_thread_by_number(db, whatsapp_number)  # ✅ Correção: removeu `await`
    if thread:
        return thread
    raise HTTPException(status_code=404, detail="Thread not found")

@app.post("/threads/")
async def create_new_thread(whatsapp_number: str, db: Session = Depends(get_db)):
    thread = get_thread_by_number(db, whatsapp_number)  # ✅ Correção: removeu `await`
    if thread:
        return thread
    create_thread(db, whatsapp_number)  # ✅ Correção: removeu `await`
    return {"message": "Thread created successfully"}
