#!/usr/bin/env python3
"""
Test script to verify RAG chat functionality
"""

import os
from dotenv import load_dotenv

def test_rag_chat():
    """Test RAG chat functionality"""
    print("🧪 Testing RAG Chat functionality...")
    
    try:
        load_dotenv()
        
        from utility.util_es import get_es
        
        # Import the search function from the RAG page
        import sys
        sys.path.append('/Users/andrewfbel/code/genai-workshops/searcheval')
        
        # Import directly from the file
        import importlib.util
        spec = importlib.util.spec_from_file_location("agentic_rag", "/Users/andrewfbel/code/genai-workshops/searcheval/pages/2_Agentic_RAG.py")
        agentic_rag = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agentic_rag)
        
        search_for_knowledge = agentic_rag.search_for_knowledge
        
        es = get_es()
        
        # Test query
        test_query = "What is Oracle DBaaS?"
        
        print(f"Testing query: '{test_query}'")
        
        # Test the search function
        result = search_for_knowledge(es, test_query)
        
        print(f"\n✅ Results:")
        print(f"  - Answer length: {len(result['answer'])} characters")
        print(f"  - Original query: {result['original_query']}")
        print(f"  - Transformed query: {result['transformed_query']}")
        print(f"  - Context passages: {len(result['retrieval_context'])}")
        print(f"  - Source URLs: {len(result['source_urls'])}")
        print(f"  - Tokens used: {result['tokens_used']}")
        
        if result['source_urls']:
            print(f"  - First URL: {result['source_urls'][0][:50]}...")
        
        if result['answer'] and len(result['answer']) > 50:
            print(f"  - Answer preview: {result['answer'][:100]}...")
            return True
        else:
            print("  ❌ No valid answer generated")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_rag_chat()