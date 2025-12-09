# Utility functions for tools
from typing import List, Dict, Any, Tuple
import re
import logging

logger = logging.getLogger(__name__)

ING_LINE_PATTERNS = [
    r"^\-\s*(.*)$",
    r"^\*\s*(.*)$",
    r"^\d+\.\s*(.*)$",
    r"^\d+\s+(.*)$",
    r"^(.*:)$",
    r"^\s*(.*\w.*)\s*$"
]

def extract_ingredients_from_text(text: str) -> List[str]:
    """Extract ingredients from recipe text using pattern matching"""
    lines = [l.rstrip() for l in text.splitlines()]
    ingredients = []
    start = None
    
    # Find ingredients section
    for i, l in enumerate(lines):
        if l.strip().lower().startswith("ingredients"):
            start = i + 1
            break
    
    # Extract snippet to parse
    snippet = lines[start:start+120] if start is not None else lines[:40]
    
    for line in snippet:
        if not line.strip():
            continue
        
        for pat in ING_LINE_PATTERNS:
            m = re.match(pat, line.strip())
            if m:
                ing = m.group(1).strip()
                # Clean up ingredient text
                ing = re.sub(r"\(.*?\)", "", ing)  # Remove parentheses
                ing = re.sub(r"^\d+(\.\d+)?\s*(cup|cups|tbsp|tsp|grams|g|kg|ml|l)\b", "", ing, flags=re.I)  # Remove measurements
                ing = re.sub(r"[0-9/]+", "", ing).strip()  # Remove numbers
                if ing:
                    ingredients.append(ing.lower().rstrip(","))
                break
    
    # Remove duplicates while preserving order
    seen = set()
    out = []
    for it in ingredients:
        if it not in seen:
            seen.add(it)
            out.append(it)
    
    return out

def parse_ingredients(ingredient_text: str) -> List[str]:
    """Parse ingredient text into a list of ingredients"""
    return extract_ingredients_from_text(ingredient_text)

def normalize_ingredient_name(ingredient: str) -> str:
    """Normalize ingredient name for matching"""
    return ingredient.lower().strip()

def calculate_recipe_score(recipe: Dict[str, Any], query: str) -> float:
    """Calculate relevance score for a recipe"""
    # Simple scoring based on query terms in content
    content = recipe.get('content', '').lower()
    query_terms = query.lower().split()
    score = sum(1 for term in query_terms if term in content)
    return score / len(query_terms) if query_terms else 0.0