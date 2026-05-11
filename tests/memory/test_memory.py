import pytest
from src.memory.manager import MemoryManager
from src.memory.embedder import NexusEmbedder

# The @pytest.mark.asyncio decorator tells pytest to run this in an event loop
@pytest.mark.asyncio
async def test_memory_indexing_and_retrieval():
    """
    End-to-end test: 
    1. Load JSON dump -> 2. Index into Postgres -> 3. Query for a specific fact.
    """
    # 1. Index the data
    manager = MemoryManager()
    
    # Must await the setup to initialize the async DB connection and tables
    await manager.setup() 
    
    # Must await the async indexing process
    await manager.index_json_dump()

    # 2. Test a Query
    embedder = NexusEmbedder()
    
    # Change this query to something that is actually in your resume/docs
    query_text = "What are the professional skills of the candidate?" 
    
    # Embedder remains sync (CPU bound), but query is async (I/O bound)
    query_vector = embedder.embed_text(query_text)
    
    # Reusing the initialized database connection from the manager
    results = await manager.db.query(query_vector, top_k=3)

    # Assertions: The test passes if we get results and they aren't empty
    assert len(results) > 0
    assert "content" in results[0]
    
    # Validate the structure of the returned distance
    assert "distance" in results[0]
    assert isinstance(results[0]["distance"], float)
    
    print(f"\n✅ Top Result: {results[0]['content']} (Distance: {results[0]['distance']:.4f})")