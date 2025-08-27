import streamlit as st
from dotenv import load_dotenv
import asyncio
import os

# Ensure nested event loops work in Streamlit
import nest_asyncio
nest_asyncio.apply()

import requests

st.set_page_config(
    page_title="Agentic RAG App",
    page_icon="🧠",
)

# Load env from Instruqt helper if running in that environment
if not os.path.exists('.env.instruqt'):
    try:
        env_text = requests.get('http://kubernetes-vm:9000/env').text
        with open('.env.instruqt', 'w') as f:
            f.write(env_text)
    except Exception:
        # Fallback silently if not available
        pass
load_dotenv('.env.instruqt')

################
## Utilities
################
from utility.util_es import get_es, search_to_context
from utility.util_llm import get_llm_util
import final_strat as strategy_module

@st.cache_resource
def get_es_client():
    print("Getting ES client ...")
    return get_es()

es = get_es_client()
llm_util = get_llm_util()

################
## RAG pipeline (mirrors Kibana Playground behavior)
################
async def rag_pipeline(user_prompt: str) -> str:
    """Executes the full RAG pipeline based on the defined strategy."""
    # 1) Strategy params
    strategy_params = strategy_module.get_parameters()
    print(f"Loaded search strategy: {strategy_params}")

    # 2) Optional query transform
    query_transform_prompt = strategy_params.get("query_transform_prompt")
    model_name = strategy_params.get("model_name", "llama3.2")

    if query_transform_prompt:
        transformed_response = llm_util.transform_query_direct(query_transform_prompt, user_prompt, model_name)
        search_query = transformed_response['answer']
    else:
        search_query = user_prompt

    # 3) Build ES hybrid query
    index_name = strategy_params['index_name']
    inner_hits_size = 3
    body = strategy_module.build_query(search_query, inner_hits_size)

    # 4) Optional rerank of inner hits
    rerank_inner_hits = strategy_params.get("rerank_inner_hits", False)

    doc_limit = 6
    citation_limit = 9
    rag_context_field = strategy_params.get("rag_context", "lore")

    retrieved_chunks = search_to_context(
        es, index_name, search_query, body, rag_context_field,
        rerank_inner_hits, doc_limit, citation_limit
    )

    # For debugging: show the exact context being passed to the LLM
    rag_context = "\n".join([f"[{i+1}] {text}" for i, text in enumerate(retrieved_chunks)])
    print("\n\033[94m--- RAG Context from Elasticsearch ---\033[0m")
    print(rag_context)
    print("\033[94m--------------------------------------\033[0m\n")

    # 5) Ask LLM using ONLY the retrieved context
    system_prompt = """
    You are a helpful documentation assistant.
    You will be provided with a user's question and a context retrieved from a documentation search.
    Your task is to answer the user's question based only on the provided context.
    Present your findings to the user in a clear and concise way. Use Markdown for formatting.
    If the context does not contain the answer, state that you could not find the information in the documentation.
    Do not use any of your own knowledge.
    """

    rag_response = llm_util.rag_direct(system_prompt, retrieved_chunks, user_prompt, model_name)
    final_answer = rag_response['answer']

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

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    # React to user input
    if prompt := st.chat_input("Ask a question about the documentation:"):
        st.session_state.messages.append({'role': 'user', 'content': prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("Thinking...")

            full_response = await rag_pipeline(prompt)
            placeholder.markdown(full_response)
            st.session_state.messages.append({'role': 'assistant', 'content': full_response})

if __name__ == "__main__":
    asyncio.run(main())