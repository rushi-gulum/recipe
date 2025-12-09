# OpenAI embeddings (new API)
import os
import math
import time
from typing import List
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
OPENAI_BATCH_SIZE = int(os.getenv("OPENAI_BATCH_SIZE", 32))
OPENAI_RETRY_SECONDS = float(os.getenv("OPENAI_RETRY_SECONDS", 1.0))

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing in environment (.env)")

try:
    from openai import OpenAI
except Exception as e:
    raise RuntimeError("Install the official openai package: pip install openai") from e

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here" else None


class Embedder:
    """
    Official OpenAI embedder (text-embedding-3-*).
    - Batches inputs to avoid hitting request size limits.
    - Retries on transient errors with exponential backoff.
    """

    def __init__(self, model: str = None):
        self.model = model or OPENAI_EMBED_MODEL
        self.client = client
        if self.client is None:
            logger.warning(f"[Embedder] OpenAI API key not configured - embeddings will not work")
        else:
            logger.info(f"[Embedder] Using OpenAI embed model: {self.model}")

    def embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        
        if self.client is None:
            logger.error("[Embedder] OpenAI client not configured")
            # Return dummy embeddings for testing
            return [[0.0] * 1536 for _ in texts]

        # simple batching
        out = []
        n = len(texts)
        batch = OPENAI_BATCH_SIZE or 1
        for i in range(0, n, batch):
            chunk = texts[i : i + batch]
            tries = 0
            while True:
                try:
                    resp = self.client.embeddings.create(model=self.model, input=chunk)
                    # response.data length equals len(chunk)
                    out.extend([d.embedding for d in resp.data])
                    break
                except Exception as e:
                    tries += 1
                    sleep = OPENAI_RETRY_SECONDS * (2 ** (tries - 1))
                    logger.warning(f"[Embedder] embedding batch failed (try={tries}) -> {e}. retrying in {sleep:.1f}s")
                    time.sleep(sleep)
                    if tries >= 5:
                        logger.error(f"OpenAI embedding failed after {tries} attempts: {e}")
                        # Return dummy embeddings as fallback
                        return [[0.0] * 1536 for _ in texts]
        return out


# Legacy class for backward compatibility
class OpenAIEmbeddings:
    def __init__(self, api_key: str = None, model: str = "text-embedding-3-small"):
        self.embedder = Embedder(model)
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        return self.embedder.embed(texts)
        
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        return self.embedder.embed([text])[0]