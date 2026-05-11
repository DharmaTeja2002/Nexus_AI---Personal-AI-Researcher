import logging
from typing import List
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class NexusEmbedder:
    """
    The Translator: Converts raw text into mathematical vectors.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        logger.info(f"🧠 Loading Embedding Model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        logger.info("✅ Embedding Model Loaded.")

    def embed_text(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts).tolist()