# FastAPI entrypoint
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger
from dotenv import load_dotenv

from .rag import RecipeRAG
from .chains import RecipeChain
from .logging_middleware import LoggingMiddleware
from .utils import ensure_recipes_exist

load_dotenv()

# Configure logging
logger.add("logs/backend.log", rotation="10 MB", retention="7 days", enqueue=True)

app = FastAPI(title="Recipe Finder — RAG Engine")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

BASE_DIR = os.path.dirname(__file__)
RECIPE_DIR = os.getenv("RECIPE_DIR", "../data/recipes")
FULL_RECIPE_DIR = os.path.abspath(os.path.join(BASE_DIR, RECIPE_DIR))

ensure_recipes_exist(FULL_RECIPE_DIR)

try:
    # pass recipe_dir as relative to backend
    rag = RecipeRAG(recipe_dir=RECIPE_DIR)
    rag.build_index()  # this will skip embedding if DB + meta exist
    logger.info("[INIT] RAG ready.")
except Exception as e:
    logger.error(f"[INIT] Failed to build RAG index: {e}")
    raise

chain = RecipeChain(rag)

class Query(BaseModel):
    ingredients: list

class SearchQuery(BaseModel):
    query: str
    k: int = 5

@app.get("/")
async def root():
    return {"message": "Recipe RAG API is running"}

@app.post("/find-recipe")
async def find_recipe(q: Query):
    if not isinstance(q.ingredients, list) or not q.ingredients:
        raise HTTPException(status_code=400, detail="Provide a non-empty list of ingredients")
    logger.info(f"[API] Ingredients received: {q.ingredients}")
    return chain.run(q.ingredients)

@app.post("/search")
async def search_recipes(q: SearchQuery):
    """Search for recipes using semantic search"""
    try:
        logger.info(f"[API] Search query: {q.query}, k={q.k}")
        
        # Use RAG pipeline for search
        results = rag.search(q.query, top_k=q.k)
        
        # Format results
        formatted_results = []
        for chunk_id, distance, content in results:
            filename = rag.chunk_to_file.get(chunk_id, "unknown")
            formatted_results.append({
                'id': chunk_id,
                'filename': filename,
                'content': content,
                'score': 1.0 - distance,  # Convert distance to similarity score
                'distance': distance
            })
        
        return {
            "query": q.query,
            "results": formatted_results,
            "count": len(formatted_results)
        }
        
    except Exception as e:
        logger.error(f"[API] Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)