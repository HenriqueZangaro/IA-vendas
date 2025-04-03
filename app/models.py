from sqlalchemy import Table, Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from .database import metadata

threads = Table(
    "threads",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("whatsapp_number", String(15), unique=True, nullable=False, index=True),
    Column("thread_id", Text, nullable=False),  # Text permite strings mais longas que String
    Column("created_at", DateTime, default=func.now(), nullable=False),
    Column("updated_at", DateTime, default=func.now(), onupdate=func.now(), nullable=False),
)
