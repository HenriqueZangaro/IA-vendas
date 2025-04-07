from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData
from databases import Database
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "postgresql://postgres:891ea6f1fe7d3b49fd23@easypanel.singularmodel.com.br:54327/singular?sslmode=disable"

# Conexão com o banco de dados
database = Database(DATABASE_URL)

# Metadados para a criação das tabelas
metadata = MetaData()

# Definir o objeto Base que irá ser usado para os modelos
Base = declarative_base(metadata=metadata)

# Criar engine do SQLAlchemy
engine = create_engine(DATABASE_URL)

# Sessão local para o banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Função para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
