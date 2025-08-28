# Database as a Service Documentation RAG System

This project provides a Retrieval-Augmented Generation (RAG) system for answering questions about Database as a Service (DBaaS) documentation using Elasticsearch and local Ollama LLM models.

## Features

- **Elasticsearch Integration**: Uses Elasticsearch with semantic search capabilities
- **Local LLM**: Powered by Ollama (llama3.2) for privacy and cost efficiency
- **RAG Pipeline**: Complete query transformation → retrieval → generation flow
- **Evaluation Framework**: Simple evaluation metrics for RAG quality assessment
- **Interactive UI**: Streamlit-based chat interface
- **Logging**: Comprehensive logging of queries, transformations, and responses

## Setup

### Prerequisites

1. **Elasticsearch**: Access to an Elasticsearch cluster with the `dbaas-confluence-semantic` index
2. **Ollama**: Local Ollama installation with llama3.2 model
3. **Python**: Python 3.8+ with required dependencies

### Installation

1. Clone the repository and navigate to the searcheval directory:
```bash
cd /path/to/genai-workshops/searcheval
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install and start Ollama:
```bash
# Install Ollama (macOS)
brew install ollama

# Start Ollama service
ollama serve

# Pull the llama3.2 model
ollama pull llama3.2
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Elasticsearch and Ollama settings
```

### Environment Variables

Create a `.env` file with the following variables:

```env
# Elasticsearch Configuration
ES_SERVER=https://your-elasticsearch-endpoint.com
ES_API_KEY=your_elasticsearch_api_key_here

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Optional: Logging Configuration
LOG_LEVEL=INFO
```

## Usage

### Interactive Chat Interface

Start the Streamlit application:

```bash
streamlit run pages/2_Agentic_RAG.py
```

This provides a chat interface where you can ask questions about database services, such as:
- "How do I configure database backups?"
- "What database engines are supported?"
- "How do I scale my database instance?"

### Jupyter Notebook Evaluation

Run the evaluation notebook to test different search strategies:

```bash
jupyter notebook Search_Evaluation.ipynb
```

The notebook will:
1. Load golden test data from `golden_data.csv`
2. Run queries through the RAG pipeline
3. Evaluate responses using simple metrics
4. Generate evaluation reports

### Command Line Evaluation

You can also run evaluations programmatically:

```python
from evaluate import run_deepeval, output_deepeval_results
from utility.util_es import get_es
import final_strat as strategy_module

# Load test data and run evaluation
es = get_es()
# ... evaluation code
```

## Architecture

### RAG Pipeline

1. **Query Transformation**: Optional query preprocessing using LLM
2. **Elasticsearch Retrieval**: Hybrid search combining semantic and keyword matching
3. **Context Ranking**: Re-ranking of retrieved passages
4. **Answer Generation**: LLM generates response with citations

### Key Components

- `final_strat.py`: Main search strategy configuration
- `utility/util_llm.py`: Ollama LLM integration
- `utility/util_es.py`: Elasticsearch utilities
- `utility/util_simple_eval.py`: Simple evaluation metrics
- `evaluate.py`: Evaluation framework
- `pages/2_Agentic_RAG.py`: Streamlit UI

### Search Strategy

The system uses a hybrid approach combining:
- **Semantic Search**: Vector embeddings using E5 model
- **Keyword Search**: Traditional text matching on title and content fields
- **RRF (Reciprocal Rank Fusion)**: Combines results from both approaches

## Evaluation

The system includes evaluation capabilities using simple metrics:

- **Citation Correctness**: Checks for proper citation format [1], [2], etc.
- **Semantic Similarity**: TF-IDF based similarity between expected and actual answers
- **Completeness**: Measures coverage of key terms from expected answers

### Golden Data Format

Test queries are stored in `golden_data.csv`:

```csv
query,challenge,best_ids,natural_answer
"How do I configure database backups?",simple,backup_configuration,"Database backups can be configured through..."
```

## Logging

The system logs all interactions including:
- Original user queries
- Transformed queries (if query transformation is used)
- Retrieved context passages
- Generated responses
- Token usage statistics

Logs are written to:
- `streamlit_interactions.log` (Streamlit UI)
- Console output (development)

## Customization

### Adding New Search Strategies

1. Create a new strategy file following the pattern in `final_strat.py`
2. Implement `get_parameters()` and `build_query()` functions
3. Add the strategy to the evaluation framework

### Modifying Prompts

Update prompts in:
- `final_strat.py`: Query transformation prompt
- `pages/2_Agentic_RAG.py`: RAG system prompt
- `evaluate.py`: Evaluation prompts

### Changing LLM Models

Update the `OLLAMA_MODEL` environment variable to use different Ollama models:
- `llama3.2` (default)
- `llama3.1`
- `mistral`
- `codellama`

## Troubleshooting

### Common Issues

1. **Elasticsearch Connection**: Verify ES_SERVER and ES_API_KEY are correct
2. **Ollama Not Running**: Ensure `ollama serve` is running
3. **Model Not Found**: Run `ollama pull llama3.2` to download the model
4. **Index Not Found**: Verify the `dbaas-confluence-semantic` index exists

### Debug Mode

Enable debug logging by setting `LOG_LEVEL=DEBUG` in your `.env` file.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the GenAI Workshops repository.