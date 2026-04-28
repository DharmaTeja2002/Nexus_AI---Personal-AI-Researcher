import pytest
from pathlib import Path
from src.ingestion.dispatcher import UnifiedIngestor
from src.core.config import settings

# This is the "Fixture". It tells pytest: "Whenever a test asks for 'ingestor', 
# create a new UnifiedIngestor() and give it to them."
@pytest.fixture
def ingestor():
    return UnifiedIngestor()

@pytest.mark.asyncio
async def test_route_text_file(ingestor):
    test_file = settings.INPUT_DIR / "test_route.txt"
    test_file.write_text("Hello World")
    
    elements = await ingestor.ingest_file(test_file)
    
    assert len(elements) > 0
    # Note: We check for "Hello World" because we are using the REAL TextParser now
    assert "Hello World" in elements[0].content 
    test_file.unlink()

@pytest.mark.asyncio
async def test_unknown_file_type(ingestor):
    test_file = settings.INPUT_DIR / "unknown.bin"
    test_file.write_bytes(b'\x00\xFF\x00\xFF') 
    
    elements = await ingestor.ingest_file(test_file)
    
    assert elements == []
    test_file.unlink()