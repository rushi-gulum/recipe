# Manual testing script for RAG system
import sys
from pathlib import Path

# Add parent directory to path to import backend modules
sys.path.append(str(Path(__file__).parent.parent))

from backend.rag import RAGPipeline
from backend.chains import RecipeChain
from backend.tools import ingredient_matcher_tool, recipe_search_tool, shopping_list_tool

def test_ingredient_tools():
    """Test the ingredient-related tools"""
    print("\n=== Testing Ingredient Tools ===")
    
    # Sample recipe text
    recipe_text = """
# Spaghetti Carbonara

*Ingredients:*
- 400g spaghetti
- 200g pancetta or bacon, diced
- 4 large egg yolks
- 100g Pecorino Romano cheese, grated
- 2 cloves garlic, minced
- Black pepper to taste
- Salt for pasta water
    """
    
    # Sample user ingredients
    user_ingredients = ["spaghetti", "eggs", "cheese", "garlic"]
    
    print(f"Recipe text preview: {recipe_text[:100]}...")
    print(f"User ingredients: {user_ingredients}")
    
    # Test ingredient matching
    matches, recipe_ings = ingredient_matcher_tool(user_ingredients, recipe_text)
    print(f"\nMatched ingredients: {matches}")
    print(f"Recipe ingredients: {recipe_ings}")
    
    # Test shopping list generation
    shopping_list = shopping_list_tool(user_ingredients, recipe_text)
    print(f"Shopping list (missing ingredients): {shopping_list}")

def main():
    # Test ingredient tools first
    test_ingredient_tools()
    
    # Initialize components
    rag_pipeline = RAGPipeline()
    rag_pipeline.setup()
    
    recipe_chain = RecipeChain()
    
    print("\n=== Recipe RAG System - Manual Test ===")
    print("Type 'quit' to exit")
    print("Type 'test' to run ingredient tool tests")
    print("-" * 40)
    
    while True:
        query = input("\nEnter your recipe query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if query.lower() == 'test':
            test_ingredient_tools()
            continue
        
        if not query:
            continue
        
        try:
            # Ask for user ingredients
            ingredients_input = input("Enter ingredients you have (comma-separated, or press Enter to skip): ").strip()
            user_ingredients = [ing.strip() for ing in ingredients_input.split(",")] if ingredients_input else []
            
            # Retrieve documents
            results = rag_pipeline.retrieve(query, k=5)
            
            # Process through chain
            final_results = recipe_chain.process_query(query, user_ingredients)
            
            print(f"\nQuery: {query}")
            if user_ingredients:
                print(f"Your ingredients: {user_ingredients}")
            print(f"Found {len(results)} results:")
            
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result.get('filename', 'Unknown')}")
                print(f"   Score: {result.get('score', 'N/A')}")
                print(f"   Preview: {result.get('content', '')[:100]}...")
                
                # If user has ingredients, show matching info
                if user_ingredients and 'content' in result:
                    matches, recipe_ings = ingredient_matcher_tool(user_ingredients, result['content'])
                    if matches:
                        print(f"    Matched ingredients: {matches}")
                    shopping_list = shopping_list_tool(user_ingredients, result['content'])
                    if shopping_list:
                        print(f"    Need to buy: {shopping_list[:3]}{'...' if len(shopping_list) > 3 else ''}")
        
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()