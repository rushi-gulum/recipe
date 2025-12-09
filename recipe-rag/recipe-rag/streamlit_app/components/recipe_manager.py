# Recipe management utilities
import streamlit as st
import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

class RecipeManager:
    """Manage recipes, favorites, and collections"""
    
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'recipe_collections' not in st.session_state:
            st.session_state.recipe_collections = {}
        if 'recipe_ratings' not in st.session_state:
            st.session_state.recipe_ratings = {}
        if 'recipe_notes' not in st.session_state:
            st.session_state.recipe_notes = {}
        if 'meal_plan' not in st.session_state:
            st.session_state.meal_plan = {}
    
    def create_collection(self, name: str, description: str = ""):
        """Create a new recipe collection"""
        if name not in st.session_state.recipe_collections:
            st.session_state.recipe_collections[name] = {
                'description': description,
                'recipes': [],
                'created_at': datetime.now().isoformat()
            }
            return True
        return False
    
    def add_to_collection(self, collection_name: str, recipe: Dict[str, Any]):
        """Add recipe to a collection"""
        if collection_name in st.session_state.recipe_collections:
            recipe_id = self.get_recipe_id(recipe)
            if recipe_id not in [r.get('id') for r in st.session_state.recipe_collections[collection_name]['recipes']]:
                recipe['id'] = recipe_id
                st.session_state.recipe_collections[collection_name]['recipes'].append(recipe)
                return True
        return False
    
    def get_recipe_id(self, recipe: Dict[str, Any]) -> str:
        """Generate a unique ID for a recipe"""
        return f"{recipe.get('filename', '')}-{hash(recipe.get('content', ''))}"
    
    def rate_recipe(self, recipe_id: str, rating: int):
        """Rate a recipe (1-5 stars)"""
        st.session_state.recipe_ratings[recipe_id] = {
            'rating': rating,
            'timestamp': datetime.now().isoformat()
        }
    
    def add_note(self, recipe_id: str, note: str):
        """Add a note to a recipe"""
        if recipe_id not in st.session_state.recipe_notes:
            st.session_state.recipe_notes[recipe_id] = []
        
        st.session_state.recipe_notes[recipe_id].append({
            'note': note,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_recipe_rating(self, recipe_id: str) -> Optional[int]:
        """Get rating for a recipe"""
        return st.session_state.recipe_ratings.get(recipe_id, {}).get('rating')
    
    def get_recipe_notes(self, recipe_id: str) -> List[Dict[str, str]]:
        """Get notes for a recipe"""
        return st.session_state.recipe_notes.get(recipe_id, [])

def show_recipe_collections(manager: RecipeManager):
    """Display and manage recipe collections"""
    st.subheader("📚 Recipe Collections")
    
    # Create new collection
    with st.expander("➕ Create New Collection"):
        col1, col2 = st.columns([3, 1])
        with col1:
            collection_name = st.text_input("Collection Name")
            collection_desc = st.text_area("Description (optional)")
        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            if st.button("Create Collection"):
                if collection_name:
                    if manager.create_collection(collection_name, collection_desc):
                        st.success(f"Created collection '{collection_name}'!")
                        st.rerun()
                    else:
                        st.error("Collection already exists!")
    
    # Display existing collections
    if st.session_state.recipe_collections:
        for collection_name, collection_data in st.session_state.recipe_collections.items():
            with st.expander(f"📚 {collection_name} ({len(collection_data['recipes'])} recipes)"):
                st.markdown(f"**Description:** {collection_data.get('description', 'No description')}")
                st.markdown(f"**Created:** {collection_data.get('created_at', 'Unknown')[:10]}")
                
                # Display recipes in collection
                for i, recipe in enumerate(collection_data['recipes']):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        recipe_title = recipe.get('title', recipe.get('filename', f'Recipe {i+1}'))
                        st.write(f"• {recipe_title}")
                    with col2:
                        if st.button("Remove", key=f"remove_{collection_name}_{i}"):
                            st.session_state.recipe_collections[collection_name]['recipes'].pop(i)
                            st.rerun()
                
                # Delete collection
                if st.button(f"🗑️ Delete Collection", key=f"delete_{collection_name}"):
                    del st.session_state.recipe_collections[collection_name]
                    st.rerun()
    else:
        st.info("No collections yet. Create one to organize your recipes!")

def show_enhanced_recipe(recipe: Dict[str, Any], manager: RecipeManager):
    """Display recipe with enhanced features (rating, notes, collections)"""
    recipe_id = manager.get_recipe_id(recipe)
    recipe_title = recipe.get('title', recipe.get('filename', 'Unknown Recipe'))
    
    # Recipe header
    st.markdown(f"### {recipe_title}")
    
    col1, col2, col3 = st.columns([2, 2, 2])
    
    # Rating
    with col1:
        current_rating = manager.get_recipe_rating(recipe_id)
        rating = st.selectbox(
            "Rate this recipe:",
            [0, 1, 2, 3, 4, 5],
            index=current_rating if current_rating else 0,
            format_func=lambda x: "⭐" * x if x > 0 else "No rating",
            key=f"rating_{recipe_id}"
        )
        
        if rating is not None and rating > 0 and rating != current_rating:
            manager.rate_recipe(recipe_id, rating)
            st.success(f"Rated {rating} stars!")
    
    # Collections
    with col2:
        if st.session_state.recipe_collections:
            collection_options = ["Select collection..."] + list(st.session_state.recipe_collections.keys())
            selected_collection = st.selectbox(
                "Add to collection:",
                collection_options,
                key=f"collection_{recipe_id}"
            )
            
            if selected_collection and selected_collection != "Select collection...":
                if manager.add_to_collection(selected_collection, recipe):
                    st.success(f"Added to {selected_collection}!")
                else:
                    st.info("Already in collection")
    
    # Notes
    with col3:
        if st.button("📝 Add Note", key=f"note_btn_{recipe_id}"):
            st.session_state[f"show_notes_{recipe_id}"] = True
    
    # Note input
    if st.session_state.get(f"show_notes_{recipe_id}", False):
        note_text = st.text_area("Add your note:", key=f"note_text_{recipe_id}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save Note", key=f"save_note_{recipe_id}"):
                if note_text:
                    manager.add_note(recipe_id, note_text)
                    st.success("Note saved!")
                    st.session_state[f"show_notes_{recipe_id}"] = False
                    st.rerun()
        with col2:
            if st.button("Cancel", key=f"cancel_note_{recipe_id}"):
                st.session_state[f"show_notes_{recipe_id}"] = False
                st.rerun()
    
    # Display existing notes
    notes = manager.get_recipe_notes(recipe_id)
    if notes:
        st.markdown("**Your Notes:**")
        for i, note in enumerate(notes):
            with st.expander(f"Note {i+1} - {note['timestamp'][:10]}"):
                st.write(note['note'])
    
    # Recipe content
    st.markdown("**Recipe:**")
    st.markdown(recipe.get('content', 'No content available'))

def show_meal_planner():
    """Display meal planning interface"""
    st.subheader("📅 Meal Planner")
    
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    meals = ['Breakfast', 'Lunch', 'Dinner', 'Snack']
    
    # Current week meal plan
    col1, col2 = st.columns([1, 4])
    
    with col1:
        selected_day = st.selectbox("Select Day:", days_of_week)
        selected_meal = st.selectbox("Select Meal:", meals)
    
    with col2:
        # Show current meal plan
        if selected_day in st.session_state.meal_plan:
            day_plan = st.session_state.meal_plan[selected_day]
            st.markdown(f"**{selected_day}'s Meals:**")
            for meal, recipe in day_plan.items():
                if recipe:
                    st.write(f"• {meal}: {recipe}")
                else:
                    st.write(f"• {meal}: Not planned")
        else:
            st.info(f"No meals planned for {selected_day}")
    
    # Add recipe to meal plan
    if st.session_state.favorite_recipes:
        st.markdown("**Add Recipe to Meal Plan:**")
        recipe_options = ["Select recipe..."] + [
            r.get('title', r.get('filename', f'Recipe {i}')) 
            for i, r in enumerate(st.session_state.favorite_recipes)
        ]
        
        selected_recipe = st.selectbox("Choose from favorites:", recipe_options)
        
        if selected_recipe != "Select recipe..." and st.button("Add to Meal Plan"):
            if selected_day not in st.session_state.meal_plan:
                st.session_state.meal_plan[selected_day] = {}
            
            st.session_state.meal_plan[selected_day][selected_meal] = selected_recipe
            st.success(f"Added {selected_recipe} to {selected_day} {selected_meal}!")
            st.rerun()
    
    # Weekly overview
    st.markdown("### 📊 Weekly Overview")
    
    if st.session_state.meal_plan:
        for day in days_of_week:
            if day in st.session_state.meal_plan:
                with st.expander(f"{day}"):
                    for meal in meals:
                        recipe = st.session_state.meal_plan[day].get(meal, "Not planned")
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**{meal}:** {recipe}")
                        with col2:
                            if recipe != "Not planned":
                                if st.button("Remove", key=f"remove_{day}_{meal}"):
                                    del st.session_state.meal_plan[day][meal]
                                    st.rerun()
    else:
        st.info("No meal plan created yet. Start adding recipes!")

def export_meal_plan():
    """Export meal plan to text format"""
    if not st.session_state.meal_plan:
        st.warning("No meal plan to export")
        return
    
    content = "WEEKLY MEAL PLAN\n"
    content += "=" * 50 + "\n\n"
    
    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    meals = ['Breakfast', 'Lunch', 'Dinner', 'Snack']
    
    for day in days_of_week:
        if day in st.session_state.meal_plan:
            content += f"{day.upper()}\n"
            content += "-" * 20 + "\n"
            
            for meal in meals:
                recipe = st.session_state.meal_plan[day].get(meal, "Not planned")
                content += f"{meal}: {recipe}\n"
            content += "\n"
    
    st.download_button(
        label="📥 Download Meal Plan",
        data=content,
        file_name=f"meal_plan_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain"
    )