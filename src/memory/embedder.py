from sentence_transformers import SentenceTransformer
from typing import List

class NexusEmbedder:
    """
    The Translator: Converts raw text into mathematical vectors.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        print(f"🧠 Loading Embedding Model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print("✅ Embedding Model Loaded.")

    def embed_text(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts).tolist()