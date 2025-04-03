from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import engine, database, get_db
from .models import metadata
from .routes import router
from .crud import get_thread_by_number, create_thread

app = FastAPI()

# ✅ Inclui as rotas da API
app.include_router(router)

# ✅ Criar tabelas no banco ao iniciar a API
@app.on_event("startup")
async def startup():
    try:
        print("🔄 Criando tabelas no banco de dados...")
        metadata.create_all(engine)
        await database.connect()
        print("✅ Banco de dados conectado!")
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")

# ✅ Desconectar do banco ao desligar a API
@app.on_event("shutdown")
async def shutdown():
    try:
        print("🛑 Desconectando do banco de dados...")
        await database.disconnect()
        print("✅ Banco de dados desconectado!")
    except Exception as e:
        print(f"❌ Erro ao desconectar do banco: {e}")

# ✅ Rota para buscar uma thread por número de WhatsApp
@app.get("/threads/{whatsapp_number}")
async def read_thread(whatsapp_number: str, db: Session = Depends(get_db)):
    thread = get_thread_by_number(db, whatsapp_number)
    if thread:
        return thread
    raise HTTPException(status_code=404, detail="Thread not found")

# ✅ Rota para criar uma nova thread se não existir
@app.post("/threads/")
async def create_new_thread(whatsapp_number: str, db: Session = Depends(get_db)):
    thread = get_thread_by_number(db, whatsapp_number)
    if thread:
        return thread
    create_thread(db, whatsapp_number)
    return {"message": "Thread created successfully"}
