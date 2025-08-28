def get_parameters() -> dict:
    """
    Returns a dictionary of parameters for configuring the search strategy

    Returns:
    dict: A dictionary containing the following keys:
        - is_disabled (bool): Indicates whether this search strategy is disabled.
        - index_name (str): The name of the index to be used.
        - query_transform_prompt (str): [OPTIONAL] Instructions for transforming queries.
        - rag_context (str): [OPTIONAL] The field to be used during RAG. defaults to 'lore' if not provided.
        - rerank_inner_hits (bool): Indicates whether to rerank inner hits.
    """
    return {
        "is_disabled": False,
        "index_name": "dbaas-confluence-semantic",
        "query_transform_prompt": """Instructions:

You are a query optimizer for Database as a Service (DBaaS) documentation search.

IMPORTANT: Only modify queries that are clearly problematic. Most queries should be returned UNCHANGED.

Only transform a query if it has:
- Excessive conversational language ("please help me understand", "I was wondering if you could tell me")
- Multiple unrelated questions in one query
- Very long, rambling sentences that obscure the main question

For good, clear questions (even if short), return them exactly as provided.

When transformation is needed:
- Keep the core technical question intact
- Preserve all technical terms, product names, and specific details
- Remove only unnecessary conversational elements
- Maintain the original question structure and intent

Examples:
- "What is Oracle DBaaS?" → "What is Oracle DBaaS?" (NO CHANGE)
- "How do I configure backups?" → "How do I configure backups?" (NO CHANGE)  
- "Please help me understand how I might be able to configure database backups in the system" → "How do I configure database backups?"

Return only the optimized query, no quotes or explanations.
        """,
        "rag_context": "content_semantic",
        "rerank_inner_hits": True
    }

    
def build_query(query_string: str, inner_hits_size:int = 3) -> dict:
    return {
      "retriever": {
        "rrf": {
          "retrievers": [
            {
              "standard": {
                "query": {
                  "nested": {
                    "path": "content_semantic.inference.chunks",
                    "query": {
                      "knn": {
                        "field": "content_semantic.inference.chunks.embeddings",
                        "query_vector_builder": {
                          "text_embedding": {
                            "model_id": ".multilingual-e5-small-elasticsearch",
                            "model_text": query_string
                          }
                        }
                      }
                    },
                    "inner_hits": {
                      "size": inner_hits_size,
                      "name": "dbaas-confluence-semantic.content_semantic",
                      "_source": [
                        "content_semantic.inference.chunks.text"
                      ]
                    }
                  }
                }
              }
            },
            {
              "standard": {
                "query": {
                  "multi_match": {
                    "query": query_string,
                    "fields": [
                      "title",
                      "content"
                    ]
                  }
                }
              }
            }
          ]
        }
      },
      "_source": False
    }