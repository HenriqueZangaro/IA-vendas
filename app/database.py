from sqlalchemy import create_engine, MetaData
from databases import Database

DATABASE_URL = "postgresql://postgres:891ea6f1fe7d3b49fd23@easypanel.singularmodel.com.br:54327/singular?sslmode=disable"

database = Database(DATABASE_URL)
metadata = MetaData()

engine = create_engine(
    DATABASE_URL
)