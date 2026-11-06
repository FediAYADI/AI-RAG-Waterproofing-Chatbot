# Architecture Documentation

## System Overview

The AI RAG Waterproofing Chatbot is a Python RAG pipeline used from the terminal through `backend/cli.py`. The pipeline is organized in layers so that a different front end (for example a web API for website integration) can be added later on top of `RAGEngine` without changing the core.

## Components

```
backend/
├── cli.py            # Terminal interface: chat, ask, ingest, stats
├── core/             # Core business logic
│   ├── config.py             # Configuration (config/config.yaml + config/.env)
│   ├── rag_engine.py         # RAG orchestration (query + ingestion)
│   └── document_processor.py # Text extraction and chunking
└── services/         # Service layer
    ├── vector_service.py     # ChromaDB operations
    ├── llm_service.py        # LLM interactions (OpenAI / Anthropic)
    └── embedding_service.py  # Text embeddings (OpenAI / HuggingFace)
```

## Data Flow

1. **Document Ingestion** (`python backend/cli.py ingest`)
   - Files → `DocumentProcessor` (text extraction) → chunking → `EmbeddingService` → `VectorService` (ChromaDB)

2. **Query Processing** (`python backend/cli.py chat`)
   - User question → query embedding → vector search (top-k) → context formatting → `LLMService` → answer + sources printed in the terminal

## Technology Stack

- **Vector DB**: ChromaDB (persistent, `data/vector_store/`)
- **Embeddings**: OpenAI `text-embedding-ada-002` (default) or HuggingFace SentenceTransformers
- **LLM**: OpenAI GPT-4 (default) or Anthropic Claude
- **Document parsing**: pypdf, python-docx, pandas/openpyxl

## Security Considerations

- API keys are read from `config/.env` (gitignored), never from source code
- Input files are parsed locally; only text chunks are sent to the embedding/LLM providers
