import asyncio
import subprocess
import sys

async def run_full_pipeline():
    print("🚀 === STEP 1: STARTING MULTIMODAL INGESTION ===")
    # Runs the ingestion process
    ingest_process = subprocess.run(["uv", "run", "python", "-m", "src.main"])
    
    if ingest_process.returncode != 0:
        print("❌ Ingestion failed. Stopping pipeline.")
        return

    print("\n🚀 === STEP 2: INDEXING INTO MEMORY BANK ===")
    # Runs the memory indexing and test query
    memory_process = subprocess.run(["uv", "run", "pytest", "tests/memory/test_memory.py"])

    if memory_process.returncode == 0:
        print("\n✨ ALL PIECES COMPLETE: Your data is now in the Vector Database!")
    else:
        print("\n❌ Memory indexing failed.")

if __name__ == "__main__":
    asyncio.run(run_full_pipeline())