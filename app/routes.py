from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import Thread, Conversation
from .schemas import ThreadCreate, ThreadResponse, ConversationResponse
from typing import Optional

router = APIRouter()

# Endpoint para criar uma nova thread
@router.post("/create-thread/", response_model=dict)
def create_thread(request: ThreadCreate, db: Session = Depends(get_db)):
    try:
        # Garantir que o whatsapp_number não tenha espaços extras
        whatsapp_number = request.whatsapp_number.strip()
        print(f"Verificando a thread para o número: {whatsapp_number}")
        
        # Verificar se já existe uma thread com o número de whatsapp informado
        thread = db.query(Thread).filter(Thread.whatsapp_number == whatsapp_number).first()
        
        if thread:
            return {
                "message": "Thread already exists", 
                "thread": {
                    "thread_id": thread.thread_id, 
                    "whatsapp_number": thread.whatsapp_number
                }
            }
        
        # Caso não exista, cria uma nova thread
        new_thread = Thread(
            whatsapp_number=whatsapp_number,
            external_thread_id=request.external_thread_id.strip() if request.external_thread_id else None
        )
        
        db.add(new_thread)
        db.commit()
        db.refresh(new_thread)
        
        return {
            "message": "Thread created successfully", 
            "thread": {
                "thread_id": new_thread.thread_id, 
                "whatsapp_number": new_thread.whatsapp_number
            }
        }
    
    except Exception as e:
        print(f"Erro ao criar thread: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar thread: {str(e)}")

# Endpoint para verificar a existência de uma thread
@router.get("/check-thread/{whatsapp_number}")
def check_thread(whatsapp_number: str, db: Session = Depends(get_db)):
    try:
        # Garantir que o whatsapp_number não tenha espaços extras
        whatsapp_number = whatsapp_number.strip()
        print(f"Verificando a thread para o número: {whatsapp_number}")
        
        # Verificar se já existe uma thread com o número de whatsapp informado
        thread = db.query(Thread).filter(Thread.whatsapp_number == whatsapp_number).first()
        
        if thread:
            return {
                "exists": True, 
                "thread": {
                    "thread_id": thread.thread_id, 
                    "whatsapp_number": thread.whatsapp_number
                }
            }
        else:
            return {"exists": False}
    
    except Exception as e:
        print(f"Erro ao verificar a thread: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao verificar a thread: {str(e)}")

# Endpoint para recuperar conversa por thread_id
@router.get("/threads/{thread_id}/conversation", response_model=Optional[ConversationResponse])
def get_conversation(thread_id: int, db: Session = Depends(get_db)):
    try:
        # Recupera a conversa associada ao thread_id
        conversation = db.query(Conversation).filter(Conversation.thread_id == thread_id).first()
        
        if conversation:
            return conversation
        else:
            raise HTTPException(status_code=404, detail="Conversation not found")
    
    except Exception as e:
        print(f"Erro ao recuperar a conversa: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar a conversa: {str(e)}")

# Endpoint para atualizar o status da conversa
@router.put("/threads/{thread_id}/status")
def update_conversation(
    thread_id: int, 
    status: str, 
    db: Session = Depends(get_db)
):
    try:
        # Busca a conversa pelo thread_id
        conversation = db.query(Conversation).filter(Conversation.thread_id == thread_id).first()
        
        if conversation:
            # Se encontrar a conversa, atualiza o status
            conversation.status = status  # Assume que tem uma coluna status no modelo
            db.commit()
            
            return {"message": f"Status updated to {status} for thread_id {thread_id}"}
        else:
            raise HTTPException(status_code=404, detail="Conversation not found")
    
    except Exception as e:
        print(f"Erro ao atualizar status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar status: {str(e)}")
