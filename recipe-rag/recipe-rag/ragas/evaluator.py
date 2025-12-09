# RAG evaluation module - recall@k, mrr, ndcg, eval logic
import json
import logging
from typing import List, Dict, Any, Tuple
import numpy as np

logger = logging.getLogger(__name__)

class RAGEvaluator:
    def __init__(self):
        self.use_semantic_matching = True  # Enable improved evaluation
    
    def recall_at_k(self, retrieved_docs: List[str], relevant_docs: List[str], k: int) -> float:
        """Calculate Recall@K metric"""
        if not relevant_docs:
            return 0.0
        
        retrieved_at_k = set(retrieved_docs[:k])
        relevant_set = set(relevant_docs)
        
        return len(retrieved_at_k.intersection(relevant_set)) / len(relevant_set)
    
    def mean_reciprocal_rank(self, retrieved_docs: List[str], relevant_docs: List[str]) -> float:
        """Calculate Mean Reciprocal Rank (MRR)"""
        for i, doc in enumerate(retrieved_docs):
            if doc in relevant_docs:
                return 1.0 / (i + 1)
        return 0.0
    
    def ndcg_at_k(self, retrieved_docs: List[str], relevant_docs: List[str], k: int) -> float:
        """Calculate Normalized Discounted Cumulative Gain (NDCG@K)"""
        # Simplified NDCG implementation
        dcg = 0.0
        for i, doc in enumerate(retrieved_docs[:k]):
            if doc in relevant_docs:
                dcg += 1.0 / np.log2(i + 2)
        
        # Ideal DCG
        idcg = sum(1.0 / np.log2(i + 2) for i in range(min(len(relevant_docs), k)))
        
        return dcg / idcg if idcg > 0 else 0.0
    
    def evaluate_query(self, query: str, retrieved_docs: List[str], ground_truth: List[str]) -> Dict[str, float]:
        """Evaluate a single query"""
        metrics = {
            'recall_at_1': self.recall_at_k(retrieved_docs, ground_truth, 1),
            'recall_at_5': self.recall_at_k(retrieved_docs, ground_truth, 5),
            'recall_at_10': self.recall_at_k(retrieved_docs, ground_truth, 10),
            'mrr': self.mean_reciprocal_rank(retrieved_docs, ground_truth),
            'ndcg_at_5': self.ndcg_at_k(retrieved_docs, ground_truth, 5),
            'ndcg_at_10': self.ndcg_at_k(retrieved_docs, ground_truth, 10)
        }
        return metrics
    
    def evaluate_dataset(self, evaluation_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Evaluate the entire dataset and return averaged metrics"""
        all_metrics = []
        
        for item in evaluation_data:
            query = item['query']
            retrieved = item['retrieved_docs']
            ground_truth = item['ground_truth']
            
            metrics = self.evaluate_query(query, retrieved, ground_truth)
            all_metrics.append(metrics)
        
        # Average all metrics
        avg_metrics = {}
        if all_metrics:
            for key in all_metrics[0].keys():
                avg_metrics[key] = np.mean([m[key] for m in all_metrics])
        
        return avg_metrics