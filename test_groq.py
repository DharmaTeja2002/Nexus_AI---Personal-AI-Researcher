import asyncio
from src.api.llm import LLMClient
from src.core.config import settings

async def main():
    print(f"Testing provider: {settings.LLM_PROVIDER}")
    try:
        client = LLMClient()
        response = await client.generate_rag_response(
            "If you can read this, just reply with 'Connection Successful!'", 
            [{"content": "No context needed."}]
        )
        print(f"\n✅ GROQ RESPONSE: {response}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

asyncio.run(main())
