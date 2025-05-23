from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import Thread, Conversation
from .schemas import ThreadCreate, ThreadResponse, ConversationResponse
from typing import List, Optional
from datetime import datetime

router = APIRouter()

# Endpoint para salvar a thread
@router.post("/save-thread/", response_model=ThreadResponse)
def save_thread(request: ThreadCreate, db: Session = Depends(get_db)):
    try:
        # Garantir que o whatsapp_number não tenha espaços extras
        whatsapp_number = request.whatsapp_number.strip()
        print(f"Verificando a thread para o número: {whatsapp_number}")
        
        # Verificar se já existe uma thread com o número de whatsapp informado
        thread = db.query(Thread).filter(Thread.whatsapp_number == whatsapp_number).first()
        if thread:
            return ThreadResponse(  # Retorne a resposta usando o modelo ThreadResponse
                thread_id=thread.thread_id,
                whatsapp_number=thread.whatsapp_number,
                external_thread_id=thread.external_thread_id,
                created_at=thread.created_at,
                updated_at=thread.updated_at
            )

        # Caso a thread não exista, cria uma nova
        new_thread = Thread(
            whatsapp_number=whatsapp_number,
            external_thread_id=request.external_thread_id.strip() if request.external_thread_id else None
        )
        db.add(new_thread)
        db.commit()
        db.refresh(new_thread)

        # Retornar a resposta usando o modelo ThreadResponse
        return ThreadResponse(
            thread_id=new_thread.thread_id,
            whatsapp_number=new_thread.whatsapp_number,
            external_thread_id=new_thread.external_thread_id,
            created_at=new_thread.created_at,
            updated_at=new_thread.updated_at
        )
    
    except Exception as e:
        print(f"Erro ao salvar thread: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao salvar thread: {str(e)}")

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
                    "whatsapp_number": thread.whatsapp_number,
                    "external_thread_id": thread.external_thread_id
                }
            }
        else:
            return {"exists": False}
    except Exception as e:
        print(f"Erro ao verificar a thread: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao verificar a thread: {str(e)}")

# Endpoint para recuperar todas as mensagens de uma conversa por thread_id
@router.get("/threads/{thread_id}/conversation", response_model=List[ConversationResponse])
def get_conversation(thread_id: int, db: Session = Depends(get_db)):
    try:
        # Recupera todas as conversas associadas ao thread_id
        conversations = db.query(Conversation).filter(Conversation.thread_id == thread_id).all()
        
        if not conversations:
            raise HTTPException(status_code=404, detail="No conversations found for this thread_id")
        
        # Retorna todas as mensagens
        return conversations  # Retorna a lista de conversas
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
