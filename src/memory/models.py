from typing import Dict, Any
from sqlalchemy import Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from pydantic import BaseModel, Field

class Base(DeclarativeBase):
    pass

class NexusMemory(Base):
    """
    SQLAlchemy ORM Model for the 'nexus_memory' table.
    """
    __tablename__ = "nexus_memory"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # 384 dimensions matches the all-MiniLM-L6-v2 output
    embedding: Mapped[Any] = mapped_column(Vector(384))
    source_file: Mapped[str] = mapped_column(Text, nullable=False)
    # Using JSONB for fast indexing and querying of metadata in Postgres
    metadata_: Mapped[Dict[str, Any]] = mapped_column(JSONB, name="metadata")

class MemoryRecord(BaseModel):
    """
    Pydantic Model for strictly validating data before it hits the DB.
    """
    content: str
    embedding: list[float] = Field(..., min_length=384, max_length=384)
    source: str
    metadata: Dict[str, Any]