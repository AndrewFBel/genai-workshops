#!/usr/bin/env python3
"""
Test script to verify both fixes work
"""

import os
from dotenv import load_dotenv

def test_search_app_urls():
    """Test Search App URL functionality"""
    print("🔍 Testing Search App URL functionality...")
    
    try:
        load_dotenv()
        
        from utility.util_es import get_es
        import final_strat as strategy_module
        
        es = get_es()
        
        # Import the search function from Search App
        import importlib.util
        spec = importlib.util.spec_from_file_location("search_app", "/Users/andrewfbel/code/genai-workshops/searcheval/pages/1_Search_App.py")
        search_app = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(search_app)
        
        # Test the get_document_details function
        index_name = strategy_module.get_parameters()['index_name']
        
        # Get a sample document ID from search results
        test_query = "Oracle DBaaS"
        body = strategy_module.build_query(test_query, 3)
        from utility.util_es import search_results_only
        results = search_results_only(es, index_name, body, 3)
        
        if results.get('hits', {}).get('hits'):
            first_hit = results['hits']['hits'][0]
            doc_id = first_hit.get('_id', '')
            
            if doc_id:
                details = search_app.get_document_details(es, index_name, doc_id)
                print(f"✅ Document details retrieved:")
                print(f"  - Title: {details['title'][:50]}...")
                print(f"  - URL: {details['url'][:50]}...")
                print(f"  - Content: {details['lore'][:100]}...")
                
                if details['url']:
                    print("✅ URL extraction working!")
                    return True
                else:
                    print("❌ No URL found")
                    return False
            else:
                print("❌ No document ID found")
                return False
        else:
            print("❌ No search results")
            return False
            
    except Exception as e:
        print(f"❌ Search App test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_rag_references():
    """Test RAG chat reference improvements"""
    print("\n💬 Testing RAG chat reference improvements...")
    
    try:
        load_dotenv()
        
        from utility.util_es import get_es
        
        # Import the search function from RAG page
        import importlib.util
        spec = importlib.util.spec_from_file_location("agentic_rag", "/Users/andrewfbel/code/genai-workshops/searcheval/pages/2_Agentic_RAG.py")
        agentic_rag = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agentic_rag)
        
        es = get_es()
        
        # Test query
        test_query = "What is Oracle DBaaS?"
        
        result = agentic_rag.search_for_knowledge(es, test_query)
        
        print(f"✅ RAG Results:")
        print(f"  - Answer length: {len(result['answer'])} characters")
        print(f"  - Context passages: {len(result['retrieval_context'])}")
        print(f"  - Source URLs: {len(result['source_urls'])}")
        
        # Check for duplicates in URLs
        unique_urls = list(dict.fromkeys([url for url in result['source_urls'] if url]))
        print(f"  - Unique URLs: {len(unique_urls)}")
        
        if result['source_urls']:
            print(f"  - First URL: {result['source_urls'][0][:50]}...")
        
        if len(result['source_urls']) > 0:
            print("✅ References working!")
            return True
        else:
            print("❌ No references found")
            return False
            
    except Exception as e:
        print(f"❌ RAG test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run both tests"""
    print("🧪 Testing Both Fixes\n")
    
    search_app_ok = test_search_app_urls()
    rag_ok = test_rag_references()
    
    print(f"\n📊 Results:")
    print(f"  - Search App URLs: {'✅ PASS' if search_app_ok else '❌ FAIL'}")
    print(f"  - RAG References: {'✅ PASS' if rag_ok else '❌ FAIL'}")
    
    if search_app_ok and rag_ok:
        print("\n🎉 All fixes working correctly!")
    else:
        print("\n⚠️  Some issues remain")

if __name__ == "__main__":
    main()