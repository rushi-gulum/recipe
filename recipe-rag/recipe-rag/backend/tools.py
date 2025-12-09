# backend/tools.py
from typing import List, Tuple
import re

ING_LINE_PATTERNS = [
    r"^\-\s*(.*)$",
    r"^\*\s*(.*)$",
    r"^\d+\.\s*(.*)$",
    r"^\d+\s+(.*)$",
    r"^(.*:)$",
    r"^\s*(.*\w.*)\s*$"
]

def extract_ingredients_from_text(text: str) -> List[str]:
    lines = [l.rstrip() for l in text.splitlines()]
    ingredients = []
    start = None
    for i, l in enumerate(lines):
        if l.strip().lower().startswith("ingredients"):
            start = i + 1
            break
    snippet = lines[start:start+120] if start is not None else lines[:40]
    for line in snippet:
        if not line.strip():
            continue
        for pat in ING_LINE_PATTERNS:
            m = re.match(pat, line.strip())
            if m:
                ing = m.group(1).strip()
                ing = re.sub(r"\(.*?\)", "", ing)
                ing = re.sub(r"^\d+(\.\d+)?\s*(cup|cups|tbsp|tsp|grams|g|kg|ml|l)\b", "", ing, flags=re.I)
                ing = re.sub(r"[0-9/]+", "", ing).strip()
                if ing:
                    ingredients.append(ing.lower().rstrip(","))
                break
    seen = set()
    out = []
    for it in ingredients:
        if it not in seen:
            seen.add(it)
            out.append(it)
    return out

def ingredient_matcher_tool(user_ingredients: List[str], recipe_text: str) -> Tuple[List[str], List[str]]:
    recipe_ings = extract_ingredients_from_text(recipe_text)
    matches = []
    normalized_user = [u.lower().strip() for u in user_ingredients]
    for u in normalized_user:
        for r in recipe_ings:
            if u in r or r in u:
                matches.append(u)
                break
    return list(set(matches)), recipe_ings

def recipe_search_tool(user_ingredients: List[str], retrieved_chunks):
    from collections import defaultdict
    groups = defaultdict(list)
    for rid, dist, chunk in retrieved_chunks:
        filename = rid.split("::")[0]
        groups[filename].append((rid, dist, chunk))
    best = None
    best_score = -1
    best_text = None
    for fname, chunks in groups.items():
        full = "\n".join([c for (_, _, c) in chunks])
        matches, recipe_ings = ingredient_matcher_tool(user_ingredients, full)
        score = len(matches)
        if score > best_score:
            best_score = score
            best = fname
            best_text = full
    return {"recipe_id": best, "score": best_score, "recipe_text": best_text}

def shopping_list_tool(user_ingredients: List[str], recipe_text: str):
    matches, recipe_ings = ingredient_matcher_tool(user_ingredients, recipe_text)
    missing = [ri for ri in recipe_ings if not any((m in ri or ri in m) for m in matches)]
    return missing