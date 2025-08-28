#!/usr/bin/env python3
"""
Test script to verify the Database as a Service RAG system setup
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test environment variables"""
    print("🔧 Testing environment variables...")
    
    load_dotenv()
    
    required_vars = ['ES_SERVER', 'ES_API_KEY', 'OLLAMA_HOST', 'OLLAMA_MODEL']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            print(f"  ✅ {var}: {value[:20]}..." if len(value) > 20 else f"  ✅ {var}: {value}")
    
    if missing_vars:
        print(f"  ❌ Missing variables: {missing_vars}")
        return False
    
    return True

def test_elasticsearch():
    """Test Elasticsearch connection"""
    print("\n🔍 Testing Elasticsearch connection...")
    
    try:
        from utility.util_es import get_es
        es = get_es()
        
        # Test connection
        info = es.info()
        print(f"  ✅ Connected to Elasticsearch: {info['version']['number']}")
        
        # Test index exists
        index_name = "dbaas-confluence-semantic"
        if es.indices.exists(index=index_name):
            print(f"  ✅ Index '{index_name}' exists")
            
            # Get index stats
            stats = es.indices.stats(index=index_name)
            doc_count = stats['indices'][index_name]['total']['docs']['count']
            print(f"  ✅ Index contains {doc_count} documents")
        else:
            print(f"  ❌ Index '{index_name}' not found")
            return False
            
        return True
        
    except Exception as e:
        print(f"  ❌ Elasticsearch error: {str(e)}")
        return False

def test_ollama():
    """Test Ollama connection"""
    print("\n🤖 Testing Ollama connection...")
    
    try:
        from utility.util_llm import get_llm_util
        llm_util = get_llm_util()
        
        # Test simple query
        response = llm_util.transform_query_direct(
            "Simplify this query", 
            "What is the database service?"
        )
        
        if response and 'answer' in response:
            print(f"  ✅ Ollama responding: {response['answer'][:50]}...")
            print(f"  ✅ Tokens used: {response.get('total_tokens', 'unknown')}")
            return True
        else:
            print("  ❌ Invalid response from Ollama")
            return False
            
    except Exception as e:
        print(f"  ❌ Ollama error: {str(e)}")
        return False

def test_rag_pipeline():
    """Test complete RAG pipeline with URLs"""
    print("\n🔄 Testing RAG pipeline...")
    
    try:
        from utility.util_es import get_es, search_to_context_with_urls
        from utility.util_llm import get_llm_util
        import final_strat as strategy_module
        
        es = get_es()
        llm_util = get_llm_util()
        
        # Test query
        test_query = "How do I configure database backups?"
        
        # Get strategy parameters
        params = strategy_module.get_parameters()
        index_name = params['index_name']
        
        # Build query
        body = strategy_module.build_query(test_query, 3)
        
        # Search with URLs
        retrieval_context, source_urls = search_to_context_with_urls(
            es, index_name, test_query, body, 
            params.get("rag_context", "content"), 
            params.get("rerank_inner_hits", False), 
            6, 9
        )
        
        if retrieval_context:
            print(f"  ✅ Retrieved {len(retrieval_context)} context passages")
            print(f"  ✅ Retrieved {len(source_urls)} source URLs")
            print(f"  ✅ First passage: {retrieval_context[0][:100]}...")
            if source_urls and source_urls[0]:
                print(f"  ✅ First URL: {source_urls[0][:50]}...")
            
            # Test query transformation
            query_transform_prompt = params.get("query_transform_prompt")
            if query_transform_prompt:
                transform_response = llm_util.transform_query_direct(query_transform_prompt, test_query)
                print(f"  ✅ Query transformation: '{test_query}' → '{transform_response['answer']}'")
            
            # Test RAG
            context = "\n".join([f"[{i+1}] {text}" for i, text in enumerate(retrieval_context[:3])])
            system_prompt = f"Answer based on context:\n{context}"
            
            rag_response = llm_util.rag_direct(system_prompt, retrieval_context[:3], test_query, should_print=False)
            
            if rag_response and 'answer' in rag_response:
                print(f"  ✅ RAG response: {rag_response['answer'][:100]}...")
                return True
            else:
                print("  ❌ No RAG response generated")
                return False
        else:
            print("  ❌ No context retrieved")
            return False
            
    except Exception as e:
        print(f"  ❌ RAG pipeline error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Database as a Service RAG System - Setup Test\n")
    
    tests = [
        ("Environment", test_environment),
        ("Elasticsearch", test_elasticsearch),
        ("Ollama", test_ollama),
        ("RAG Pipeline", test_rag_pipeline)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} test failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Summary:")
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("  1. Run: streamlit run pages/2_Agentic_RAG.py")
        print("  2. Or open: Search_Evaluation.ipynb")
    else:
        print("\n⚠️  Some tests failed. Please check your configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()