import json
import asyncio
import logging
from pathlib import Path
from src.core.config import settings
from src.memory.embedder import NexusEmbedder
from src.memory.database import NexusVectorStore

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    The Coordinator: Asynchronously orchestrates the flow from JSON dump to Vector DB.
    """
    def __init__(self):
        self.embedder = NexusEmbedder()
        self.db = NexusVectorStore()

    async def setup(self):
        """Initializes the database connection."""
        await self.db.initialize()

    async def index_json_dump(self):
        """
        Reads the nexus_memory_dump.json and indexes everything into Postgres asynchronously.
        """
        dump_path = settings.OUTPUT_DIR / "nexus_memory_dump.json"
        if not dump_path.exists():
            logger.error("❌ Error: No nexus_memory_dump.json found. Run the ingestion pipeline first!")
            return

        logger.info(f"📖 Loading data from {dump_path}...")
        # Since this is a one-time file read per run, sync open is acceptable, 
        # but for absolute strictness we could use aiofiles.
        with open(dump_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        elements = data.get("elements",[])
        logger.info(f"📦 Found {len(elements)} elements to index.")

        batch_size = 100
        for i in range(0, len(elements), batch_size):
            batch = elements[i : i + batch_size]
            
            # 1. Extract text
            texts = [el['content'] for el in batch]
            
            # 2. Generate embeddings (Run CPU-heavy AI model in a separate thread so we don't block DB I/O)
            embeddings = await asyncio.to_thread(self.embedder.embed_batch, texts)
            
            # 3. Prepare data
            db_ready_data =[]
            for j, el in enumerate(batch):
                db_ready_data.append({
                    "content": el['content'],
                    "embedding": embeddings[j],
                    "source": el['source_file'],
                    "metadata": el.get('metadata', {})
                })
            
            # 4. Save to Postgres asynchronously
            await self.db.add_documents(db_ready_data)
            logger.info(f"✅ Indexed batch {i // batch_size + 1}/{(len(elements)//batch_size)+1}")

        logger.info("🎉 Memory Bank Indexing Complete!")