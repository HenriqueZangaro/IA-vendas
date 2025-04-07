from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import insert, select
from .database import get_db
from .models import threads, conversations  # Adicionamos a tabela 'conversations'
from pydantic import BaseModel
from .crud import get_conversation_by_thread_id, update_conversation_status  # Funções de CRUD

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
        query = select(threads).where(threads.c.whatsapp_number == whatsapp_number)
        existing_thread = db.execute(query).fetchone()

        if existing_thread:
            # Corrigindo a ordem dos valores retornados
            existing_thread_dict = {
                "thread_id": existing_thread[0],  # O ID da thread
                "whatsapp_number": existing_thread[1]      # O número do WhatsApp
            }
            return {"message": "Thread already exists", "thread": existing_thread_dict}

        # Caso não exista, cria uma nova thread
        stmt = insert(threads).values(
            whatsapp_number=whatsapp_number,  # Removendo espaços extras
            external_thread_id=request.external_thread_id.strip()  # Garantindo consistência
        )
        db.execute(stmt)
        db.commit()

        # Retorna a thread recém-criada
        new_thread = db.execute(select(threads).where(threads.c.whatsapp_number == whatsapp_number)).fetchone()

        # Corrigindo a ordem dos valores retornados
        new_thread_dict = {
            "thread_id": new_thread[0],  # O ID da thread
            "whatsapp_number": new_thread[1]      # O número do WhatsApp
        }
        return {"message": "Thread created successfully", "thread": new_thread_dict}

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
        query = select(threads).where(threads.c.whatsapp_number == whatsapp_number)
        thread = db.execute(query).fetchone()

        if thread:
            # Corrigindo a ordem dos valores retornados
            thread_dict = {
                "thread_id": thread[0],  # O ID da thread
                "whatsapp_number": thread[1]      # O número do WhatsApp
            }
            return {"exists": True, "thread": thread_dict}
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
