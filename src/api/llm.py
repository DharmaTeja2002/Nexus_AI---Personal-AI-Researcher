import openai
from src.core.config import settings

class LLMClient:
    def __init__(self):
        if settings.LLM_PROVIDER.lower() == "local":
            # Connect to LM Studio / Ollama
            self.client = openai.AsyncOpenAI(
                base_url=settings.LOCAL_LLM_URL,
                api_key="lm-studio" # Local instances usually don't care, but the SDK requires a string
            )
            self.model = settings.LOCAL_LLM_MODEL
            print(f"🤖 LLM Router: Configured to use LOCAL LLM at {settings.LOCAL_LLM_URL}")
        elif settings.LLM_PROVIDER.lower() == "groq":
            # Connect to Groq Cloud API
            if not settings.GROQ_API_KEY:
                raise ValueError("GROQ_API_KEY is missing but provider is set to 'groq'")
            self.client = openai.AsyncOpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=settings.GROQ_API_KEY
            )
            self.model = "llama-3.1-8b-instant" # Fast, smart default for Groq free tier
            print("🤖 LLM Router: Configured to use GROQ API")
        else:
            # Connect to actual OpenAI
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is missing but provider is set to 'openai'")
            self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = "gpt-4o-mini" # Fast, smart default for paid API
            print("🤖 LLM Router: Configured to use OPENAI API")

    async def generate_rag_response(self, question: str, context_chunks: list) -> str:
        # Build the context string
        context_str = "\n\n---\n\n".join([c['content'] for c in context_chunks])
        
        system_prompt = (
            "You are Nexus AI, a helpful, precise, and highly detailed corporate intelligence assistant. "
            "You will be given a user question and several context snippets extracted from the company's internal files. "
            "Answer the question based ONLY on the provided context. "
            "IMPORTANT: Always provide a comprehensive, detailed explanation. Use bullet points and paragraphs to format your response thoroughly, expanding on the context provided. "
            "If the answer is not in the context, say 'I don't know based on the provided documents.' Do not hallucinate."
        )
        
        user_prompt = f"Context:\n{context_str}\n\nQuestion: {question}"
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2 # low temp for factuality
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error connecting to LLM ({settings.LLM_PROVIDER}): {str(e)}"
