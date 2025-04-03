from sqlalchemy import Table, Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from .database import metadata

threads = Table(
    "threads",
    metadata,
    Column("thread_id", Integer, primary_key=True, index=True),  # Renomeado de "id"
    Column("whatsapp_number", String(15), unique=True, nullable=False, index=True),
    Column("external_thread_id", Text, nullable=False),  # Renomeei para evitar confusão
    Column("created_at", DateTime, default=func.now(), nullable=False),
    Column("updated_at", DateTime, default=func.now(), onupdate=func.now(), nullable=False),
)
