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
        if not context_chunks:
            # Condition 1: No documents uploaded or found
            system_prompt = (
                "You are Nexus AI, a brilliant and helpful corporate intelligence assistant. "
                "The user asked a question, but there are no uploaded documents matching this topic. "
                "You must answer their question using your general knowledge of the world. "
                "IMPORTANT: At the very end of your response, you MUST append this exact note on a new line: "
                "\n\n*(Note: This was answered generally from outside world knowledge since no specific documents were found).* "
            )
            user_prompt = f"Question: {question}"
        else:
            # Condition 2: Documents were uploaded and found
            context_str = "\n\n---\n\n".join([c['content'] for c in context_chunks])
            system_prompt = (
                "You are Nexus AI, a smart corporate intelligence assistant. "
                "You have been provided with context snippets extracted from the user's uploaded files. "
                "Answer the user's question based ONLY on these documents, but explain it in a generalized, conversational, and easy-to-understand way. "
                "Use bullet points and paragraphs to format your response nicely."
            )
            user_prompt = f"Context:\n{context_str}\n\nQuestion: {question}"
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3 # Slightly higher temperature for better conversational flow
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error connecting to LLM ({settings.LLM_PROVIDER}): {str(e)}"
