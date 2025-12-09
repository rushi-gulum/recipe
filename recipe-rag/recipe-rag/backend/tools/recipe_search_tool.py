# Recipe search tool
from typing import List, Dict, Any
from collections import defaultdict
import logging
from .ingredient_matcher import ingredient_matcher_tool

logger = logging.getLogger(__name__)

class RecipeSearchTool:
    def __init__(self):
        pass
        
    def search_recipes(self, query: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search for recipes based on query and filters"""
        # This would be implemented to work with the RAG pipeline
        pass

def recipe_search_tool(user_ingredients: List[str], retrieved_chunks):
    """
    Search for the best recipe match based on user ingredients
    
    Args:
        user_ingredients: List of ingredients the user has
        retrieved_chunks: List of (recipe_id, distance, chunk) tuples from vector search
        
    Returns:
        Dict with best recipe info: recipe_id, score, and recipe_text
    """
    groups = defaultdict(list)
    
    # Group chunks by filename
    for rid, dist, chunk in retrieved_chunks:
        filename = rid.split("::")[0]
        groups[filename].append((rid, dist, chunk))
    
    best = None
    best_score = -1
    best_text = None
    
    # Find recipe with most ingredient matches
    for fname, chunks in groups.items():
        # Combine all chunks for this recipe
        full = "\n".join([c for (_, _, c) in chunks])
        matches, recipe_ings = ingredient_matcher_tool(user_ingredients, full)
        score = len(matches)
        
        if score > best_score:
            best_score = score
            best = fname
            best_text = full
    
    return {"recipe_id": best, "score": best_score, "recipe_text": best_text}