# Recipe RAG System

A Retrieval-Augmented Generation (RAG) system for recipe search and discovery using OpenAI embeddings and ChromaDB.

## Features

 **Semantic Recipe Search** - Find recipes using natural language queries
 **Ingredient Matching** - Match available ingredients to suitable recipes  
 **Shopping List Generation** - Create shopping lists from selected recipes
 **RAG Evaluation** - Comprehensive evaluation metrics (Recall@K, MRR, NDCG)
 **Interactive UI** - Streamlit-based web interface

## Architecture

- **Backend**: FastAPI server with RAG pipeline
- **Vector Database**: ChromaDB for persistent vector storage
- **Embeddings**: OpenAI text-embedding-3-small
- **Frontend**: Streamlit web application
- **Evaluation**: Custom RAG metrics and evaluation framework

## Quick Start

### 1. Installation

```bash
# Clone and navigate to project
cd recipe-rag

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your OpenAI API key
```

### 2. Add Recipe Data

Place your recipe text files in `data/recipes/`:
```
data/recipes/
├── spaghetti_carbonara.txt
├── vegetarian_buddha_bowl.txt
└── ...
```

### 3. Run the System

```bash
# Start the backend API
python backend/main.py

# In another terminal, start the Streamlit UI
streamlit run streamlit_app/app.py
```

### 4. Access the Application

- **Web UI**: http://localhost:8501
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Recipe Format

Recipes should be saved as `.txt` files with this structure:

```
# Recipe Title

*Ingredients:*
- 400g spaghetti
- 200g pancetta or bacon, diced
- ...

*Instructions:*
1. Bring a large pot of salted water to boil
2. Cook spaghetti according to package directions
3. ...

*Prep Time: 10 minutes*
*Cook Time: 15 minutes*
*Serves: 4*
```

## RAG Evaluation

Evaluate system performance using ground truth data:

```bash
# Run evaluation
python tools/evaluate_rag.py --ground-truth data/ground_truth/ground_truth.jsonl

# Results will show metrics like:
# - recall_at_5: 0.8500
# - mrr: 0.7200  
# - ndcg_at_10: 0.6800
```

## API Endpoints

### Search Recipes
```bash
POST /search
{
  "query": "vegetarian pasta recipe",
  "k": 5
}
```

### Health Check
```bash
GET /
```

## Project Structure

```
recipe-rag/
├── backend/              # FastAPI backend
│   ├── main.py          # API entrypoint  
│   ├── rag.py           # RAG pipeline
│   ├── chains.py        # Result ranking
│   ├── embeddings.py    # OpenAI embeddings
│   ├── vectorstore_chroma.py  # Vector database
│   └── tools/           # Recipe tools
├── ragas/               # Evaluation framework
├── data/                # Recipe and ground truth data
├── streamlit_app/       # Web UI
├── tools/               # Utility scripts
└── logs/                # Application logs
```

## Configuration

Key environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `CHROMA_PERSIST_DIRECTORY`: Vector database storage path  
- `RECIPES_DIRECTORY`: Path to recipe text files
- `LOG_LEVEL`: Logging verbosity (INFO, DEBUG, etc.)

## Development

### Adding New Tools

1. Create tool in `backend/tools/`
2. Import in `backend/chains.py`
3. Add to processing pipeline

### Custom Evaluation

1. Add ground truth queries to `data/ground_truth/ground_truth.jsonl`
2. Run evaluation script
3. Analyze results in `logs/evaluation_results.json`

## Troubleshooting

**Connection Errors**: Ensure the backend API is running on port 8000
**Empty Results**: Check that recipe files exist in `data/recipes/`
**Import Errors**: Verify all dependencies are installed with `pip install -r requirements.txt`

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request


cd /e/recipe/recipe-rag/streamlit_app && /e/recipe/.venv/Scripts/python.exe -m streamlit run minimal_app.py --server.port 8502 #frontend
cd recipe-rag
$ python start_server.py #server start backend



cd /e/recipe/recipe-rag && /e/recipe/.venv/Scripts/python.exe run_evaluation.py #ragas evaluation