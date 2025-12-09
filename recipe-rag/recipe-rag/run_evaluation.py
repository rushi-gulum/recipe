#!/usr/bin/env python3
"""
Recipe RAG Evaluation Runner
Run this to evaluate your RAG system performance
"""

import sys
import json
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from ragas.evaluator import RAGEvaluator
from backend.rag import RecipeRAG

def load_ground_truth(file_path):
    """Load ground truth data"""
    ground_truth = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                ground_truth.append(json.loads(line))
    return ground_truth

def run_evaluation():
    """Run RAG evaluation and show results"""
    print(" Starting Recipe RAG Evaluation...")
    
    # Load ground truth
    gt_file = "data/ground_truth/ground_truth.jsonl"
    if not os.path.exists(gt_file):
        print(f" Ground truth file not found: {gt_file}")
        return
    
    ground_truth = load_ground_truth(gt_file)
    print(f" Loaded {len(ground_truth)} test queries")
    
    # Initialize RAG system
    print(" Initializing RAG system...")
    try:
        rag = RecipeRAG(recipe_dir="data/recipes")
        rag.build_index()
    except Exception as e:
        print(f" Failed to initialize RAG: {e}")
        return
    
    # Initialize evaluator
    evaluator = RAGEvaluator()
    
    # Run evaluation
    print(" Running evaluation...")
    evaluation_data = []
    
    for i, item in enumerate(ground_truth, 1):
        query = item['query']
        relevant_docs = item['relevant_docs']
        
        print(f"  Query {i}/{len(ground_truth)}: {query}")
        
        try:
            # Search using RAG
            results = rag.search(query, top_k=10)
            # Extract unique filenames from search results
            retrieved_filenames = []
            for chunk_id, distance, content in results:
                # Map chunk_id to filename using RAG's mapping
                filename = rag.chunk_to_file.get(chunk_id, "unknown")
                if filename != "unknown" and filename not in retrieved_filenames:
                    retrieved_filenames.append(filename)
            
            evaluation_data.append({
                'query': query,
                'retrieved_docs': retrieved_filenames,
                'ground_truth': relevant_docs
            })
            
            # Show detailed comparison
            retrieved_set = set(retrieved_filenames[:5])
            expected_set = set(relevant_docs)
            matches = retrieved_set.intersection(expected_set)
            
            print(f"    Retrieved: {retrieved_filenames[:3]}...")
            print(f"    Expected:  {relevant_docs}")
            if matches:
                print(f"    ✅ Matches: {list(matches)}")
            else:
                print(f"    ❌ No matches in top 5")
            print()
            
        except Exception as e:
            print(f" Error processing query: {e}")
            continue
    
    # Calculate metrics
    if not evaluation_data:
        print(" No evaluation data available")
        return
    
    results = evaluator.evaluate_dataset(evaluation_data)
    
    # Display results
    print("\n" + "="*50)
    print(" RAG EVALUATION RESULTS")
    print("="*50)
    
    print(f"\n ACCURACY METRICS:")
    print(f"  Recall@1:  {results.get('recall_at_1', 0):.3f}  (How often the best result is correct)")
    print(f"  Recall@5:  {results.get('recall_at_5', 0):.3f}  (How often correct answer is in top 5)")
    print(f"  Recall@10: {results.get('recall_at_10', 0):.3f} (How often correct answer is in top 10)")
    
    print(f"\n RANKING QUALITY:")
    print(f"  MRR:       {results.get('mrr', 0):.3f}  (Mean Reciprocal Rank - higher is better)")
    print(f"  NDCG@5:    {results.get('ndcg_at_5', 0):.3f}  (Ranking quality in top 5)")
    print(f"  NDCG@10:   {results.get('ndcg_at_10', 0):.3f} (Ranking quality in top 10)")
    
    # Interpretation
    print(f"\n INTERPRETATION:")
    recall_1 = results.get('recall_at_1', 0)
    recall_5 = results.get('recall_at_5', 0)
    mrr = results.get('mrr', 0)
    
    if recall_1 >= 0.8:
        print("   EXCELLENT: Top result is correct 80%+ of the time")
    elif recall_1 >= 0.6:
        print("   GOOD: Top result is correct 60%+ of the time") 
    elif recall_1 >= 0.4:
        print("    FAIR: Top result is correct 40%+ of the time")
    else:
        print("   POOR: Top result is correct less than 40% of the time")
    
    if recall_5 >= 0.9:
        print("   EXCELLENT: Correct answer in top 5 results 90%+ of the time")
    elif recall_5 >= 0.7:
        print("  GOOD: Correct answer in top 5 results 70%+ of the time")
    elif recall_5 >= 0.5:
        print("    FAIR: Correct answer in top 5 results 50%+ of the time") 
    else:
        print("   POOR: Correct answer in top 5 results less than 50% of the time")
    
    if mrr >= 0.7:
        print("   EXCELLENT: Very good ranking quality")
    elif mrr >= 0.5:
        print("   GOOD: Good ranking quality")
    elif mrr >= 0.3:
        print("    FAIR: Fair ranking quality")
    else:
        print("   POOR: Poor ranking quality")
    
    # Save detailed results
    os.makedirs("logs", exist_ok=True)
    with open("logs/evaluation_results.json", "w") as f:
        json.dump({
            "metrics": results,
            "evaluation_data": evaluation_data,
            "summary": {
                "total_queries": len(ground_truth),
                "successful_queries": len(evaluation_data),
                "success_rate": len(evaluation_data) / len(ground_truth)
            }
        }, f, indent=2)
    
    print(f"\n Detailed results saved to: logs/evaluation_results.json")
    print("="*50)

if __name__ == "__main__":
    run_evaluation()