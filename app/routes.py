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
    try:
        # Garantir que o whatsapp_number não tenha espaços extras
        whatsapp_number = request.whatsapp_number.strip()
        print(f"Verificando a thread para o número: {whatsapp_number}")

        # Verificar se já existe uma thread com o número de whatsapp informado
        query = select(threads).where(threads.c.whatsapp_number == whatsapp_number)
        existing_thread = db.execute(query).fetchone()

        if existing_thread:
            # Acessar os dados da tupla com índices numéricos
            existing_thread_dict = {
                "whatsapp_number": existing_thread[0],
                "external_thread_id": existing_thread[1]
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

        # Acessar os dados da tupla com índices numéricos
        new_thread_dict = {
            "whatsapp_number": new_thread[0],
            "external_thread_id": new_thread[1]
        }
        return {"message": "Thread created successfully", "thread": new_thread_dict}

    except Exception as e:
        # Se ocorrer algum erro, capturamos a exceção e retornamos um erro 500 com a descrição
        print(f"Erro ao criar thread: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar thread: {str(e)}")

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
            # Acessar os dados da tupla com índices numéricos
            thread_dict = {
                "whatsapp_number": thread[0],
                "external_thread_id": thread[1]
            }
            return {"exists": True, "thread": thread_dict}
        else:
            return {"exists": False}

    except Exception as e:
        # Captura qualquer exceção inesperada
        print(f"Erro ao verificar a thread: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao verificar a thread: {str(e)}")
