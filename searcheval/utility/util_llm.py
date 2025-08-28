
import ollama
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMUtil:
    def __init__(self):
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model_name = os.getenv("OLLAMA_MODEL", "llama3.2")
        self.client = ollama.Client(host=self.ollama_host)
        
        # Initialize logging
        self.log_file = "rag_interactions.log"
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging for RAG interactions"""
        log_handler = logging.FileHandler(self.log_file)
        log_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)
    
    def _log_interaction(self, interaction_type: str, data: Dict[str, Any]):
        """Log RAG interactions"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type,
            "data": data
        }
        logger.info(json.dumps(log_entry))
    
    def transform_query_direct(self, system_prompt: str, user_query: str, model_name: str = None) -> dict:
        """Transform user query using Ollama"""
        if model_name is None:
            model_name = self.model_name
            
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        # Log the query transformation request
        self._log_interaction("query_transform_request", {
            "original_query": user_query,
            "system_prompt": system_prompt,
            "model": model_name
        })
        
        try:
            response = self.client.chat(
                model=model_name,
                messages=messages,
                options={
                    "temperature": 0.0,
                    "num_predict": 512
                }
            )
            
            transformed_query = response['message']['content'].strip()
            
            # Log the transformation result
            self._log_interaction("query_transform_response", {
                "original_query": user_query,
                "transformed_query": transformed_query,
                "model": model_name
            })
            
            return {"answer": transformed_query, "total_tokens": 0}  # Ollama doesn't provide token count
        
        except Exception as e:
            logger.error(f"Query transformation error: {e}")
            self._log_interaction("query_transform_error", {
                "original_query": user_query,
                "error": str(e)
            })
            return {"answer": user_query, "total_tokens": 0}
    
    def rag_direct(self, system_prompt: str, retrieval_context: list, query_string: str, model_name: str = None, should_print=True) -> dict:
        """Perform RAG using Ollama"""
        if model_name is None:
            model_name = self.model_name
            
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query_string}
        ]
        
        # Log the RAG request
        self._log_interaction("rag_request", {
            "query": query_string,
            "system_prompt": system_prompt,
            "retrieval_context": retrieval_context,
            "model": model_name
        })
        
        try:
            response = self.client.chat(
                model=model_name,
                messages=messages,
                options={
                    "temperature": 0.0,
                    "num_predict": 1024
                }
            )
            
            rag_answer = response['message']['content'].strip()
            
            if should_print:
                print(f"\tRAG answer: {rag_answer}")
            
            # Log the RAG response
            self._log_interaction("rag_response", {
                "query": query_string,
                "answer": rag_answer,
                "model": model_name
            })
            
            return {"answer": rag_answer, "total_tokens": 0}  # Ollama doesn't provide token count
        
        except Exception as e:
            logger.error(f"RAG error: {e}")
            self._log_interaction("rag_error", {
                "query": query_string,
                "error": str(e)
            })
            return {"answer": "Unable to return response due to an LLM error", "total_tokens": 0}
    
    def flush_cache(self):
        """No-op since we're not using cache"""
        pass

singleton_llm_util = LLMUtil()

def get_llm_util() -> LLMUtil:
    return singleton_llm_util