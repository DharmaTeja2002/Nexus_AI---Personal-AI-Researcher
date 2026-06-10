import json
import psycopg2
from pathlib import Path

# 1. Check the JSON Dump
dump_path = Path("data/output/nexus_memory_dump.json")
if dump_path.exists():
    with open(dump_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        print("=== 📂 BATCH OUTPUT (JSON DUMP) ===")
        print(f"Total Elements Extracted: {data.get('total_elements')}")
        print(f"Total Files Processed: {len(data.get('files_processed', []))}")
        print("Files:")
        for file in data.get('files_processed', []):
            print(f"  - {file}")
else:
    print("❌ JSON Dump not found!")

# 2. Check the PostgreSQL Database
print("\n=== 💾 VECTOR DATABASE (PostgreSQL) ===")
try:
    conn = psycopg2.connect(
        dbname="nexus_db", user="nexus_user", password="nexus_pass", host="localhost", port=5432
    )
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM nexus_memory;")
    count = cursor.fetchone()[0]
    print(f"Total Vectors Indexed in Database: {count}")
    
    # Let's see what source files are actually in the DB
    cursor.execute("SELECT DISTINCT source_file FROM nexus_memory;")
    sources = cursor.fetchall()
    print("Files Indexed in Database:")
    for src in sources:
        print(f"  - {src[0]}")
        
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Database connection failed: {e}")
