from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import engine, database, get_db
from .models import metadata
from .routes import router
from .crud import get_conversation_by_thread_id, update_conversation_status

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
def read_thread(whatsapp_number: str, db: Session = Depends(get_db)):
    thread = get_thread_by_number(db, whatsapp_number)
    if thread:
        return {"exists": True, "thread": thread}
    raise HTTPException(status_code=404, detail="Thread not found")

# ✅ Rota para criar uma nova thread se não existir
@app.post("/threads/")
def create_new_thread(whatsapp_number: str, thread_id: str, db: Session = Depends(get_db)):
    try:
        thread = get_thread_by_number(db, whatsapp_number)
        if thread:
            return {"message": "Thread already exists", "thread": thread}
        
        create_thread(db, whatsapp_number, thread_id)
        return {"message": "Thread created successfully", "whatsapp_number": whatsapp_number, "thread_id": thread_id}
    except Exception as e:
        print(f"❌ Erro ao criar thread: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# ✅ Novo endpoint para recuperar a conversa existente usando thread_id
@app.get("/threads/{thread_id}/conversation")
def get_conversation(thread_id: str, db: Session = Depends(get_db)):
    try:
        # Recupera o histórico da conversa associada ao thread_id
        conversation = get_conversation_by_thread_id(db, thread_id)
        
        if conversation:
            return {"exists": True, "conversation": conversation}
        else:
            raise HTTPException(status_code=404, detail="Conversation not found")
    except Exception as e:
        print(f"❌ Erro ao recuperar a conversa: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar a conversa: {e}")

# ✅ Novo endpoint para atualizar o status da conversa
@app.put("/threads/{thread_id}/status")
def update_conversation(thread_id: str, status: str, db: Session = Depends(get_db)):
    try:
        # Atualiza o status da conversa associada ao thread_id
        updated_conversation = update_conversation_status(db, thread_id, status)
        
        if updated_conversation:
            return {"message": f"Status updated to {status} for thread_id {thread_id}"}
        else:
            raise HTTPException(status_code=404, detail="Conversation not found")
    except Exception as e:
        print(f"❌ Erro ao atualizar status: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar status: {e}")
