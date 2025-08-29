#!/usr/bin/env python3
"""
Debug script to test search functionality and understand index structure
"""

import os
from dotenv import load_dotenv

def debug_search():
    """Debug search functionality"""
    print("🔍 Debug: Testing search functionality...")
    
    try:
        load_dotenv()
        
        from utility.util_es import get_es, search_to_context_with_urls
        import final_strat as strategy_module
        
        es = get_es()
        
        # Test query
        test_query = "What is Oracle DBaaS?"
        
        # Get strategy parameters
        params = strategy_module.get_parameters()
        index_name = params['index_name']
        rag_context = params.get("rag_context", "content")
        rerank_inner_hits = params.get("rerank_inner_hits", False)
        
        print(f"Index name: {index_name}")
        print(f"RAG context: {rag_context}")
        print(f"Rerank inner hits: {rerank_inner_hits}")
        
        # Build query
        body = strategy_module.build_query(test_query, 3)
        print(f"Query body: {body}")
        
        # Test basic search first
        from utility.util_es import search_results_only
        results = search_results_only(es, index_name, body, 3)
        
        print(f"\nSearch results structure:")
        print(f"Total hits: {results.get('hits', {}).get('total', {})}")
        
        if results.get('hits', {}).get('hits'):
            first_hit = results['hits']['hits'][0]
            print(f"First hit keys: {list(first_hit.keys())}")
            
            if '_source' in first_hit:
                source_keys = list(first_hit['_source'].keys())
                print(f"_source keys: {source_keys}")
                
                # Look for URL fields
                url_fields = [k for k in source_keys if 'url' in k.lower() or 'link' in k.lower()]
                print(f"Potential URL fields: {url_fields}")
                
                # Show some content
                for key in ['title', 'content', 'text', 'body'][:3]:
                    if key in first_hit['_source']:
                        value = str(first_hit['_source'][key])[:100]
                        print(f"{key}: {value}...")
            
            if 'inner_hits' in first_hit:
                inner_hits = first_hit['inner_hits']
                print(f"Inner hits keys: {list(inner_hits.keys())}")
                
                for inner_key in inner_hits.keys():
                    inner_data = inner_hits[inner_key]
                    if 'hits' in inner_data and 'hits' in inner_data['hits']:
                        inner_hit_count = len(inner_data['hits']['hits'])
                        print(f"Inner hits '{inner_key}': {inner_hit_count} hits")
                        
                        if inner_hit_count > 0:
                            first_inner = inner_data['hits']['hits'][0]
                            if '_source' in first_inner:
                                inner_source_keys = list(first_inner['_source'].keys())
                                print(f"  Inner _source keys: {inner_source_keys}")
        
        # Now test the search_to_context_with_urls function
        print(f"\n🔄 Testing search_to_context_with_urls...")
        
        retrieval_context, source_urls = search_to_context_with_urls(
            es, index_name, test_query, body, rag_context, rerank_inner_hits, 6, 9
        )
        
        print(f"Retrieved {len(retrieval_context)} context passages")
        print(f"Retrieved {len(source_urls)} source URLs")
        
        if retrieval_context:
            print(f"First context: {retrieval_context[0][:200]}...")
        
        if source_urls:
            print(f"First URL: {source_urls[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_search()