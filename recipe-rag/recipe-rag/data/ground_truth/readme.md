# Ground Truth for RAG Evaluation

This file contains manually curated query-document pairs for evaluating the RAG system's performance.

## Format

Each line should be a JSON object with:
- `query`: The search query
- `relevant_docs`: List of recipe filenames that are relevant for this query
- `description`: Optional description of the query intent

## Example Queries

1. **Vegetarian queries** - Should match vegetarian recipes
2. **Pasta queries** - Should match pasta-based recipes  
3. **Quick meal queries** - Should match recipes with short cook times
4. **Ingredient-specific queries** - Should match recipes containing specific ingredients

## Usage

This data is used by the evaluation script to measure:
- How well the system retrieves relevant recipes
- Ranking quality of search results
- Overall system performance metrics