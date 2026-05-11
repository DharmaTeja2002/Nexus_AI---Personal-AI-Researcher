import asyncio
import logging

# Set up logging so we can see the SQLAlchemy and Pydantic outputs clearly
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NexusAI")

# Import Piece 1: The Ingestion Pipeline
from src.main import run_pipeline

# Import Piece 2: The Hybrid Memory Bank
from src.memory.manager import MemoryManager
from src.memory.embedder import NexusEmbedder

async def run_system():
    print("="*60)
    print("🚀 STARTING NEXUS AI: ENTERPRISE PIPELINE")
    print("="*60)

    # ---------------------------------------------------------
    # PHASE 1: MULTIMODAL INGESTION
    # ---------------------------------------------------------
    print("\n" + "-"*40)
    print("🧠 [PHASE 1] MULTIMODAL INGESTION")
    print("-"*40)
    
    # We await the exact function you wrote in main.py
    await run_pipeline()

    # ---------------------------------------------------------
    # PHASE 2: HYBRID MEMORY BANK (VECTORIZATION & DB)
    # ---------------------------------------------------------
    print("\n" + "-"*40)
    print("💾 [PHASE 2] HYBRID MEMORY BANK")
    print("-"*40)
    
    manager = MemoryManager()
    
    # 1. Setup DB Schema (Async SQLAlchemy - creates tables and pgvector extension safely)
    print("⚙️ Initializing Async Database Connection...")
    await manager.setup()
    
    # 2. Index the newly created JSON dump into Postgres
    print("⚙️ Vectorizing and Indexing data into PostgreSQL...")
    await manager.index_json_dump()

    # ---------------------------------------------------------
    # PHASE 3: SEMANTIC RETRIEVAL TEST (Proof of Life)
    # ---------------------------------------------------------
    print("\n" + "-"*40)
    print("🔎 [PHASE 3] VAULT RETRIEVAL CHECK")
    print("-"*40)
    
    embedder = NexusEmbedder()
    
    # NOTE: You can change this question to match the files you put in your input folder!
    test_query = "What is the summary of this document?" 
    
    print(f'🤔 Asking the Database: "{test_query}"')
    
    # Embed the text (Synchronous CPU task)
    query_vector = embedder.embed_text(test_query)
    
    # Query the DB (Asynchronous I/O task)
    results = await manager.db.query(query_vector, top_k=1)
    
    if results:
        print(f"\n✅ SUCCESS! Top Memory Retrieved (Similarity Distance: {results[0]['distance']:.4f}):")
        print(f"📄 Source File: {results[0]['source_file']}")
        print(f"💬 Content Snippet: {results[0]['content'][:300]}...") # Print first 300 chars
    else:
        print("\n⚠️ No results found. Did the JSON dump have content?")

    print("\n" + "="*60)
    print("🎉 NEXUS AI SYSTEM RUN COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    try:
        asyncio.run(run_system())
    except KeyboardInterrupt:
        print("\n🛑 Master Pipeline stopped by user.")
    except Exception as e:
        print(f"\n❌ FATAL SYSTEM ERROR: {e}")