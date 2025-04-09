from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import get_db
from .models import Thread, Conversation
from .schemas import ThreadCreate, ThreadResponse, ConversationResponse  # Importando os esquemas ThreadResponse e ThreadCreate
from typing import List, Optional

router = APIRouter()

# Endpoint para salvar a thread (não mais criar)
@router.post("/save-thread/", response_model=ThreadResponse)
def save_thread(request: ThreadCreate, db: Session = Depends(get_db)):
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
                    "whatsapp_number": thread.whatsapp_number,
                    "external_thread_id": thread.external_thread_id,
                    "messages": thread.messages  # Incluindo as mensagens salvas
                }
            }

        # Apenas salva a thread criada pela OpenAI (não cria uma nova thread)
        new_thread = Thread(
            whatsapp_number=whatsapp_number,
            external_thread_id=request.external_thread_id.strip() if request.external_thread_id else None
        )
        db.add(new_thread)
        db.commit()
        db.refresh(new_thread)
        
        return {
            "message": "Thread saved successfully",
            "thread": {
                "thread_id": new_thread.thread_id,
                "whatsapp_number": new_thread.whatsapp_number,
                "external_thread_id": new_thread.external_thread_id,  # Este é o thread_id da OpenAI
                "messages": new_thread.messages,  # Retornando as mensagens
                "created_at": new_thread.created_at,
                "updated_at": new_thread.updated_at
            }
        }
    
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
                    "external_thread_id": thread.external_thread_id,
                    "messages": thread.messages  # Incluindo as mensagens salvas
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
        thread = db.query(Thread).filter(Thread.thread_id == thread_id).first()
        
        if not thread:
            raise HTTPException(status_code=404, detail="No thread found for this thread_id")
        
        # Retorna as mensagens associadas ao external_thread_id
        return {"messages": thread.messages}
    except Exception as e:
        print(f"Erro ao recuperar a conversa: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar a conversa: {str(e)}")
