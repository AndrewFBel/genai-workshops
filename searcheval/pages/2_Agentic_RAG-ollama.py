import streamlit as st
from dotenv import load_dotenv
import asyncio
import json
import os
from typing import List, Dict

# Use the ollama library directly
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
## Retrieval Code for RAG
################

from utility.util_es import get_es
from utility.util_es import search_to_context
import final_strat as strategy_module

@st.cache_resource
def get_es_client():
    print("Getting ES client ...")
    return get_es()
es = get_es_client()

# This function is now called for every user query
def search_for_knowledge(es, original_query: str) -> str:
    print(f"\033[91mRAG question sent to Elasticsearch: {original_query}\033[0m")
    doc_limit = 6
    inner_hits_size = 3
    citation_limit = 9
    query_string = original_query
    index_name = strategy_module.get_parameters()['index_name']
    body = strategy_module.build_query(query_string, inner_hits_size)
    rag_context = strategy_module.get_parameters().get("rag_context", "lore")
    rerank_inner_hits = strategy_module.get_parameters().get("rerank_inner_hits", False)
    retrieval_context  = search_to_context(es, index_name, query_string, body, rag_context, rerank_inner_hits, doc_limit, citation_limit)
    top_context_citations = retrieval_context[:citation_limit]
    context = "\n".join([f"[{i+1}] {text}" for i, text in enumerate(top_context_citations)])
    return context

################
## LLM and PROMPT
################

# A new, simpler system prompt that instructs the LLM to use the provided context.
system_prompt = """
You are a helpful documentation assistant.
You will be provided with a user's question and a context retrieved from a documentation search.
Your task is to answer the user's question based *only* on the provided context.
Present your findings to the user in a clear and concise way. Use Markdown for formatting.
If the context does not contain the answer, state that you could not find the information in the documentation.
Do not use any of your own knowledge.
"""

################
## Chat
################

async def prompt_ai(user_prompt: str):
    # 1. Always send the user query to Elasticsearch first.
    rag_context = search_for_knowledge(es, user_prompt)

    # Log the RAG response from Elasticsearch for comparison.
    print("\n\033[94m--- RAG Response from Elasticsearch ---\033[0m")
    print(rag_context)
    print("\033[94m---------------------------------------\033[0m\n")

    # 2. Prepare the messages for the LLM.
    llm_messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': f"""Here is the context from the documentation search:

{rag_context}

Please answer the following question based only on this context:

{user_prompt}"""}
    ]

    # 3. Call the LLM once with the context and question.
    response = ollama.chat(
        model='llama2',
        messages=llm_messages,
    )
    
    final_answer = response['message']['content']

    # Log the final answer provided to the user for comparison.
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

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    # React to user input
    if prompt := st.chat_input("Ask a question about the documentation:"):
        # Add user message to history and display it
        st.session_state.messages.append({'role': 'user', 'content': prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get and display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            
            # Call the refactored prompt_ai function
            full_response = await prompt_ai(prompt)
            
            message_placeholder.markdown(full_response)
            # Add assistant response to history
            st.session_state.messages.append({'role': 'assistant', 'content': full_response})

if __name__ == "__main__":
    asyncio.run(main())