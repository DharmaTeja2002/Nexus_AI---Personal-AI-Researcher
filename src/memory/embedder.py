import logging
from typing import List
from fastembed import TextEmbedding

logger = logging.getLogger(__name__)

class NexusEmbedder:
    """
    The Translator: Converts raw text into mathematical vectors without PyTorch!
    """
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        logger.info(f"🧠 Loading FastEmbed Model: {model_name}...")
        self.model = TextEmbedding(model_name)
        logger.info("✅ FastEmbed Model Loaded.")

    def embed_text(self, text: str) -> List[float]:
        # fastembed returns a generator of numpy arrays
        return list(self.model.embed([text]))[0].tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [arr.tolist() for arr in list(self.model.embed(texts))]