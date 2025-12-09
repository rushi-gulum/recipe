# Ingredient matching tool
from typing import List, Dict, Any, Tuple
import logging
from .utils import extract_ingredients_from_text

logger = logging.getLogger(__name__)

class IngredientMatcher:
    def __init__(self):
        pass
        
    def match_ingredients(self, user_ingredients: List[str], recipe_ingredients: List[str]) -> Dict[str, Any]:
        """Match user ingredients against recipe ingredients"""
        return ingredient_matcher_tool(user_ingredients, recipe_ingredients)

def ingredient_matcher_tool(user_ingredients: List[str], recipe_text: str) -> Tuple[List[str], List[str]]:
    """
    Match user ingredients against recipe ingredients extracted from text
    
    Args:
        user_ingredients: List of ingredients the user has
        recipe_text: Full recipe text to extract ingredients from
        
    Returns:
        Tuple of (matched_ingredients, recipe_ingredients)
    """
    recipe_ings = extract_ingredients_from_text(recipe_text)
    matches = []
    normalized_user = [u.lower().strip() for u in user_ingredients]
    
    for u in normalized_user:
        for r in recipe_ings:
            if u in r or r in u:
                matches.append(u)
                break
    
    return list(set(matches)), recipe_ings