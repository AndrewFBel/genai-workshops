import streamlit as st
from dotenv import load_dotenv
import asyncio
import json
import os
from typing import List, Dict

import ollama

import nest_asyncio
nest_asyncio.apply()

import requests
from io import StringIO
if not os.path.exists('.env.instruqt'):
    env_text = requests.get('http://kubernetes-vm:9000/env').text
    with open('.env.instruqt', 'w') as f:
        f.write(env_text)
load_dotenv('.env.instruqt')

st.set_page_config(
    page_title="RAG App",
    page_icon="🧠",
)

################
## UTILITIES
################

from utility.util_es import get_es, search_to_context
import final_strat as strategy_module

@st.cache_resource
def get_es_client():
    print("Getting ES client ...")
    return get_es()
es = get_es_client()

def transform_query(prompt: str, user_query: str) -> str:
    """Uses the LLM to transform the user's query based on a given prompt."""
    print(f"\033[93mTransforming query with prompt: {prompt}\033[0m")
    response = ollama.chat(
        model='llama3.2',
        messages=[
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': user_query}
        ]
    )
    transformed_content = response['message']['content']
    print(f"\033[93mOriginal query: {user_query} -> Transformed query: {transformed_content}\033[0m")
    return transformed_content

################
## RAG PIPELINE
################

async def rag_pipeline(user_prompt: str):
    """Executes the full RAG pipeline based on the defined strategy."""

    # 1. Get the search strategy from the strategy module
    strategy_params = strategy_module.get_parameters()
    print(f"Loaded search strategy: {strategy_params}")

    # 2. Conditionally transform the user query
    query_transform_prompt = strategy_params.get("query_transform_prompt")
    if query_transform_prompt:
        search_query = transform_query(query_transform_prompt, user_prompt)
    else:
        search_query = user_prompt

    # 3. Perform hybrid search in Elasticsearch
    index_name = strategy_params['index_name']
    inner_hits_size = 3  # Define this or get from params if needed
    body = strategy_module.build_query(search_query, inner_hits_size)
    
    # 4. Conditionally rerank the results
    rerank_inner_hits = strategy_params.get("rerank_inner_hits", False)
    
    doc_limit = 6
    citation_limit = 9
    rag_context_field = strategy_params.get("rag_context", "lore")

    # Execute search and get context
    retrieved_chunks = search_to_context(
        es, index_name, search_query, body, rag_context_field, 
        rerank_inner_hits, doc_limit, citation_limit
    )
    rag_context = "\n".join([f"[{i+1}] {text}" for i, text in enumerate(retrieved_chunks)])

    # Log the raw RAG context for comparison
    print("\n\033[94m--- RAG Context from Elasticsearch ---\033[0m")
    print(rag_context)
    print("\033[94m--------------------------------------\033[0m\n")

    # 5. Send to LLM to form a nice answer
    system_prompt = """
    You are a helpful documentation assistant.
    You will be provided with a user's question and a context retrieved from a documentation search.
    Your task is to answer the user's question based *only* on the provided context.
    Present your findings to the user in a clear and concise way. Use Markdown for formatting.
    If the context does not contain the answer, state that you could not find the information in the documentation.
    Do not use any of your own knowledge.
    """

    llm_messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': f"""Here is the context from the documentation search:

{rag_context}

Please answer the following question based only on this context:

{user_prompt}"""}
    ]

    response = ollama.chat(
        model='llama3.2',
        messages=llm_messages,
    )
    
    final_answer = response['message']['content']

    # Log the final answer for comparison
    print("\n\033[92m--- Final Answer Provided to User ---\033[0m")
    print(final_answer)
    print("\033[92m-------------------------------------\033[0m\n")
    
    return final_answer

###############
## The UI
###############

async def main():
    st.title("Documentation Assistant")
    if st.button("Reset Chat"):
        st.session_state.messages = []
        st.rerun()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    if prompt := st.chat_input("Ask a question about the documentation:"):
        st.session_state.messages.append({'role': 'user', 'content': prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            
            full_response = await rag_pipeline(prompt)
            
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({'role': 'assistant', 'content': full_response})

if __name__ == "__main__":
    asyncio.run(main())