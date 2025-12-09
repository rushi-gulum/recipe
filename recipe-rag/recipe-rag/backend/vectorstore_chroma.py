# New Chroma (2025) persistent client
import os
from typing import List, Tuple, Dict, Any
from loguru import logger

# Disable ChromaDB telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "False"

import chromadb
from chromadb.config import Settings

PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./vectordata")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "recipes")

class ChromaStore:
    """
    Thin abstraction over Chroma client (duckdb+parquet).
    - Persists in PERSIST_DIR
    - get_collection() will create or return existing.
    """

    def __init__(self, persist_dir: str = None, collection_name: str = None):
        self.persist_dir = persist_dir or PERSIST_DIR
        self.collection_name = collection_name or COLLECTION_NAME
        os.makedirs(self.persist_dir, exist_ok=True)
        
        # Modern ChromaDB configuration (v0.4+)
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        
        # create/get collection
        try:
            try:
                self.col = self.client.get_collection(self.collection_name)
                logger.info(f"[ChromaStore] Found existing collection '{self.collection_name}'")
            except Exception:
                self.col = self.client.create_collection(name=self.collection_name)
                logger.info(f"[ChromaStore] Created new collection '{self.collection_name}'")
            
            logger.info(f"[ChromaStore] Initialized collection '{self.collection_name}' at {self.persist_dir}")
        except Exception as e:
            logger.error(f"[ChromaStore] init error: {e}")
            raise

    def add_documents(self, ids: List[str], texts: List[str], embeddings: List[List[float]]):
        if not ids:
            return
        # Chroma expects list shape align; pass embeddings directly
        self.col.add(ids=ids, documents=texts, embeddings=embeddings)
        logger.info(f"[ChromaStore] added {len(ids)} documents to collection '{self.collection_name}'")

    def query(self, query_embedding: List[float], top_k: int = 5):
        if query_embedding is None:
            return []
        
        # Query for results  
        res = self.col.query(query_embeddings=[query_embedding], n_results=top_k, include=["distances", "documents"])
        
        # Get all IDs to map back to results
        all_data = self.col.get(include=["documents"])
        all_ids = all_data.get("ids", [])
        all_docs = all_data.get("documents", [])
        
        # Create document to ID mapping
        doc_to_id = {}
        for doc_id, doc in zip(all_ids, all_docs):
            doc_to_id[doc] = doc_id
        
        # Map query results back to IDs
        distances = res.get("distances", [[]])[0]
        docs = res.get("documents", [[]])[0]
        out = []
        for dist, doc in zip(distances, docs):
            doc_id = doc_to_id.get(doc, f"unknown_doc")
            out.append((doc_id, float(dist), doc))
        return out

    def count(self):
        try:
            # try collection.count() (if present)
            if hasattr(self.col, "count"):
                return self.col.count()
            # fallback: fetch ids
            r = self.col.get(include=["ids"])
            ids = r.get("ids", [])
            if isinstance(ids, list) and len(ids) > 0:
                return len(ids[0])
            return 0
        except Exception:
            return 0

    def persist(self):
        try:
            # Chroma client persists automatically, but call persist to be safe
            try:
                self.client.persist()
            except Exception:
                pass
            logger.info("[ChromaStore] persisted")
        except Exception as e:
            logger.error(f"[ChromaStore] persist failed: {e}")


# Legacy class for backward compatibility
class ChromaVectorStore:
    def __init__(self, persist_directory: str = "./vectordata"):
        self.chroma_store = ChromaStore(persist_dir=persist_directory)
        
    def setup(self, collection_name: str = "recipes"):
        """Initialize Chroma client and collection"""
        # Already initialized in ChromaStore constructor
        pass
        
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the vector store"""
        if not documents:
            return
            
        ids = [doc.get('id', str(i)) for i, doc in enumerate(documents)]
        texts = [doc.get('content', '') for doc in documents]
        embeddings = [doc.get('embedding', []) for doc in documents]
        
        self.chroma_store.add_documents(ids, texts, embeddings)
        
    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        # This would need an embedder to convert query to embedding
        # For now, return empty list
        return []