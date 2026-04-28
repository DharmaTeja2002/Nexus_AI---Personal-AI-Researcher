import psycopg2
import json
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector
from typing import List, Dict, Any
from src.core.config import settings

class NexusVectorStore:
    """
    The Vault: Stores vectors in PostgreSQL using the pgvector extension.
    """
    def __init__(self):
        self.conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASS
        )
        # This tells Python how to handle the 'vector' type from Postgres
        register_vector(self.conn)
        self._create_table()
        print("✅ PostgreSQL Vector Store Initialized.")

    def _create_table(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS nexus_memory (
                    id SERIAL PRIMARY KEY,
                    content TEXT,
                    embedding vector(384),
                    source_file TEXT,
                    metadata JSONB
                );
            """)
            self.conn.commit()

    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        Inserts documents into the DB. 
        Expected dict: {"content": "...", "embedding": [...], "source": "...", "metadata": {...}}
        """
        data = [
            (doc['content'], doc['embedding'], doc['source'], json.dumps(doc['metadata']))
            for doc in documents
        ]
        
        with self.conn.cursor() as cur:
            execute_values(
                cur, 
                "INSERT INTO nexus_memory (content, embedding, source_file, metadata) VALUES %s",
                data
            )
            self.conn.commit()
        print(f"💾 Successfully indexed {len(documents)} elements into PostgreSQL.")

    def query(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Performs a Cosine Similarity search using the <=> operator.
        """
        with self.conn.cursor() as cur:
            # ADDED ::vector to the %s to explicitly cast the input array to a vector type
            cur.execute(
                "SELECT content, source_file, metadata, embedding <=> %s::vector AS distance "
                "FROM nexus_memory ORDER BY distance ASC LIMIT %s",
                (query_vector, top_k)
            )
            rows = cur.fetchall()
            
            results = []
            for row in rows:
                results.append({
                    "content": row[0],
                    "source_file": row[1],
                    "metadata": row[2],
                    "distance": row[3]
                })
            return results