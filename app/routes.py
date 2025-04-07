from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import insert, select
from .database import get_db
from .models import Thread, Conversation  # Alterado para importar as classes ORM
from pydantic import BaseModel
from .crud import get_conversation_by_thread_id, update_conversation_status, get_thread_by_number, create_thread  # Funções de CRUD

router = APIRouter()

class ThreadCreateRequest(BaseModel):
    whatsapp_number: str
    external_thread_id: str  # Mantendo coerente com a nova coluna no banco

# Endpoint para criar uma nova thread
@router.post("/create-thread/")
def create_thread(request: ThreadCreateRequest, db: Session = Depends(get_db)):
    try:
        # Garantir que o whatsapp_number não tenha espaços extras
        whatsapp_number = request.whatsapp_number.strip()
        print(f"Verificando a thread para o número: {whatsapp_number}")

        # Verificar se já existe uma thread com o número de whatsapp informado
        thread = db.query(Thread).filter(Thread.whatsapp_number == whatsapp_number).first()

        if thread:
            return {"message": "Thread already exists", "thread": {"thread_id": thread.thread_id, "whatsapp_number": thread.whatsapp_number}}

        # Caso não exista, cria uma nova thread
        new_thread = Thread(
            whatsapp_number=whatsapp_number,
            external_thread_id=request.external_thread_id.strip()
        )
        db.add(new_thread)
        db.commit()

        # Retorna a thread recém-criada
        db.refresh(new_thread)  # Atualiza a instância com os dados do banco, incluindo o ID gerado
        return {"message": "Thread created successfully", "thread": {"thread_id": new_thread.thread_id, "whatsapp_number": new_thread.whatsapp_number}}

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
            return {"exists": True, "thread": {"thread_id": thread.thread_id, "whatsapp_number": thread.whatsapp_number}}
        else:
            return {"exists": False}

    except Exception as e:
        print(f"Erro ao verificar a thread: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao verificar a thread: {str(e)}")

# Novo endpoint para recuperar a conversa existente usando thread_id
@router.get("/threads/{thread_id}/conversation")
def get_conversation(thread_id: str, db: Session = Depends(get_db)):
    try:
        # Recupera o histórico da conversa associada ao thread_id
        conversation = get_conversation_by_thread_id(db, thread_id)
        
        if conversation:
            return {"exists": True, "conversation": conversation}
        else:
            raise HTTPException(status_code=404, detail="Conversation not found")
    except Exception as e:
        print(f"Erro ao recuperar a conversa: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar a conversa: {str(e)}")

# Novo endpoint para atualizar o status da conversa
@router.put("/threads/{thread_id}/status")
def update_conversation(thread_id: str, status: str, db: Session = Depends(get_db)):
    try:
        # Atualiza o status da conversa associada ao thread_id
        updated_conversation = update_conversation_status(db, thread_id, status)
        
        if updated_conversation:
            return {"message": f"Status updated to {status} for thread_id {thread_id}"}
        else:
            raise HTTPException(status_code=404, detail="Conversation not found")
    except Exception as e:
        print(f"Erro ao atualizar status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar status: {str(e)}")
