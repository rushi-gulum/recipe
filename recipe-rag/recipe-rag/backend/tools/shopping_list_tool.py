# Shopping list generation tool
from typing import List, Dict, Any
import logging
from .ingredient_matcher import ingredient_matcher_tool

logger = logging.getLogger(__name__)

class ShoppingListTool:
    def __init__(self):
        pass
        
    def generate_shopping_list(self, recipes: List[Dict[str, Any]]) -> List[str]:
        """Generate a shopping list from selected recipes"""
        # This would combine ingredients from multiple recipes
        pass

def shopping_list_tool(user_ingredients: List[str], recipe_text: str):
    """
    Generate a shopping list of missing ingredients for a recipe
    
    Args:
        user_ingredients: List of ingredients the user already has
        recipe_text: Full recipe text to extract ingredients from
        
    Returns:
        List of missing ingredients needed for the recipe
    """
    matches, recipe_ings = ingredient_matcher_tool(user_ingredients, recipe_text)
    
    # Find ingredients in recipe that aren't matched by user ingredients
    missing = [ri for ri in recipe_ings if not any((m in ri or ri in m) for m in matches)]
    
    return missing