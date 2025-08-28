import streamlit as st

st.set_page_config(
    page_title="Database as a Service Documentation",
    page_icon="🗄️",
    initial_sidebar_state="expanded",
    layout="wide"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .metric-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem;
    }
    
    .quick-start {
        background: #e3f2fd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2196f3;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🗄️ Database as a Service Documentation</h1>
    <p>Intelligent documentation search and Q&A system powered by RAG</p>
</div>
""", unsafe_allow_html=True)

# Navigation message
st.sidebar.success("👈 Select a tool from the sidebar to get started!")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>🔍 Search Documentation</h3>
        <p>Search through Database as a Service documentation using advanced semantic search capabilities. Find relevant information quickly with hybrid search combining keyword and vector similarity.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <h3>💬 Ask Questions</h3>
        <p>Get intelligent answers to your database questions using our RAG (Retrieval-Augmented Generation) system. Ask about configurations, best practices, troubleshooting, and more.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <h3>📊 Evaluation Framework</h3>
        <p>Comprehensive evaluation system to measure and improve search relevance and answer quality using multiple metrics including citation correctness and semantic similarity.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="quick-start">
        <h3>🚀 Quick Start</h3>
        <ol>
            <li><strong>Search App</strong> - Find specific documentation</li>
            <li><strong>RAG Chat</strong> - Ask questions and get answers</li>
            <li><strong>Evaluation</strong> - Test and improve performance</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # System status indicators
    st.markdown("### 🔧 System Status")
    
    # Mock status indicators (you can make these dynamic)
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        <div class="metric-container">
            <h4>🟢 Elasticsearch</h4>
            <p>Connected</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_b:
        st.markdown("""
        <div class="metric-container">
            <h4>🟢 Ollama LLM</h4>
            <p>Ready</p>
        </div>
        """, unsafe_allow_html=True)

# Footer section
st.markdown("---")
st.markdown("""
### 📋 Available Tools

**🔍 Search App** - Direct search interface for finding specific documentation pages and content.

**🗄️ RAG Chat** - Interactive chat interface that answers questions using retrieved documentation context.

Both tools use:
- **Elasticsearch** for fast, semantic search
- **Local Ollama LLM** (llama3.2) for privacy-focused AI responses  
- **Hybrid search** combining keyword and vector similarity
- **Citation tracking** for source transparency

---
*Powered by Elasticsearch + Ollama + Streamlit*
""")