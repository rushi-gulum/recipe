# RAG Evaluation Instructions

This module contains tools for evaluating the performance of the Recipe RAG system.

## Usage

### Running Evaluation

1. Prepare ground truth data in `data/ground_truth/ground_truth.jsonl`
2. Run the evaluation script:
   ```bash
   python tools/evaluate_rag.py
   ```

### Metrics Explained

- **Recall@K**: Fraction of relevant documents retrieved in top K results
- **MRR (Mean Reciprocal Rank)**: Average of reciprocal ranks of first relevant document
- **NDCG@K**: Normalized Discounted Cumulative Gain at K, considering ranking quality

### Ground Truth Format

Each line in `ground_truth.jsonl` should be a JSON object:
```json
{
    "query": "vegetarian pasta recipe",
    "relevant_docs": ["recipe_01.txt", "recipe_15.txt"],
    "description": "Query for vegetarian pasta recipes"
}
```

### Evaluation Process

1. Load ground truth queries and relevant documents
2. For each query, retrieve top K documents using RAG pipeline
3. Calculate evaluation metrics comparing retrieved vs relevant docs
4. Aggregate results across all queries

## Files

- `evaluator.py`: Core evaluation logic and metrics calculation
- `README.md`: This documentation file