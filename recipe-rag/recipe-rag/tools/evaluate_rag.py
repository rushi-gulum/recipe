# CLI script to run RAG evaluation
import json
import argparse
import logging
import sys
from pathlib import Path

# Add parent directory to path to import backend modules
sys.path.append(str(Path(__file__).parent.parent))

from ragas.evaluator import RAGEvaluator
from backend.rag import RAGPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_ground_truth(file_path: str):
    """Load ground truth data from JSONL file"""
    ground_truth = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                ground_truth.append(json.loads(line))
    return ground_truth

def main():
    parser = argparse.ArgumentParser(description='Evaluate RAG system performance')
    parser.add_argument('--ground-truth', default='data/ground_truth/ground_truth.jsonl',
                       help='Path to ground truth JSONL file')
    parser.add_argument('--k', type=int, default=10,
                       help='Number of documents to retrieve for each query')
    parser.add_argument('--output', default='logs/evaluation_results.json',
                       help='Output file for evaluation results')
    
    args = parser.parse_args()
    
    # Load ground truth
    logger.info(f"Loading ground truth from {args.ground_truth}")
    ground_truth = load_ground_truth(args.ground_truth)
    
    # Initialize RAG pipeline
    logger.info("Initializing RAG pipeline")
    rag_pipeline = RAGPipeline()
    rag_pipeline.setup()
    
    # Initialize evaluator
    evaluator = RAGEvaluator()
    
    # Prepare evaluation data
    evaluation_data = []
    
    for item in ground_truth:
        query = item['query']
        relevant_docs = item['relevant_docs']
        
        # Retrieve documents using RAG pipeline
        retrieved_results = rag_pipeline.retrieve(query, k=args.k)
        retrieved_docs = [result['filename'] for result in retrieved_results]
        
        evaluation_data.append({
            'query': query,
            'retrieved_docs': retrieved_docs,
            'ground_truth': relevant_docs
        })
    
    # Run evaluation
    logger.info("Running evaluation")
    results = evaluator.evaluate_dataset(evaluation_data)
    
    # Save results
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print results
    print("\n=== RAG Evaluation Results ===")
    for metric, value in results.items():
        print(f"{metric}: {value:.4f}")
    
    logger.info(f"Results saved to {args.output}")

if __name__ == "__main__":
    main()