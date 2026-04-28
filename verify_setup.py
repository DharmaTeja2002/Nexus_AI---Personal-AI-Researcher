from src.core.config import settings
import pydantic
import magic

print(f"🚀 Project: {settings.PROJECT_NAME}")
print(f"📂 Input Folder: {settings.INPUT_DIR}")
print(f"📦 Pydantic Version: {pydantic.__version__}")
print("✅ Foundation is ready!")