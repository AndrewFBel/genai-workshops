"""
Simple evaluation utility to replace deepeval for local Ollama-based evaluation
"""

import json
import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

logger = logging.getLogger(__name__)

@dataclass
class SimpleTestCase:
    """Simple test case for evaluation"""
    name: str
    input: str
    actual_output: str
    expected_output: str
    retrieval_context: List[str]

@dataclass
class SimpleMetricResult:
    """Simple metric result"""
    name: str
    score: float
    reason: str

@dataclass
class SimpleTestResult:
    """Simple test result"""
    name: str
    success: bool
    metrics_data: List[SimpleMetricResult]

@dataclass
class SimpleEvaluationResult:
    """Simple evaluation result"""
    test_results: List[SimpleTestResult]

class SimpleEvaluator:
    """Simple evaluator using basic NLP techniques"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    
    def evaluate_citation_correctness(self, actual_output: str) -> SimpleMetricResult:
        """Check if the output contains proper citations"""
        citation_pattern = r'\[\d+\]'
        citations = re.findall(citation_pattern, actual_output)
        
        if citations:
            score = 1.0
            reason = f"Found {len(citations)} citations: {', '.join(citations)}"
        else:
            score = 0.0
            reason = "No citations found in the format [#]"
        
        return SimpleMetricResult(
            name="Citation Correctness",
            score=score,
            reason=reason
        )
    
    def evaluate_semantic_similarity(self, actual_output: str, expected_output: str) -> SimpleMetricResult:
        """Evaluate semantic similarity between actual and expected output"""
        try:
            # Clean the texts
            actual_clean = re.sub(r'\[\d+\]', '', actual_output).strip()
            expected_clean = re.sub(r'\[\d+\]', '', expected_output).strip()
            
            if not actual_clean or not expected_clean:
                return SimpleMetricResult(
                    name="Semantic Similarity",
                    score=0.0,
                    reason="Empty text after cleaning"
                )
            
            # Calculate TF-IDF similarity
            texts = [actual_clean, expected_clean]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            # Convert to 0-1 scale and apply threshold
            score = max(0.0, min(1.0, similarity))
            
            if score >= 0.7:
                reason = f"High semantic similarity: {score:.3f}"
            elif score >= 0.4:
                reason = f"Moderate semantic similarity: {score:.3f}"
            else:
                reason = f"Low semantic similarity: {score:.3f}"
            
            return SimpleMetricResult(
                name="Semantic Similarity",
                score=score,
                reason=reason
            )
        
        except Exception as e:
            logger.error(f"Error calculating semantic similarity: {e}")
            return SimpleMetricResult(
                name="Semantic Similarity",
                score=0.0,
                reason=f"Error: {str(e)}"
            )
    
    def evaluate_completeness(self, actual_output: str, expected_output: str) -> SimpleMetricResult:
        """Evaluate completeness of the answer"""
        try:
            # Extract key terms from expected output
            expected_words = set(expected_output.lower().split())
            actual_words = set(actual_output.lower().split())
            
            # Remove common stop words and citations
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            expected_words = expected_words - stop_words
            actual_words = actual_words - stop_words
            
            if not expected_words:
                return SimpleMetricResult(
                    name="Completeness",
                    score=1.0,
                    reason="No key terms to evaluate"
                )
            
            # Calculate overlap
            overlap = len(expected_words.intersection(actual_words))
            completeness_score = overlap / len(expected_words)
            
            reason = f"Found {overlap}/{len(expected_words)} key terms from expected answer"
            
            return SimpleMetricResult(
                name="Completeness",
                score=completeness_score,
                reason=reason
            )
        
        except Exception as e:
            logger.error(f"Error calculating completeness: {e}")
            return SimpleMetricResult(
                name="Completeness",
                score=0.0,
                reason=f"Error: {str(e)}"
            )
    
    def evaluate_test_case(self, test_case: SimpleTestCase) -> SimpleTestResult:
        """Evaluate a single test case"""
        metrics = []
        
        # Evaluate citation correctness
        citation_metric = self.evaluate_citation_correctness(test_case.actual_output)
        metrics.append(citation_metric)
        
        # Evaluate semantic similarity
        similarity_metric = self.evaluate_semantic_similarity(
            test_case.actual_output, 
            test_case.expected_output
        )
        metrics.append(similarity_metric)
        
        # Evaluate completeness
        completeness_metric = self.evaluate_completeness(
            test_case.actual_output,
            test_case.expected_output
        )
        metrics.append(completeness_metric)
        
        # Determine overall success (all metrics must pass minimum threshold)
        success = all(metric.score >= 0.3 for metric in metrics)  # Lowered threshold for local eval
        
        return SimpleTestResult(
            name=test_case.name,
            success=success,
            metrics_data=metrics
        )

def generate_test_case(name: str, query: str, actual_output: str, retrieval_context: List[str], correct_answer: str) -> SimpleTestCase:
    """Generate a simple test case"""
    return SimpleTestCase(
        name=name,
        input=query,
        actual_output=actual_output,
        expected_output=correct_answer,
        retrieval_context=retrieval_context
    )

def evaluate_test_cases(test_cases: List[SimpleTestCase]) -> SimpleEvaluationResult:
    """Evaluate a list of test cases"""
    evaluator = SimpleEvaluator()
    results = []
    
    for test_case in test_cases:
        result = evaluator.evaluate_test_case(test_case)
        results.append(result)
    
    return SimpleEvaluationResult(test_results=results)