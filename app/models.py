from sqlalchemy import Table, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import metadata

threads = Table(
    "threads",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("whatsapp_number", String(15), unique=True, nullable=False),
    Column("thread_id", String, nullable=False),  # Nova coluna para armazenar a thread
    Column("created_at", DateTime, default=func.now(), nullable=False),
    Column("updated_at", DateTime, default=func.now(), onupdate=func.now(), nullable=False),
)
