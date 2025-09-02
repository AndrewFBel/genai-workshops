# Elasticsearch Documentation Retrieval System

A comprehensive Retrieval-Augmented Generation (RAG) system demonstrating advanced Elasticsearch semantic search capabilities for documentation retrieval. This project was developed as a proof-of-concept showcasing various search strategies and evaluation methodologies.

## 🏗️ Project Structure

```
genai-workshops/
└── searcheval/                    # Main project directory
    ├── README.md                  # Basic setup instructions
    ├── requirements.txt           # Python dependencies
    ├── .env.example              # Environment configuration template
    ├── golden_data.csv           # Test dataset for evaluation
    ├── final_strat.py            # Production search strategy
    ├── evaluate.py               # Evaluation framework
    ├── streamlit_ui.py           # Main Streamlit application
    ├── Search_Evaluation.ipynb   # Jupyter notebook for analysis
    │
    ├── strategies/               # Search strategy implementations
    │   ├── 1_default_bm25.py    # Baseline BM25 search
    │   ├── 2_hybrid_elser.py    # Hybrid with ELSER
    │   ├── 3_hybrid_e5.py       # Hybrid with E5 embeddings
    │   ├── 4_hybrid_e5_qt.py    # E5 + Query Transformation
    │   ├── 5_hybrid_e5_rr.py    # E5 + Reranking
    │   └── 6_hybrid_e5_qt_rr.py # Full pipeline (E5 + QT + RR)
    │
    ├── pages/                    # Streamlit pages
    │   ├── 1_Search_App.py      # Basic search interface
    │   └── 2_Agentic_RAG.py     # Advanced RAG chat interface
    │
    ├── utility/                  # Core utilities
    │   ├── util_es.py           # Elasticsearch client and operations
    │   ├── util_llm.py          # LLM integration (Ollama)
    │   ├── util_simple_eval.py  # Evaluation metrics
    │   ├── util_deep_eval.py    # Advanced evaluation
    │   ├── util_vis_result.py   # Result visualization
    │   ├── util_llm_rag_cache.py        # RAG response caching
    │   └── util_query_transform_cache.py # Query transformation caching
    │
    ├── mappings/                 # Elasticsearch index configurations
    │   ├── dbaas-confluence-semantic.json  # Semantic search mapping
    │   └── dbaas-confluence-html-export.json # HTML export mapping
    │
    ├── tests/                    # Test suite
    │   ├── test_setup.py        # Environment and setup tests
    │   └── test_rag_chat.py     # RAG functionality tests
    │
    └── .caches/                  # Performance optimization caches
        ├── .rag_cache.json      # Cached RAG responses
        ├── .query_transform_cache.json # Cached query transformations
        └── .transform_cache.json # General transformation cache
```

## 🎯 Core Components

### Search Strategies
The project implements a progressive enhancement approach with six different search strategies:

1. **BM25 Baseline** (`1_default_bm25.py`)
   - Traditional keyword-based search
   - Multi-match query on title and content fields
   - Serves as performance baseline

2. **Hybrid ELSER** (`2_hybrid_elser.py`)
   - Combines BM25 with Elasticsearch's ELSER (Elastic Learned Sparse EncodeR)
   - Uses sparse vector representations for semantic understanding
   - Reciprocal Rank Fusion (RRF) for result combination

3. **Hybrid E5** (`3_hybrid_e5.py`)
   - Integrates E5 dense embeddings with BM25
   - Dense vector search for semantic similarity
   - RRF for optimal result ranking

4. **E5 + Query Transformation** (`4_hybrid_e5_qt.py`)
   - Adds LLM-based query preprocessing
   - Transforms complex queries into optimized search terms
   - Maintains hybrid search approach

5. **E5 + Reranking** (`5_hybrid_e5_rr.py`)
   - Implements semantic reranking of results
   - Post-processing relevance scoring
   - Enhanced result quality

6. **Full Pipeline** (`6_hybrid_e5_qt_rr.py`)
   - Complete implementation with all enhancements
   - Query transformation + hybrid search + reranking
   - Production-ready configuration

### RAG Pipeline Architecture

```
User Query → Query Transformation → Elasticsearch Retrieval → Reranking → Context Assembly → LLM Generation → Response
     ↓              ↓                        ↓                    ↓              ↓              ↓
  [Optional]    [LLM-based]           [Hybrid Search]      [ML Reranker]   [Context Prep]  [Ollama LLM]
```

### Key Utilities

- **`util_es.py`**: Elasticsearch client management, index operations, search execution
- **`util_llm.py`**: Ollama integration for local LLM inference
- **`util_simple_eval.py`**: Evaluation metrics (citation correctness, semantic similarity)
- **`util_vis_result.py`**: Result visualization and analysis tools

## 🚀 Getting Started

### Prerequisites

