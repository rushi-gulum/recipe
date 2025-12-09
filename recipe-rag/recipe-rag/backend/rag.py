# RAG pipeline (Chroma + Embedding + Chunker)
import os
import uuid
import pickle
from typing import List, Dict, Any
from loguru import logger

from .embeddings import Embedder
from .vectorstore_chroma import ChromaStore

# chunk config
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 800))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 100))
PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./vectordata")
META_FILE = os.path.join(PERSIST_DIR, "chroma_meta.pkl")


class RecipeRAG:
    """
    RAG using OpenAI embeddings + Chroma DB.
    - Will not re-embed if vector DB + metadata exists.
    - Stores chunk metadata in chroma_meta.pkl (ids->file, full recipes)
    """

    def __init__(self, recipe_dir: str = "../data/recipes"):
        base = os.path.dirname(__file__)
        self.recipe_dir = os.path.abspath(os.path.join(base, recipe_dir))
        self.embedder = Embedder()
        self.store = ChromaStore()
        # metadata
        self.chunk_to_file: Dict[str, str] = {}
        self.full_recipes: Dict[str, str] = {}
        # load metadata if present
        self._load_meta()
        self._index_loaded = False

    def _chunk_text(self, text: str) -> List[str]:
        text = text.strip()
        if not text:
            return []
        chunks = []
        i = 0
        L = len(text)
        while i < L:
            end = min(i + CHUNK_SIZE, L)
            chunks.append(text[i:end])
            if end == L:
                break
            i = end - CHUNK_OVERLAP
        return chunks

    def _load_meta(self):
        if os.path.exists(META_FILE):
            try:
                with open(META_FILE, "rb") as fh:
                    meta = pickle.load(fh)
                self.chunk_to_file = meta.get("chunk_to_file", {})
                self.full_recipes = meta.get("full_recipes", {})
                logger.info(f"[RAG] loaded metadata (chunks={len(self.chunk_to_file)}, recipes={len(self.full_recipes)})")
            except Exception as e:
                logger.warning(f"[RAG] failed to load metadata: {e}")

    def _save_meta(self):
        try:
            meta = {"chunk_to_file": self.chunk_to_file, "full_recipes": self.full_recipes}
            os.makedirs(PERSIST_DIR, exist_ok=True)
            with open(META_FILE, "wb") as fh:
                pickle.dump(meta, fh)
            logger.info("[RAG] metadata saved")
        except Exception as e:
            logger.error(f"[RAG] metadata save failed: {e}")

    def build_index(self):
        """
        Build index only if Chroma collection is empty OR metadata missing:
         - If collection has vectors and metadata file exists -> load metadata and skip embedding.
         - Otherwise read files, chunk, embed, store in chroma + metadata.
        """
        try:
            count = self.store.count()
        except Exception:
            count = 0

        if count > 0 and self.chunk_to_file:
            logger.info("[RAG] existing vector DB + metadata found — skipping re-embedding")
            self._index_loaded = True
            return

        # else we must (re)create index
        if not os.path.exists(self.recipe_dir):
            logger.warning(f"[RAG] recipe dir not found: {self.recipe_dir}")
            return

        files = [f for f in os.listdir(self.recipe_dir) if f.lower().endswith(".txt")]
        if not files:
            logger.warning("[RAG] no .txt files found in recipe dir")
            return

        ids, texts, embeddings = [], [], []

        logger.info(f"[RAG] Indexing {len(files)} recipe files...")
        for fname in files:
            path = os.path.join(self.recipe_dir, fname)
            with open(path, "r", encoding="utf-8") as fh:
                raw = fh.read().strip()
            self.full_recipes[fname] = raw
            chunks = self._chunk_text(raw)
            if not chunks:
                continue
            logger.info(f"[RAG] {fname}: {len(chunks)} chunks")
            # embed chunks
            chunk_embs = self.embedder.embed(chunks)
            for i, chunk in enumerate(chunks):
                _id = f"{fname}::chunk::{i}::{uuid.uuid4()}"
                ids.append(_id)
                texts.append(chunk)
                embeddings.append(chunk_embs[i])
                self.chunk_to_file[_id] = fname

        if ids:
            self.store.add_documents(ids=ids, texts=texts, embeddings=embeddings)
            self.store.persist()
            self._save_meta()
            self._index_loaded = True
            logger.info(f"[RAG] Indexed {len(ids)} chunks from {len(files)} files")

    def search(self, query: str, top_k: int = 5):
        q_emb = self.embedder.embed([query])[0]
        return self.store.query(q_emb, top_k=top_k)


# Legacy class for backward compatibility
class RAGPipeline:
    def __init__(self):
        self.recipe_rag = RecipeRAG()
        
    def setup(self):
        """Initialize the RAG pipeline components"""
        self.recipe_rag.build_index()
        
    def chunk_documents(self, documents: List[str]) -> List[Dict[str, Any]]:
        """Chunk documents for embedding"""
        chunks = []
        for i, doc in enumerate(documents):
            doc_chunks = self.recipe_rag._chunk_text(doc)
            for j, chunk in enumerate(doc_chunks):
                chunks.append({
                    'id': f"doc_{i}_chunk_{j}",
                    'content': chunk,
                    'source_doc': i
                })
        return chunks
        
    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a query"""
        if not self.recipe_rag._index_loaded:
            self.recipe_rag.build_index()
            
        results = self.recipe_rag.search(query, top_k=k)
        
        # Convert to expected format
        formatted_results = []
        for chunk_id, distance, content in results:
            filename = self.recipe_rag.chunk_to_file.get(chunk_id, "unknown")
            formatted_results.append({
                'id': chunk_id,
                'filename': filename,
                'content': content,
                'score': 1.0 - distance,  # Convert distance to similarity score
                'distance': distance
            })
        
        return formatted_results