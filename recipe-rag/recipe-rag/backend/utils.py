# Utility functions to ensure recipe folder etc
import os
import logging
from pathlib import Path
from loguru import logger

def ensure_recipes_exist(recipe_dir: str):
    if not os.path.exists(recipe_dir):
        os.makedirs(recipe_dir, exist_ok=True)
        sample = os.path.join(recipe_dir, "sample_tomato_rice.txt")
        with open(sample, "w", encoding="utf-8") as f:
            f.write("""
Tomato Garlic Rice

Ingredients:
- 1 cup Rice
- 2 Tomatoes
- 1 Onion
- 3 cloves Garlic
- 1 tbsp Butter
- Salt to taste

Instructions:
1. Wash rice.
2. Saute onion and garlic.
3. Add tomato and cook.
4. Add rice and water, simmer until done.
""")
        logger.info(f"[Utils] created sample recipe at {sample}")

def ensure_directories():
    """Ensure all required directories exist"""
    directories = [
        "data/recipes",
        "data/ground_truth",
        "data/samples",
        "vectordata",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")

def load_recipes(recipes_dir: str = "data/recipes") -> list:
    """Load all recipe files from the recipes directory"""
    recipes = []
    recipes_path = Path(recipes_dir)
    
    if not recipes_path.exists():
        logger.warning(f"Recipes directory does not exist: {recipes_dir}")
        # Create directory and sample recipe
        ensure_recipes_exist(recipes_dir)
        recipes_path = Path(recipes_dir)
    
    for recipe_file in recipes_path.glob("*.txt"):
        try:
            with open(recipe_file, 'r', encoding='utf-8') as f:
                content = f.read()
                recipes.append({
                    "filename": recipe_file.name,
                    "content": content
                })
        except Exception as e:
            logger.error(f"Error loading recipe {recipe_file}: {e}")
    
    logger.info(f"Loaded {len(recipes)} recipes")
    return recipes