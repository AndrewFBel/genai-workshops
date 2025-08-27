st.set_page_config(
    page_title="Agentic RAG App",
    page_icon="🧠",
)

import streamlit as st
from datetime import datetime, timezone
import asyncio
import os
from typing import List, Union

# Ollama LLM
import ollama

st.set_page_config(
    page_title="Documentation RAG App",
    page_icon="📄",
)


################
## Retrieval Code for RAG
################


# --- RAG Retrieval for Documentation ---
from utility.util_es import get_es, search_to_context
import final_strat as strategy_module

@st.cache_resource
def get_es_client():
    return get_es()
es = get_es_client()

def search_for_documentation(es, original_query: str) -> str:
    """
    Retrieve relevant documentation context and generate an answer using Ollama LLM.
    """
    doc_limit = 6
    inner_hits_size = 3
    citation_limit = 9

    rag_system_prompt = """
Instructions:
- You are an assistant for technical documentation question-answering tasks.
- Answer questions truthfully and factually using only the context presented.
- Do not jump to conclusions or make assumptions.
- If the answer is not present in the provided context, say you don't know.
- Always cite the document where the answer was extracted using inline academic citation style [], using the position(s). Example: [1][3].
- Use markdown format for code examples or bulleted lists.
- Be correct, factual, precise, and reliable.

Context:
{context}
"""

    # Query transform (if any)
    query_transform_prompt = strategy_module.get_parameters().get("query_transform_prompt", None)
    if query_transform_prompt:
        query_string = original_query  # For now, skip LLM transform
    else:
        query_string = original_query

    index_name = strategy_module.get_parameters()['index_name']
    body = strategy_module.build_query(query_string, inner_hits_size)
    rag_context = strategy_module.get_parameters().get("rag_context", "docs")
    rerank_inner_hits = strategy_module.get_parameters().get("rerank_inner_hits", False)

    retrieval_context = search_to_context(es, index_name, query_string, body, rag_context, rerank_inner_hits, doc_limit, citation_limit)
    top_context_citations = retrieval_context[:citation_limit]
    context = "\n".join([f"[{i+1}] {text}" for i, text in enumerate(top_context_citations)])

    system_prompt = rag_system_prompt.format(context=context)

    # --- Ollama LLM call ---
    ollama_model = os.environ.get("OLLAMA_MODEL", "llama3")
    ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    ollama_client = ollama.Client(host=ollama_host)
    prompt = f"{system_prompt}\n\nQuestion: {original_query}"
    response = ollama_client.generate(model=ollama_model, prompt=prompt)
    actual_output = response['response'] if 'response' in response else str(response)
    return actual_output




################
## AGENTs and MODELS
################


# --- System prompt for documentation agent ---
agent_system_prompt = """
You are an expert technical documentation assistant.
Your primary task is to look up factual information using external research tools rather than relying on your own internal knowledge.
Always rely on external research before answering any documentation-related question.
Use Markdown bullet points to present facts you’ve discovered through your research.
Only provide facts from your research — avoid speculation or drawing conclusions beyond what you’ve found.
Do not elaborate or add additional commentary—just repeat the researched facts in bullet points, and then provide a short concluding statement.
If no information is found, clearly state that no data was located and prompt the user for clarification.
"""



################
## Chat
################
## The part that streams a response from the Agent


# --- Async wrapper for RAG response ---
async def prompt_ai(message):
    response = search_for_documentation(es, message)
    yield response



        

###############
## Some Utilities
###############


# --- Simple chat history for Streamlit ---
def _gen_system_prompt(prompt: str) -> dict:
    return {"role": "system", "content": prompt}

def _gen_ai_response_obj(response_content: str) -> dict:
    return {"role": "ai", "content": response_content}

def _gen_user_prompt_obj(prompt: str) -> dict:
    return {"role": "user", "content": prompt}





###############
## The UI
###############


async def main():
    st.title("Documentation RAG Chat")
    if st.button("Reset Chat"):
        st.session_state.messages = [
            _gen_system_prompt(agent_system_prompt),
            _gen_ai_response_obj("Welcome to the documentation chat! Ask me a question.")
        ]
        st.rerun()

    if "messages" not in st.session_state:
        st.session_state.messages = [_gen_system_prompt(agent_system_prompt)]

    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "system":
            continue
        with st.chat_message("human" if message["role"] == "user" else "ai"):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Ask a documentation question:"):
        st.chat_message("user").markdown(prompt)
        response_content = ""
        with st.chat_message("ai"):
            message_placeholder = st.empty()
            async for chunk in prompt_ai(prompt):
                response_content += chunk
                message_placeholder.markdown(response_content)
        st.session_state.messages.append(_gen_user_prompt_obj(prompt))
        st.session_state.messages.append(_gen_ai_response_obj(response_content))

if __name__ == "__main__":
    asyncio.run(main())