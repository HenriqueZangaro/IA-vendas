from .models_base import Base  # Agora importando Base de models_base.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:891ea6f1fe7d3b49fd23@easypanel.singularmodel.com.br:54327/singular?sslmode=disable"

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
