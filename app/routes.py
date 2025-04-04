from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import insert, select
from .database import get_db
from .models import threads
from pydantic import BaseModel

router = APIRouter()

class ThreadCreateRequest(BaseModel):
    whatsapp_number: str
    external_thread_id: str  # Mantendo coerente com a nova coluna no banco

@router.post("/create-thread/")
def create_thread(request: ThreadCreateRequest, db: Session = Depends(get_db)):
    # Verificar se já existe uma thread com o número de whatsapp informado
    query = select(threads).where(threads.c.whatsapp_number == request.whatsapp_number)
    existing_thread = db.execute(query).fetchone()
    
    if existing_thread:
        # Retorna a thread completa (todos os dados da thread) se já existir
        return {"message": "Thread already exists", "thread": dict(existing_thread)}
    
    # Caso não exista, cria uma nova thread
    stmt = insert(threads).values(
        whatsapp_number=request.whatsapp_number.strip(),  # Removendo espaços extras
        external_thread_id=request.external_thread_id.strip()  # Garantindo consistência
    )
    db.execute(stmt)
    db.commit()
    
    # Retorna a thread recém-criada
    new_thread = db.execute(select(threads).where(threads.c.whatsapp_number == request.whatsapp_number)).fetchone()
    return {"message": "Thread created successfully", "thread": dict(new_thread)}

@router.get("/check-thread/{whatsapp_number}")
def check_thread(whatsapp_number: str, db: Session = Depends(get_db)):
    # Verificar se já existe uma thread com o número de whatsapp informado
    query = select(threads).where(threads.c.whatsapp_number == whatsapp_number.strip())
    thread = db.execute(query).fetchone()
    
    if thread:
        # Retorna a thread completa (todos os dados da thread) se a thread existir
        return {"exists": True, "thread": dict(thread)}
    
    return {"exists": False}
