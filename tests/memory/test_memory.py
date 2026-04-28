import pytest
from src.memory.manager import MemoryManager
from src.memory.embedder import NexusEmbedder
from src.memory.database import NexusVectorStore

def test_memory_indexing_and_retrieval():
    """
    End-to-end test: 
    1. Load JSON dump -> 2. Index into Postgres -> 3. Query for a specific fact.
    """
    # 1. Index the data
    manager = MemoryManager()
    manager.index_json_dump()

    # 2. Test a Query
    embedder = NexusEmbedder()
    db = NexusVectorStore()

    # Change this query to something that is actually in your resume/docs
    query_text = "What are the professional skills of the candidate?" 
    
    query_vector = embedder.embed_text(query_text)
    results = db.query(query_vector, top_k=3)

    # Assertions: The test passes if we get results and they aren't empty
    assert len(results) > 0
    assert "content" in results[0]
    print(f"\n✅ Top Result: {results[0]['content']}")