from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import engine, get_db
from .models import Thread, Conversation
from .models_base import Base
from .routes import router
from .crud import get_conversation_by_thread_id, get_thread_by_number  # Remover 'create_thread', pois não cria mais a thread
import logging
from sqlalchemy import inspect
from .schemas import ThreadCreate

# Configuração do logging para DEBUG
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Inclui as rotas da API
app.include_router(router)

# Criar tabelas no banco ao iniciar a API
@app.on_event("startup")
async def startup():
    try:
        print("🔄 Criando tabelas no banco de dados...")
        # Criar tabelas
        Base.metadata.create_all(engine)
        # Verificação detalhada
        inspector = inspect(engine)
        print("\n🔍 Verificação detalhada das tabelas:")
        for table_name in Base.metadata.tables.keys():
            print(f"\nTabela: {table_name}")
            columns = inspector.get_columns(table_name)
            for column in columns:
                print(f" - {column['name']}: {column['type']}")
        print("✅ Banco de dados conectado!")
    except Exception as e:
        print(f"❌ Erro detalhado ao criar as tabelas: {e}")
        import traceback
        traceback.print_exc()
        logger.error(f"Erro ao iniciar a aplicação: {e}")

# Desconectar do banco ao desligar a API
@app.on_event("shutdown")
async def shutdown():
    try:
        print("🛑 Encerrando a aplicação...")
        print("✅ Banco de dados desconectado (gerenciado pelo SQLAlchemy).")
    except Exception as e:
        print(f"❌ Erro ao finalizar a aplicação: {e}")
        logger.error(f"Erro ao finalizar a aplicação: {e}")

# Rota para buscar uma thread por número de WhatsApp
@app.get("/threads/{whatsapp_number}", operation_id="get_thread_by_whatsapp_number")
def read_thread(whatsapp_number: str, db: Session = Depends(get_db)):
    thread = get_thread_by_number(db, whatsapp_number)
    if thread:
        return {"exists": True, "thread": thread}
    raise HTTPException(status_code=404, detail="Thread not found")

# Rota para salvar uma thread recebida
@app.post("/threads/", operation_id="save_thread")
def save_thread(request: ThreadCreate, db: Session = Depends(get_db)):
    try:
        # Garantir que o whatsapp_number não tenha espaços extras
        whatsapp_number = request.whatsapp_number.strip()
        print(f"Verificando a thread para o número: {whatsapp_number}")
        
        # Verificar se já existe uma thread com o número de whatsapp informado
        thread = get_thread_by_number(db, whatsapp_number)
        if thread:
            return {"message": "Thread already exists", "thread": thread}

        # Apenas salva a thread recebida (não cria uma nova)
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
                "created_at": new_thread.created_at,
                "updated_at": new_thread.updated_at
            }
        }
    
    except Exception as e:
        print(f"❌ Erro ao salvar thread: {e}")
        logger.error(f"Erro ao salvar thread: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Função para criar uma nova conversa
def create_conversation(db: Session, thread_id: int, messages: str):
    new_conversation = Conversation(thread_id=thread_id, messages=messages)
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    return new_conversation

# Novo endpoint para criar uma conversa
@app.post("/threads/{thread_id}/conversation", operation_id="create_conversation")
def create_conversation_endpoint(thread_id: str, messages: str, db: Session = Depends(get_db)):
    try:
        # Verificar se a thread existe (associado ao thread_id)
        thread = db.query(Thread).filter(Thread.external_thread_id == thread_id).first()
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        # Criar uma nova conversa associada à thread_id e salvar a mensagem
        new_conversation = Conversation(
            thread_id=thread.thread_id,  # Agora usando o ID da thread existente
            status="iniciado",  # Status inicial da conversa
            messages=messages  # Mensagem recebida ou gerada pela IA
        )

        db.add(new_conversation)
        db.commit()  # Salvar a conversa no banco
        db.refresh(new_conversation)  # Atualiza a instância com os dados do banco

        return {"message": "Conversation created successfully", "conversation": new_conversation}

    except Exception as e:
        logger.error(f"Erro ao criar conversa: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Novo endpoint para recuperar a conversa existente usando thread_id
@app.get("/threads/{thread_id}/conversation", operation_id="get_conversation_by_thread_id")
def get_conversation(thread_id: str, db: Session = Depends(get_db)):
    try:
        thread = db.query(Thread).filter(Thread.thread_id == int(thread_id)).first()
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        conversation = get_conversation_by_thread_id(db, thread_id)
        if conversation:
            return {"exists": True, "conversation": conversation}
        else:
            raise HTTPException(status_code=404, detail=f"Conversation for thread_id {thread_id} not found")
    except Exception as e:
        logger.error(f"Erro ao recuperar a conversa: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar a conversa: {e}")

# Novo endpoint para atualizar o status da última conversa
@app.put("/threads/{thread_id}/status", operation_id="update_conversation_status")
def update_conversation(thread_id: str, status: str, db: Session = Depends(get_db)):
    try:
        # Verificar se o thread_id existe
        thread = db.query(Thread).filter(Thread.thread_id == int(thread_id)).first()
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        # Recupera a última conversa associada ao thread_id (maior ID)
        last_conversation = (
            db.query(Conversation)
            .filter(Conversation.thread_id == int(thread_id))
            .order_by(Conversation.id.desc())  # Ordena por ID em ordem decrescente
            .first()
        )
        if not last_conversation:
            raise HTTPException(status_code=404, detail="No conversations found for the given thread_id")
        
        # Atualiza o status da última conversa
        last_conversation.status = status
        db.commit()  # Commit the change
        return {"message": f"Status updated to '{status}' for the last conversation with thread_id {thread_id}"}
    except Exception as e:
        logger.error(f"Erro ao atualizar status: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar status: {e}")
