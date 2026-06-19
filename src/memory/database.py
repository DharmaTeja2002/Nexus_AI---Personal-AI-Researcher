import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, text
from src.core.config import settings
from src.memory.models import Base, NexusMemory, MemoryRecord

logger = logging.getLogger(__name__)

class NexusVectorStore:
    """
    The Vault: Asynchronous PostgreSQL + pgvector interface using SQLAlchemy 2.0.
    """
    def __init__(self):
        # We must use asyncpg driver for asynchronous SQLAlchemy
        if settings.DATABASE_URL:
            db_url = settings.DATABASE_URL
            if db_url.startswith("postgresql://"):
                db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        else:
            db_url = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        self.engine = create_async_engine(db_url, echo=False)
        self.async_session = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def initialize(self):
        """Creates the vector extension and the table schema asynchronously."""
        try:
            async with self.engine.begin() as conn:
                # pgvector extension must exist before table creation
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ PostgreSQL Async Vector Store Initialized.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize database schema: {e}")
            raise

    async def add_documents(self, documents: List[Dict[str, Any]]):
        """
        Validates documents via Pydantic, creates ORM instances, and commits asynchronously.
        """
        # 1. Pydantic Validation
        validated_docs = [MemoryRecord(**doc) for doc in documents]
        
        # 2. ORM Object Creation
        db_records =[
            NexusMemory(
                content=doc.content,
                embedding=doc.embedding,
                source_file=doc.source,
                metadata_=doc.metadata
            ) for doc in validated_docs
        ]
        
        # 3. Async DB Insertion
        try:
            async with self.async_session() as session:
                session.add_all(db_records)
                await session.commit()
                logger.info(f"💾 Successfully indexed {len(db_records)} elements.")
        except Exception as e:
            logger.error(f"❌ Database Insertion Failed: {e}")
            raise

    async def query(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Performs an asynchronous Cosine Similarity search using pgvector ORM.
        """
        try:
            async with self.async_session() as session:
                # SQLAlchemy 2.0 syntax: select(Entity, DistanceLabel).order_by(Distance)
                stmt = (
                    select(
                        NexusMemory, 
                        NexusMemory.embedding.cosine_distance(query_vector).label("distance")
                    )
                    .order_by(NexusMemory.embedding.cosine_distance(query_vector))
                    .limit(top_k)
                )
                
                result = await session.execute(stmt)
                rows = result.all()
                
                return[
                    {
                        "content": row.NexusMemory.content,
                        "source_file": row.NexusMemory.source_file,
                        "metadata": row.NexusMemory.metadata_,
                        "distance": float(row.distance)
                    } for row in rows
                ]
        except Exception as e:
            logger.error(f"❌ Vector Query Failed: {e}")
            raise