1. **Elasticsearch Cluster** (8.0+)
   - Semantic search capabilities enabled
   - Inference API configured
   - Required models: E5, ELSER (optional)

2. **Ollama** (Local LLM)
   - Installed and running
   - Model: llama3.2 (or compatible)

3. **Python Environment** (3.8+)
   - All dependencies from requirements.txt

### Quick Setup

1. **Clone and Navigate**
   ```bash
   git clone <repository>
   cd genai-workshops/searcheval
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your Elasticsearch and Ollama settings
   ```

4. **Setup Ollama**
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Start service
   ollama serve
   
   # Pull model
   ollama pull llama3.2
   ```

5. **Verify Setup**
   ```bash
   python tests/test_setup.py
   ```

### Running the Application

#### Interactive Chat Interface
```bash
streamlit run pages/2_Agentic_RAG.py
```

#### Search Evaluation
```bash
jupyter notebook Search_Evaluation.ipynb
```

#### Command Line Evaluation
```bash
python evaluate.py
```

## 🔧 Configuration

### Environment Variables

```env
# Elasticsearch Configuration
ES_SERVER=https://your-elasticsearch-endpoint.com
ES_API_KEY=your_elasticsearch_api_key_here

# Ollama Configuration  
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Optional Settings
LOG_LEVEL=INFO
CACHE_ENABLED=true
```

### Index Configuration

The system expects an Elasticsearch index with semantic search capabilities:

- **Index Name**: `dbaas-confluence-semantic` (configurable)
- **Required Fields**: `title`, `content`, `content_e5`, `content_elser`
- **Semantic Text Fields**: Configured with appropriate inference endpoints
- **Custom Analyzers**: Domain-specific text analysis

See `mappings/dbaas-confluence-semantic.json` for complete configuration.

## 📊 Evaluation Framework

### Metrics

- **Citation Correctness**: Validates proper citation format [1], [2], etc.
- **Semantic Similarity**: TF-IDF based similarity scoring
- **Completeness**: Coverage of key terms from expected answers
- **Response Quality**: LLM-based evaluation of answer relevance

### Golden Dataset

Test queries stored in `golden_data.csv`:
```csv
query,challenge,best_ids,natural_answer
"How do I configure database backups?",simple,backup_config,"Database backups can be configured..."
```

### Running Evaluations

1. **Jupyter Notebook**: Interactive analysis with visualizations
2. **Command Line**: Automated evaluation across all strategies
3. **Streamlit UI**: Real-time evaluation during development

## 🎨 User Interfaces

### 1. Search App (`pages/1_Search_App.py`)
- Basic search interface
- Strategy comparison
- Result visualization

### 2. Agentic RAG (`pages/2_Agentic_RAG.py`)
- Conversational interface
- Context-aware responses
- Citation tracking
- Query history

## 🔍 Advanced Features

### Caching System
- **RAG Cache**: Stores generated responses
- **Query Transform Cache**: Caches transformed queries
- **Performance Optimization**: Reduces API calls and latency

### Logging
- Comprehensive interaction logging
- Query transformation tracking
- Performance metrics
- Error handling and debugging

### Extensibility
- Modular strategy system
- Pluggable evaluation metrics
- Configurable LLM backends
- Custom analyzer support

## 🛠️ Development

### Adding New Search Strategies

1. Create new file in `strategies/` directory
2. Implement required functions:
   ```python
   def get_parameters() -> dict:
       # Strategy configuration
   
   def build_query(query_string: str, inner_hits_size: int = 3) -> dict:
       # Elasticsearch query DSL
   ```

### Custom Evaluation Metrics

Extend `util_simple_eval.py` or `util_deep_eval.py` with new metrics:
```python
def custom_metric(expected: str, actual: str) -> float:
    # Implementation
    return score
```

### Testing

```bash
# Run all tests
python -m pytest tests/

# Specific test
python tests/test_rag_chat.py
```

## 📈 Performance Considerations

- **Index Optimization**: Proper sharding and replica configuration
- **Caching Strategy**: Multi-level caching for performance
- **Batch Processing**: Efficient evaluation of multiple queries
- **Resource Management**: Memory and CPU optimization for local LLM

## 🔒 Security

- API key management through environment variables
- Local LLM processing for data privacy
- Secure Elasticsearch connections
- Input validation and sanitization

## 📚 Documentation

- **Technical Documentation**: Inline code documentation
- **API Reference**: Utility function documentation
- **Configuration Guide**: Environment and index setup
- **Troubleshooting**: Common issues and solutions

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Implement changes with tests
4. Update documentation
5. Submit pull request

## 📄 License

This project is part of the GenAI Workshops repository and follows the same licensing terms.

---

*This project demonstrates advanced Elasticsearch semantic search capabilities and serves as a comprehensive example for building production-ready documentation retrieval systems.*