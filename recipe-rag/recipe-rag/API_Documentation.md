# Recipe RAG API Documentation

## Overview
The Recipe RAG API provides intelligent recipe search capabilities using semantic search and ingredient-based matching.

## Base URL
```
http://localhost:8000
```

## Authentication
No authentication required for local development.

---

## Endpoints

### 1. Health Check
**GET** `/health`

Check if the API server is running.

**Response:**
```json
{
  "status": "ok"
}
```

---

### 2. Text-based Recipe Search
**POST** `/search`

Search for recipes using natural language queries.

**Request Body:**
```json
{
  "query": "string",  // Natural language recipe description
  "k": 5             // Number of results to return (optional, default: 5)
}
```

**Example Request:**
```json
{
  "query": "spicy chicken curry with vegetables",
  "k": 3
}
```

**Response:**
```json
{
  "query": "spicy chicken curry with vegetables",
  "results": [
    {
      "id": "recipe_25::chunk_1",
      "filename": "recipe_25.txt",
      "content": "Title: Spicy Chicken Curry\n\nIngredients:\n- 500g chicken breast...",
      "score": 0.89,
      "distance": 0.11
    }
  ],
  "count": 1
}
```

**Response Fields:**
- `query`: Original search query
- `results`: Array of recipe chunks matching the query
  - `id`: Unique chunk identifier
  - `filename`: Source recipe file name
  - `content`: Recipe text content
  - `score`: Similarity score (0-1, higher is better)
  - `distance`: Distance metric (lower is better)
- `count`: Number of results returned

---

### 3. Ingredient-based Recipe Search
**POST** `/find-recipe`

Find the best recipe match based on available ingredients.

**Request Body:**
```json
{
  "ingredients": ["ingredient1", "ingredient2", ...]  // Array of available ingredients
}
```

**Example Request:**
```json
{
  "ingredients": ["chicken", "tomato", "onion", "garlic", "rice"]
}
```

**Response:**
```json
{
  "recipe_id": "recipe_12",
  "score": 0.87,
  "recipe": "Title: Chicken Tomato Rice\n\nIngredients:\n- 300g chicken breast\n- 2 large tomatoes\n- 1 medium onion\n- 3 cloves garlic\n- 1 cup rice\n- 2 tbsp olive oil\n- Salt and pepper\n\nInstructions:\n1. Cook rice according to package instructions\n2. Cut chicken into bite-sized pieces\n3. Heat oil in a large pan...",
  "matched_ingredients": ["chicken", "tomato", "onion", "garlic", "rice"],
  "missing_ingredients": ["olive oil", "salt", "pepper"]
}
```

**Response Fields:**
- `recipe_id`: Identifier of the best matching recipe
- `score`: Match quality score (0-1, higher is better)
- `recipe`: Complete recipe text including title, ingredients, and instructions
- `matched_ingredients`: Ingredients you have that are used in the recipe
- `missing_ingredients`: Additional ingredients needed to make the recipe

**Error Response:**
```json
{
  "error": "No recipes found"
}
```

---

### 4. API Root
**GET** `/`

Get basic API information.

**Response:**
```json
{
  "message": "Recipe RAG API is running"
}
```

---

## Error Handling

### HTTP Status Codes
- `200 OK`: Successful request
- `400 Bad Request`: Invalid request parameters
- `405 Method Not Allowed`: HTTP method not supported for endpoint
- `500 Internal Server Error`: Server-side error

### Error Response Format
```json
{
  "detail": "Error message description"
}
```

---

## Usage Examples

### Example 1: Find Quick Dinner Ideas
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "quick 30 minute dinner recipe",
    "k": 5
  }'
```

### Example 2: Use Available Ingredients
```bash
curl -X POST "http://localhost:8000/find-recipe" \
  -H "Content-Type: application/json" \
  -d '{
    "ingredients": ["pasta", "cheese", "tomato", "basil"]
  }'
```

### Example 3: Find Vegetarian Options
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "vegetarian pasta without meat",
    "k": 3
  }'
```

---

## Postman Collection

Import the provided Postman collection files:
1. `Recipe_RAG_API.postman_collection.json` - API endpoints
2. `Recipe_RAG_Environment.postman_environment.json` - Environment variables

### How to Import:
1. Open Postman
2. Click "Import" button
3. Select both JSON files
4. Set "Recipe RAG Environment" as active environment
5. Start testing the API endpoints

---

## Data Format

### Recipe File Structure
```
Title: Recipe Name

Ingredients:
- ingredient 1
- ingredient 2
- ingredient 3

Instructions:
1. Step one
2. Step two
3. Step three
```

### Supported Search Types
1. **Semantic Search**: Natural language queries like "healthy breakfast", "spicy dinner", "vegetarian pasta"
2. **Ingredient Search**: List of ingredients you have available
3. **Cuisine Type**: "Italian", "Mexican", "Asian", etc.
4. **Cooking Method**: "grilled", "baked", "fried", etc.
5. **Dietary Restrictions**: "vegetarian", "vegan", "gluten-free", etc.

---

## Technical Details

- **Vector Database**: ChromaDB for semantic search
- **Embeddings**: OpenAI text embeddings
- **Framework**: FastAPI with Python
- **Search Algorithm**: Hybrid ranking (75% semantic + 25% ingredient matching)
- **Response Time**: Typically < 3 seconds
- **Recipe Database**: 50+ recipes with 85 searchable chunks