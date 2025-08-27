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
    page_title="Agentic RAG App",
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

# This function remains the same, it's the tool's implementation
def search_for_knowledge(es, original_query: str) -> str:
    print(f"\033[91mRAG question: {original_query}\033[0m")
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
## AGENT and TOOLS
################

# Define the tool as a plain function
def search_documentation(query: str) -> str:
    """Search for knowledge about in the documentation"""
    print(f"Executing search_documentation with query: {query}")
    return search_for_knowledge(es, query)

# Map tool names to functions
AVAILABLE_TOOLS = {
    "search_documentation": search_documentation,
}

# Create the tool definition for Ollama
TOOLS_DEFINITION = [
    {
        'type': 'function',
        'function': {
            'name': 'search_documentation',
            'description': 'Search for knowledge in the documentation',
            'parameters': {
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'The search query for the documentation'
                    }
                },
                'required': ['query']
            }
        }
    }
]

agent_system_prompt = """
You are an expert documentation retrieval assistant.
Your primary task is to look up factual information using the 'search_documentation' tool rather than relying on your own internal knowledge.
Then you will present your findings to the user in a clear and concise way.

Instructions:
1. **Always rely on external research.** Before answering any question, consult the available tools for relevant information.
2. **Use Markdown** to present facts you’ve discovered through your research.
3. **Only provide facts from your research** — avoid speculation or drawing conclusions beyond what you’ve found.
4. **Do not elaborate or add additional commentary**— just repeat the researched facts.
5. **If no information is found,** clearly state that no data was located and prompt the user for clarification.
"""

################
## Chat
################

def _debug_chat_history(messages: List[Dict], when: str = None):
    if when:
        print(f"######### {when} : Chat History #########")
    for message in messages:
        role = message['role']
        content = message['content']
        print(f"{role}: {content}")
    print("")

async def prompt_ai(prompt: str):
    # Add the new user prompt to the history
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    
    # Use a non-streaming approach for simplicity with tool calls
    # First API call to see if a tool is needed
    response = ollama.chat(
        model='llama2',
        messages=st.session_state.messages,
        tools=TOOLS_DEFINITION
    )
    
    st.session_state.messages.append(response['message'])
    
    # Check if the model wants to use a tool
    if response['message'].get('tool_calls'):
        tool_calls = response['message']['tool_calls']
        
        # Execute tool calls
        for tool_call in tool_calls:
            function_name = tool_call['function']['name']
            function_to_call = AVAILABLE_TOOLS.get(function_name)
            if function_to_call:
                function_args = tool_call['function']['arguments']
                query = function_args.get('query')
                
                # Call the function
                tool_output = function_to_call(query=query)
                
                # Add tool output to the history
                st.session_state.messages.append({
                    'role': 'tool',
                    'content': tool_output,
                })
            else:
                print(f"Error: Tool '{function_name}' not found.")

        # Second API call to get the final response based on tool output
        final_response = ollama.chat(
            model='llama2',
            messages=st.session_state.messages
        )
        
        final_content = final_response['message']['content']
        st.session_state.messages.append(final_response['message'])
        yield final_content
    else:
        # No tool call, just yield the content directly
        final_content = response['message']['content']
        yield final_content


###############
## The UI
###############

async def main():
    st.title("Documentation Assistant")
    if st.button("Reset Chat"):
        st.session_state.messages = [
            {'role': 'system', 'content': agent_system_prompt},
            {'role': 'assistant', 'content': "Welcome to the Documentation Assistant chat! Ask me a question."}
        ]
        st.rerun()

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {'role': 'system', 'content': agent_system_prompt},
            {'role': 'assistant', 'content': "Welcome to the Documentation Assistant chat! Ask me a question."}
        ]

    # Display chat messages
    for message in st.session_state.messages:
        if message['role'] == 'system' or message['role'] == 'tool':
            continue
        
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    # React to user input
    if prompt := st.chat_input("Ask a question about the documentation:"):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # The new prompt_ai function manages history itself, so we just pass the prompt
            async for chunk in prompt_ai(prompt):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            # History is now managed inside prompt_ai and the main UI loop

if __name__ == "__main__":
    asyncio.run(main())