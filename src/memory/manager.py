import json
from pathlib import Path
from src.core.config import settings
from src.memory.embedder import NexusEmbedder
from src.memory.database import NexusVectorStore

class MemoryManager:
    """
    The Coordinator: Orchestrates the flow from JSON dump to Vector DB.
    """
    def __init__(self):
        self.embedder = NexusEmbedder()
        self.db = NexusVectorStore()

    def index_json_dump(self):
        """
        Reads the nexus_memory_dump.json and indexes everything into Postgres.
        """
        dump_path = settings.OUTPUT_DIR / "nexus_memory_dump.json"
        if not dump_path.exists():
            print("❌ Error: No nexus_memory_dump.json found. Run the ingestion pipeline first!")
            return

        print(f"📖 Loading data from {dump_path}...")
        with open(dump_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        elements = data.get("elements", [])
        print(f"📦 Found {len(elements)} elements to index.")

        # To be efficient, we process in batches
        batch_size = 100
        for i in range(0, len(elements), batch_size):
            batch = elements[i : i + batch_size]
            
            # 1. Extract text for embedding
            texts = [el['content'] for el in batch]
            
            # 2. Generate embeddings
            embeddings = self.embedder.embed_batch(texts)
            
            # 3. Prepare data for DB
            db_ready_data = []
            for j, el in enumerate(batch):
                db_ready_data.append({
                    "content": el['content'],
                    "embedding": embeddings[j],
                    "source": el['source_file'],
                    "metadata": el['metadata']
                })
            
            # 4. Save to Postgres
            self.db.add_documents(db_ready_data)
            print(f"✅ Indexed batch {i // batch_size + 1}/{(len(elements)//batch_size)+1}")

        print("\n🎉 Memory Bank Indexing Complete!")