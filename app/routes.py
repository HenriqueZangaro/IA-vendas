from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import insert, select
from .database import get_db
from .models import threads
from pydantic import BaseModel

router = APIRouter()  # ✅ Criando um roteador em vez de FastAPI diretamente

class ThreadCreateRequest(BaseModel):
    whatsapp_number: str
    external_thread_id: str  # Alterado para refletir a nova coluna no banco

@router.post("/create-thread/")
def create_thread(request: ThreadCreateRequest, db: Session = Depends(get_db)):
    query = select(threads).where(threads.c.whatsapp_number == request.whatsapp_number)
    existing_thread = db.scalar(query)  # ✅ fetchone() substituído por scalar()
    
    if existing_thread:
        raise HTTPException(status_code=400, detail="Thread already exists for this phone number.")
    
    stmt = insert(threads).values(
        whatsapp_number=request.whatsapp_number,
        external_thread_id=request.external_thread_id  # Alterado
    )
    db.execute(stmt)
    db.commit()
    
    return {"message": "Thread created successfully", "external_thread_id": request.external_thread_id}

@router.get("/check-thread/{whatsapp_number}")
def check_thread(whatsapp_number: str, db: Session = Depends(get_db)):
    query = select(threads).where(threads.c.whatsapp_number == whatsapp_number)
    thread = db.scalar(query)
    
    if thread:
        return {"exists": True, "external_thread_id": thread.external_thread_id}  # Alterado
    
    return {"exists": False}
