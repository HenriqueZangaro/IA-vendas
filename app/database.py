from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base  # Importando o Base diretamente de models.py

DATABASE_URL = "postgresql://user:password@localhost/dbname"

# Usando o Base para criar o engine
engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Função para criar as tabelas no banco de dados
def create_tables():
    Base.metadata.create_all(bind=engine)

# Função para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
