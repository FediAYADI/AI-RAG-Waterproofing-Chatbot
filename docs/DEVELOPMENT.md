# Development Guide

## Setup

1. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp config/.env.example config/.env
   # Edit config/.env with your API keys
   ```

4. **Build the vector store and start chatting**
   ```bash
   python backend/cli.py ingest
   python backend/cli.py
   ```

## Development Workflow

1. **RAG improvements**: `backend/core/rag_engine.py`
2. **Document processing**: `backend/core/document_processor.py`
3. **Services (embeddings, LLM, vector DB)**: `backend/services/`
4. **Terminal interface**: `backend/cli.py`

### Code Style

Follow PEP 8 and use Black for formatting.

### Testing

```bash
pytest
pytest --cov=backend

# Manual end-to-end check from the terminal
python backend/cli.py ask "Comment appliquer SikaTop-141 ?" --show-chunks
```

## Common Tasks

### Adding a New Document Type

1. Add a parser in `backend/core/document_processor.py`
2. Update allowed extensions in `config/config.yaml`

### Adding a New LLM Provider

1. Extend `backend/services/llm_service.py`
2. Update the `llm` section of `config/config.yaml`

### Updating the Vector Database

1. Modify `backend/services/vector_service.py`
2. Update the `vector_db` section of `config/config.yaml`
3. Re-ingest documents (`rm -rf data/vector_store && python backend/cli.py ingest -y`)

## Troubleshooting

1. **`Failed to start the RAG pipeline: The api_key client option must be set`**: set `OPENAI_API_KEY` in `config/.env`
2. **"the vector store is empty" warning**: run `python backend/cli.py ingest`
3. **LLM rate limits**: reduce `rag.top_k_retrieval` or retry later
4. **Memory issues**: reduce chunk size or batch size in `config/config.yaml`
