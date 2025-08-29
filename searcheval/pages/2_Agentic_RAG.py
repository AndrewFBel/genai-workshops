import streamlit as st
from dotenv import load_dotenv
from datetime import datetime, timezone
import json
import os
import logging
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Database as a Service Documentation",
    page_icon="🗄️",
)

################
## IMPORTS
################

from utility.util_es import get_es, search_to_context, search_to_context_with_urls
from utility.util_llm import get_llm_util
import final_strat as strategy_module

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('streamlit_interactions.log'),
        logging.StreamHandler()
    ]
)

@st.cache_resource
def get_cached_es():
    print("Getting ES ...")
    return get_es()
es = get_cached_es()

@st.cache_resource
def get_cached_llm_util():
    print("Getting LLM Util ...")
    return get_llm_util()
llm_util = get_cached_llm_util()

def search_for_knowledge(es, original_query: str) -> Dict[str, Any]:
    """
    Search for knowledge using the Database as a Service documentation
    Returns both the answer and metadata for logging
    """
    print(f"\033[91mRAG question: {original_query}\033[0m")

    doc_limit = 6
    inner_hits_size = 3
    citation_limit = 9

    rag_system_prompt = """
Instructions:

You are an expert assistant for Database as a Service (DBaaS) documentation and support.

- Answer questions truthfully and factually using only the context presented from the DBaaS documentation.
- Focus on providing accurate information about database services, configurations, operations, and best practices.
- Do not jump to conclusions or make assumptions beyond what is stated in the documentation.
- If the answer is not present in the provided context, clearly state that you don't know rather than making up an answer.
- You must always cite the document where the answer was extracted using inline academic citation style [], using the position or multiple positions. Example: [1][3].
- Use markdown format for code examples, configuration snippets, or bulleted lists.
- Be precise, reliable, and focus on actionable information for database administrators and developers.
- When discussing database operations, include relevant warnings or prerequisites if mentioned in the context.

Context:
{context}
"""
    
    try:
        tokens_used = 0
        transformed_query = original_query

        ## pre-process the query string
        query_transform_prompt = strategy_module.get_parameters().get("query_transform_prompt", None)
        if query_transform_prompt:
            response = llm_util.transform_query_direct(
                system_prompt=query_transform_prompt, 
                user_query=original_query)
            transformed_query = response["answer"]
            total_tokens = response["total_tokens"]
            tokens_used += total_tokens
            print(f"\033[93mTransformed query: {transformed_query}\033[0m")

        ## Do the RAG
        index_name = strategy_module.get_parameters()['index_name']
        body = strategy_module.build_query(transformed_query, inner_hits_size)
        rag_context = strategy_module.get_parameters().get("rag_context", "content")
        ## determine if this strategy wants inner hits re-ranked
        rerank_inner_hits = strategy_module.get_parameters().get("rerank_inner_hits", False)

        ## RAG: R retrieval with URLs
        retrieval_context, source_urls = search_to_context_with_urls(es, index_name, transformed_query, body, rag_context, rerank_inner_hits, doc_limit, citation_limit)
        
        # Ensure we have valid data
        if not retrieval_context:
            print("WARNING: No retrieval context found")
            retrieval_context = ["No relevant documentation found for this query."]
            source_urls = [""]
        
        top_context_citations = retrieval_context[:citation_limit]
        top_source_urls = source_urls[:citation_limit] if source_urls else [""] * len(top_context_citations)

        context = "\n".join([f"[{i+1}] {text}" for i, text in enumerate(top_context_citations)])

        system_prompt = rag_system_prompt.format(context=context)

        rag_response = llm_util.rag_direct(system_prompt, top_context_citations, original_query, should_print=False)
        actual_output = rag_response["answer"]
        rag_tokens = rag_response["total_tokens"]
        tokens_used += rag_tokens

        print(f"\t\033[91mRAG answer: {actual_output}\033[0m")
        print(f"\t\033[91mTotal tokens used: {tokens_used}\033[0m")

        # Return structured data for logging
        return {
            "answer": actual_output,
            "original_query": original_query,
            "transformed_query": transformed_query,
            "retrieval_context": top_context_citations,
            "source_urls": top_source_urls,
            "tokens_used": tokens_used
        }
        
    except Exception as e:
        print(f"ERROR in search_for_knowledge: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return error response
        return {
            "answer": f"I apologize, but I encountered an error while processing your question: {str(e)}",
            "original_query": original_query,
            "transformed_query": original_query,
            "retrieval_context": [],
            "source_urls": [],
            "tokens_used": 0
        }

################
## SIMPLE RAG FLOW
################

def process_user_query(user_query: str) -> Dict[str, Any]:
    """
    Process user query through the complete RAG pipeline
    """
    try:
        # Get the RAG response
        rag_result = search_for_knowledge(es, user_query)
        
        # Log the interaction
        logging.info(f"User query processed: {user_query}")
        logging.info(f"RAG response generated with {rag_result['tokens_used']} tokens")
        
        return rag_result
    except Exception as e:
        logging.error(f"Error processing query '{user_query}': {str(e)}")
        return {
            "answer": f"I apologize, but I encountered an error while processing your question: {str(e)}",
            "original_query": user_query,
            "transformed_query": user_query,
            "retrieval_context": [],
            "source_urls": [],
            "tokens_used": 0
        }

################
## STREAMLIT UI
################

st.title("🗄️ Database as a Service Documentation Assistant")
st.markdown("Ask questions about database services, configurations, and operations.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask about database services..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("Searching documentation..."):
            # Process the query
            result = process_user_query(prompt)
            
            # Display the answer
            st.markdown(result["answer"])
            
            # Show reference sources
            if result.get('source_urls'):
                st.markdown("### 📚 Sources")
                unique_urls = list(dict.fromkeys(result['source_urls']))  # Remove duplicates while preserving order
                for i, url in enumerate(unique_urls[:5], 1):  # Show max 5 unique sources
                    if url:
                        st.markdown(f"[{i}. View Source Document]({url})")
            
            # Show additional information in an expander
            with st.expander("Query Details"):
                st.write(f"**Original Query:** {result['original_query']}")
                if result['transformed_query'] != result['original_query']:
                    st.write(f"**Transformed Query:** {result['transformed_query']}")
                st.write(f"**Tokens Used:** {result['tokens_used']}")
                
                if result['retrieval_context']:
                    st.write("**Retrieved Context:**")
                    for i, context in enumerate(result['retrieval_context'][:3], 1):
                        st.write(f"[{i}] {context[:200]}...")
                        if i <= len(result.get('source_urls', [])):
                            source_url = result['source_urls'][i-1]
                            if source_url:
                                st.markdown(f"   🔗 [Source]({source_url})")
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": result["answer"]})

# Sidebar with example queries
st.sidebar.title("Example Queries")
st.sidebar.markdown("""
Try asking about:
- How to configure database backups
- Supported database engines
- How to scale database instances
- Storage capacity limits
- Database monitoring and alerts
- Security configurations
- Performance optimization
""")

# Clear chat button
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()