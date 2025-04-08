from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import engine, get_db
from .models import Thread, Conversation
from .models_base import Base
from .routes import router
from .crud import get_conversation_by_thread_id, update_conversation_status, get_thread_by_number, create_thread
import logging
from sqlalchemy import inspect

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
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar a aplicação: {e}")

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

# Rota para criar uma nova thread se não existir
@app.post("/threads/", operation_id="create_thread")
def create_new_thread(whatsapp_number: str, thread_id: str, db: Session = Depends(get_db)):
    try:
        # Garantir que o whatsapp_number não tenha espaços extras
        whatsapp_number = whatsapp_number.strip()
        print(f"Verificando a thread para o número: {whatsapp_number}")
        # Verificar se já existe uma thread com o número de whatsapp informado
        thread = get_thread_by_number(db, whatsapp_number)
        if thread:
            return {"message": "Thread already exists", "thread": thread}
        # Caso não exista, cria uma nova thread
        create_thread(db, whatsapp_number, thread_id)
        return {"message": "Thread created successfully", "whatsapp_number": whatsapp_number, "thread_id": thread_id}
    except Exception as e:
        print(f"❌ Erro ao criar thread: {e}")
        logger.error(f"Erro ao criar thread: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Função para criar uma nova conversa
def create_conversation(db: Session, thread_id: int, messages: str):  # Alterado para 'messages'
    new_conversation = Conversation(thread_id=thread_id, messages=messages)  # Alterado para 'messages'
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    return new_conversation

# Novo endpoint para criar uma conversa
@app.post("/threads/{thread_id}/conversation", operation_id="create_conversation")
def create_conversation_endpoint(thread_id: str, messages: str, db: Session = Depends(get_db)):  # Alterado para 'messages'
    try:
        conversation = create_conversation(db, int(thread_id), messages)  # Alterado para 'messages'
        return {"message": "Conversation created successfully", "conversation": conversation}
    except Exception as e:
        logger.error(f"Erro ao criar conversa: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Novo endpoint para recuperar a conversa existente usando thread_id
@app.get("/threads/{thread_id}/conversation", operation_id="get_conversation_by_thread_id")
def get_conversation(thread_id: str, db: Session = Depends(get_db)):
    try:
        # Certifique-se de que o thread_id é válido
        thread = db.query(Thread).filter(Thread.thread_id == int(thread_id)).first()
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        # Recupera o histórico da conversa associada ao thread_id
        conversation = get_conversation_by_thread_id(db, thread_id)
        if conversation:
            return {"exists": True, "conversation": conversation}
        else:
            raise HTTPException(status_code=404, detail=f"Conversation for thread_id {thread_id} not found")
    except Exception as e:
        logger.error(f"Erro ao recuperar a conversa: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar a conversa: {e}")

# Novo endpoint para atualizar o status da conversa
@app.put("/threads/{thread_id}/status", operation_id="update_conversation_status")
def update_conversation(thread_id: str, status: str, db: Session = Depends(get_db)):
    try:
        # Verificar se o thread_id existe
        thread = db.query(Thread).filter(Thread.thread_id == int(thread_id)).first()
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        # Atualiza o status de todas as conversas associadas ao thread_id
        conversations = db.query(Conversation).filter(Conversation.thread_id == int(thread_id)).all()
        if not conversations:
            raise HTTPException(status_code=404, detail="No conversations found for the given thread_id")
        
        for conversation in conversations:
            conversation.status = status
        db.commit()
        
        return {"message": f"Status updated to {status} for all conversations with thread_id {thread_id}"}
    except Exception as e:
        logger.error(f"Erro ao atualizar status: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar status: {e}")
