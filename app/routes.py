from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import insert, select
from .database import get_db
from .models import threads
from pydantic import BaseModel

app = FastAPI()

class ThreadCreateRequest(BaseModel):
    whatsapp_number: str
    thread_id: str  # ✅ Agora está alinhado com o modelo

@app.post("/create-thread/")
def create_thread(request: ThreadCreateRequest, db: Session = Depends(get_db)):
    # Verifica se já existe uma thread para o número
    query = select(threads).where(threads.c.whatsapp_number == request.whatsapp_number)
    existing_thread = db.scalar(query)  # ✅ Correção: usar scalar() em vez de fetchone()
    
    if existing_thread:
        raise HTTPException(status_code=400, detail="Thread already exists for this phone number.")
    
    # Insere uma nova thread
    stmt = insert(threads).values(
        whatsapp_number=request.whatsapp_number,
        thread_id=request.thread_id  # ✅ thread_id agora está no modelo correto
    )
    db.execute(stmt)
    db.commit()
    
    return {"message": "Thread created successfully", "thread_id": request.thread_id}

@app.get("/check-thread/{whatsapp_number}")
def check_thread(whatsapp_number: str, db: Session = Depends(get_db)):
    query = select(threads).where(threads.c.whatsapp_number == whatsapp_number)
    thread = db.scalar(query)  # ✅ Correção: usar scalar()
    
    if thread:
        return {"exists": True, "thread_id": thread.thread_id}
    
    return {"exists": False}
