import asyncio
from pathlib import Path
from src.ingestion.dispatcher import UnifiedIngestor
from src.core.config import settings

async def main():
    ingestor = UnifiedIngestor()
    print("🚀 Starting Ingestion Process...")
    
    count = 0
    async for element in ingestor.process_all(settings.INPUT_DIR):
        print(f"\n--- Element {count} ---")
        print(f"Type: {element.element_type}")
        print(f"Source: {element.source_file}")
        print(f"Content: {element.content}")
        count += 1
    
    print(f"\n✅ Finished! Processed {count} elements.")

if __name__ == "__main__":
    asyncio.run(main())