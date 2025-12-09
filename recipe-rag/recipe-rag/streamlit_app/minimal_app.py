import streamlit as st
import requests
import os
from typing import List

# Page configuration
st.set_page_config(
    page_title="Recipe Search",
    layout="wide"
)

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def get_full_recipe(recipe_id: str):
    """Get full recipe content by reading the original file"""
    try:
        recipe_path = f"../data/recipes/{recipe_id}.txt"
        if os.path.exists(recipe_path):
            with open(recipe_path, 'r', encoding='utf-8') as f:
                return f.read()
    except:
        pass
    return None

def main():
    st.title("Recipe Search")
    
    # Check backend
    if not check_backend():
        st.error("Backend server is not running!")
        st.code("python start_server.py")
        return
    
    st.success("Connected to Recipe API")
    
    # Tabs
    tab1, tab2 = st.tabs(["Text Search", "Ingredient Search"])
    
    with tab1:
        st.header("Search by Description")
        query = st.text_input("What would you like to cook?")
        num_results = st.slider("Results", 1, 10, 5)
        
        if st.button("Search") and query:
            try:
                response = requests.post(
                    "http://localhost:8000/search",
                    json={"query": query, "k": num_results},
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    
                    for i, recipe in enumerate(results):
                        filename = recipe.get('filename', '')
                        score = recipe.get('score', 0)
                        content = recipe.get('content', '')
                        
                        with st.expander(f"{filename} (Score: {score:.2f})"):
                            # Try to get full recipe
                            recipe_name = filename.replace('.txt', '') if filename.endswith('.txt') else filename
                            full_recipe = get_full_recipe(recipe_name)
                            
                            if full_recipe:
                                st.markdown("**Full Recipe:**")
                                st.text(full_recipe)
                            else:
                                st.markdown("**Recipe Content:**")
                                st.text(content)
                else:
                    st.error(f"Search failed: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    with tab2:
        st.header("Search by Ingredients")
        ingredient_input = st.text_area("Enter ingredients (one per line):")
        
        if st.button("Find Recipes") and ingredient_input:
            ingredients = [ing.strip() for ing in ingredient_input.split('\n') if ing.strip()]
            
            if ingredients:
                try:
                    response = requests.post(
                        "http://localhost:8000/find-recipe",
                        json={"ingredients": ingredients},
                        timeout=10
                    )
                    if response.status_code == 200:
                        result = response.json()
                        
                        if "error" not in result:
                            recipe_id = result.get('recipe_id', '')
                            score = result.get('score', 0)
                            matched = result.get('matched_ingredients', [])
                            missing = result.get('missing_ingredients', [])
                            
                            st.success(f"Found: {recipe_id} (Score: {score:.2f})")
                            
                            # Show ingredient info
                            col1, col2 = st.columns(2)
                            with col1:
                                if matched:
                                    st.success(f"**Matched ({len(matched)}):**")
                                    for ing in matched:
                                        st.write(f"• {ing}")
                            
                            with col2:
                                if missing:
                                    st.warning(f"**Missing ({len(missing)}):**")
                                    for ing in missing:
                                        st.write(f"• {ing}")
                            
                            # Show full recipe
                            full_recipe = get_full_recipe(recipe_id)
                            if full_recipe:
                                st.markdown("**Complete Recipe:**")
                                st.text(full_recipe)
                            else:
                                st.markdown("**Recipe Content:**")
                                st.text(result.get('recipe', ''))
                        else:
                            st.warning("No recipes found with these ingredients")
                    else:
                        st.error(f"Search failed: {response.status_code}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()