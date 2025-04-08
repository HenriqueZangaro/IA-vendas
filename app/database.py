from .models_base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from sqlalchemy import inspect

# Configuração de log
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# URL de conexão com o banco de dados PostgreSQL
DATABASE_URL = "postgresql://postgres:891ea6f1fe7d3b49fd23@easypanel.singularmodel.com.br:54327/singular?sslmode=disable"

# Criação do engine com opções de diagnóstico
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Mostra logs detalhados de SQL
    pool_pre_ping=True  # Verifica a conexão antes de usar
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    try:
        print("🔍 Detalhes da criação de tabelas:")
        # Verifica se as tabelas já existem
        existing_tables = Base.metadata.tables.keys()
        print(f"Tabelas definidas no modelo: {list(existing_tables)}")
        
        # Tenta criar as tabelas
        Base.metadata.create_all(bind=engine)
        
        # Confirmação de criação
        print("✅ Processo de criação de tabelas concluído.")
        
        # Verifica novamente as tabelas
        with engine.connect() as connection:
            inspector = inspect(engine)
            for table_name in existing_tables:
                columns = inspector.get_columns(table_name)
                print(f"\nTabela: {table_name}")
                for column in columns:
                    print(f" - {column['name']}: {column['type']}")
    except Exception as e:
        print(f"❌ Erro detalhado ao criar tabelas: {e}")
        import traceback
        traceback.print_exc()
        logger.error(f"Erro ao criar tabelas: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
