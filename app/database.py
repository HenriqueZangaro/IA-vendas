from .models_base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

# Configuração de log
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://postgres:891ea6f1fe7d3b49fd23@easypanel.singularmodel.com.br:54327/singular?sslmode=disable"

# Adicione echo e pool_pre_ping para diagnóstico
engine = create_engine(
    DATABASE_URL, 
    echo=True,             # Mostra logs detalhados de SQL
    pool_pre_ping=True     # Verifica a conexão antes de usar
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    try:
        print("Tabelas a serem criadas:")
        for table in Base.metadata.tables:
            print(f" - {table}")
        
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        import traceback
        traceback.print_exc()
        logger.error(f"Erro ao criar tabelas: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
