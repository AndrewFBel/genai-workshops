import streamlit as st

st.set_page_config(
    page_title="Search App",
    page_icon="🔍",
)


# ## For Local Dev
# from dotenv import load_dotenv
# load_dotenv()

from datetime import datetime, timezone
import asyncio
import json
import os

import random
from typing import List, Union

import nest_asyncio
nest_asyncio.apply()

################
## Retrieval Code for Search
################


from utility.util_es import get_es
from utility.util_llm import LLMUtil, get_llm_util
from utility.util_es import search_results_only
import final_strat as strategy_module

@st.cache_resource
def get_es_client():
    print("Getting ES client ...")
    return get_es()
es = get_es_client()


def search_for_hits(es, original_query: str) -> str:

    doc_limit = 10
    query_string = original_query
    inner_hits_size = 3

    index_name = strategy_module.get_parameters()['index_name']
    body = strategy_module.build_query(query_string, inner_hits_size)
    
    search_results  = search_results_only(es, index_name, body,  doc_limit)

    return search_results


def get_document_details(es, index_name, doc_id):
    """Get document details by ID"""
    try:
        doc = es.get(index=index_name, id=doc_id)
        source = doc.get("_source", {})
        return {
            "url": (source.get("page_url") or source.get("url") or source.get("source_url") or source.get("link") or ""),
            "title": source.get("title", "Untitled Document"),
            "lore": source.get("lore", source.get("content", source.get("text", "No content available")))
        }
    except Exception as e:
        return {
            "url": "",
            "title": f"Document {doc_id}",
            "lore": "Content not available"
        }

def render_results(search_results): 
    index_name = strategy_module.get_parameters()['index_name']
    
    for hit in search_results['hits']['hits']:
        # Try to get from _source first (if available)
        if "_source" in hit:
            source = hit["_source"]
            url = (source.get("page_url") or source.get("url") or source.get("source_url") or source.get("link") or "")
            title = source.get("title", "Untitled Document")
            lore = source.get("lore", source.get("content", source.get("text", "No content available")))
        else:
            # Fallback: get document by ID
            doc_id = hit.get("_id", "")
            details = get_document_details(es, index_name, doc_id)
            url = details["url"]
            title = details["title"]
            lore = details["lore"]

        with st.container():
            if url:
                st.markdown(
                    f"""
                    <div style="border: 1px solid #ddd; border-radius: 10px; padding: 10px; margin-bottom: 10px;">
                        <a href="{url}" target="_blank"><h5>{title}</h5></a>
                        <p>{lore[:200]}...</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style="border: 1px solid #ddd; border-radius: 10px; padding: 10px; margin-bottom: 10px;">
                        <h5>{title}</h5>
                        <p>{lore[:200]}...</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


st.title("Search App")

query = st.text_input("Enter your search query:", on_change=lambda: st.session_state.update({"search_button": True}))

if st.session_state.get("search_button") and query:
    st.session_state["search_button"] = False
    with st.spinner("Searching..."):
        search_results = search_for_hits(es, query)
        if search_results:
            st.write("Search Results:")
            render_results(search_results)
        else:
            st.write("No results found.")

