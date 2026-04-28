import asyncio
import json
from pathlib import Path
from src.core.config import settings
from src.ingestion.dispatcher import UnifiedIngestor
from src.ingestion.schemas import IngestionResponse

async def run_pipeline():
    print("DEBUG: [1] Entry point reached")
    print("🚀 NexusAI Ingestion Pipeline Starting...")
    
    print("DEBUG: [2] Initializing UnifiedIngestor...")
    ingestor = UnifiedIngestor()
    
    all_elements = []
    processed_files = set()

    print(f"DEBUG: [3] Checking input directory: {settings.INPUT_DIR}")
    if not settings.INPUT_DIR.exists():
        print(f"❌ ERROR: Input directory {settings.INPUT_DIR} does not exist!")
        return

    # Let's see how many files are actually there before we start
    files_found = list(settings.INPUT_DIR.iterdir())
    print(f"DEBUG: [4] Found {len(files_found)} total items in input folder.")

    print("DEBUG: [5] Starting async loop...")
    try:
        async for element in ingestor.process_all(settings.INPUT_DIR):
            if element.source_file not in processed_files:
                print(f"📦 Processing and extracting elements from: {element.source_file}...")
                processed_files.add(element.source_file)
                
            all_elements.append(element)
    except Exception as e:
        print(f"❌ CRITICAL ERROR during streaming: {e}")

    print("DEBUG: [6] Streaming finished.")
    
    # 2. Wrap everything in our Unified Response Schema
    print("DEBUG: [7] Creating final response object...")
    final_response = IngestionResponse(
        total_elements=len(all_elements),
        files_processed=list(processed_files),
        elements=all_elements
    )

    # 3. Save to the output folder
    output_path = settings.OUTPUT_DIR / "nexus_memory_dump.json"
    print(f"DEBUG: [8] Saving to {output_path}...")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_response.model_dump_json(indent=2))

    print(f"\n✅ Pipeline Complete!")
    print(f"📄 Final JSON saved to: {output_path}")
    print(f"📊 Total Files Processed: {len(processed_files)}")
    print(f"📊 Total Elements Captured: {len(all_elements)}")

if __name__ == "__main__":
    print("DEBUG: [0] Script started. Calling asyncio.run()...")
    try:
        asyncio.run(run_pipeline())
    except KeyboardInterrupt:
        print("\n🛑 Pipeline stopped by user.")
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")