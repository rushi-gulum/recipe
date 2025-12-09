# Final ranking logic + tools
import os
import numpy as np
from typing import List, Dict, Any
from loguru import logger

from .rag import RecipeRAG
from .tools import ingredient_matcher_tool, shopping_list_tool, recipe_search_tool


class RecipeChain:
    def __init__(self, rag: RecipeRAG = None):
        self.rag = rag or RecipeRAG()
        self.alpha = float(os.getenv("RERANK_EMBED_WEIGHT", 0.75))
        self.beta = float(os.getenv("RERANK_ING_WEIGHT", 0.25))
        self.top_k_raw = int(os.getenv("RERANK_TOPK_RAW", 5))
        self.tools = [
            ingredient_matcher_tool,
            shopping_list_tool,
            recipe_search_tool
        ]

    def run(self, ingredients: List[str]) -> Dict[str, Any]:
        query = " ".join(ingredients)
        logger.info(f"[Chain] Running chain for query: {query}")

        # embed query
        query_emb = self.rag.embedder.embed([query])[0]
        # Convert numpy array to list if needed
        if hasattr(query_emb, 'tolist'):
            query_emb = query_emb.tolist()
        query_emb = np.array(query_emb)
        query_emb = query_emb / (np.linalg.norm(query_emb) + 1e-12)

        # retrieve
        retrieved = self.rag.store.query(query_emb.tolist(), top_k=self.top_k_raw)
        logger.info(f"[Chain] Retrieved {len(retrieved)} candidate chunks")

        if not retrieved:
            return {"error": "No recipes found"}

        # group by filename
        groups = {}
        for chunk_id, score, chunk_text in retrieved:
            recipe_name = chunk_id.split("::")[0]
            groups.setdefault(recipe_name, {"ids": [], "texts": []})
            groups[recipe_name]["ids"].append(chunk_id)
            groups[recipe_name]["texts"].append(chunk_text)

        reranked = []
        for recipe_name, info in groups.items():
            # average embedding for recipe: try to get chunk embeddings from metadata file via rag.store? (not stored in chroma_meta to save space).
            # fallback: embed the concatenated texts (cheap because groups are small)
            avg_emb = np.asarray(self.rag.embedder.embed(["\n".join(info["texts"])])).mean(axis=0)
            avg_emb = avg_emb / (np.linalg.norm(avg_emb) + 1e-12)
            embed_score = float(np.dot(query_emb, avg_emb))

            full_text = "\n".join(info["texts"])
            matches, recipe_ing = ingredient_matcher_tool(ingredients, full_text)
            ing_score = len(matches) / max(1, len(recipe_ing))

            final_score = self.alpha * embed_score + self.beta * ing_score
            reranked.append((final_score, recipe_name, full_text, matches, recipe_ing))

        reranked.sort(key=lambda x: x[0], reverse=True)
        best_score, best_recipe_id, best_text, matched_ing, all_ing = reranked[0]
        missing = shopping_list_tool(ingredients, best_text)

        return {
            "recipe_id": best_recipe_id,
            "score": best_score,
            "recipe": best_text,
            "matched_ingredients": matched_ing,
            "missing_ingredients": missing,
        }
        
    def rank_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply final ranking logic to search results"""
        # Sort by relevance score (highest first)
        return sorted(results, key=lambda x: x.get('score', 0), reverse=True)
        
    def process_query(self, query: str, user_ingredients: List[str] = None) -> Dict[str, Any]:
        """Process a recipe search query through the complete chain"""
        if user_ingredients:
            # Use ingredient-based search
            return self.run(user_ingredients)
        else:
            # Use semantic search
            if not self.rag._index_loaded:
                self.rag.build_index()
            
            results = self.rag.search(query, top_k=5)
            formatted_results = []
            
            for chunk_id, distance, content in results:
                filename = self.rag.chunk_to_file.get(chunk_id, "unknown")
                formatted_results.append({
                    'id': chunk_id,
                    'filename': filename,
                    'content': content,
                    'score': 1.0 - distance,
                    'distance': distance
                })
            
            return {
                "query": query,
                "user_ingredients": user_ingredients or [],
                "results": self.rank_results(formatted_results),
                "tools_used": [tool.__name__ for tool in self.tools]
            }
    
    def search_with_ingredients(self, user_ingredients: List[str], retrieved_chunks) -> Dict[str, Any]:
        """Search for recipes using ingredient matching"""
        return recipe_search_tool(user_ingredients, retrieved_chunks)
    
    def generate_shopping_list(self, user_ingredients: List[str], recipe_text: str) -> List[str]:
        """Generate shopping list for a recipe"""
        return shopping_list_tool(user_ingredients, recipe_text)
    
    def match_ingredients(self, user_ingredients: List[str], recipe_text: str) -> tuple:
        """Match user ingredients with recipe ingredients"""
        return ingredient_matcher_tool(user_ingredients, recipe_text)