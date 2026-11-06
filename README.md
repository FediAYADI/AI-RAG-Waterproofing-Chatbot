# AI RAG Waterproofing Chatbot

A RAG (Retrieval-Augmented Generation) chatbot specialized in waterproofing and construction materials. It searches a knowledge base of supplier documents (Sika, GEKO, Isomat, Derbigum, Afrochim technical sheets, brochures and product lists) and generates answers grounded in the retrieved content.

During the current development phase the chatbot is used **exclusively from the terminal**. Website integration will be added in a later phase.

## How it works

1. **Ingestion** – `DocumentProcessor` extracts text from PDF, DOCX, TXT, MD, CSV and Excel files.
2. **Chunking** – text is split into overlapping chunks (`rag.chunk_size` / `rag.chunk_overlap`).
3. **Embedding** – `EmbeddingService` embeds chunks (OpenAI or HuggingFace).
4. **Vector storage** – `VectorService` stores chunks in a persistent ChromaDB collection (`data/vector_store/`).
5. **Retrieval + generation** – `RAGEngine` retrieves the top-k chunks for a question and `LLMService` (OpenAI or Anthropic) answers using them as context.

## Project Structure

```
.
├── backend/
│   ├── cli.py                    # Terminal interface (entry point)
│   ├── core/
│   │   ├── config.py             # Settings loaded from config/config.yaml + config/.env
│   │   ├── document_processor.py # Text extraction and chunking
│   │   └── rag_engine.py         # RAG pipeline orchestration
│   └── services/
│       ├── embedding_service.py  # Text embeddings
│       ├── llm_service.py        # LLM response generation + system prompt
│       └── vector_service.py     # ChromaDB storage and search
├── config/
│   ├── config.yaml               # Application settings
│   └── .env.example              # API key template (copy to config/.env)
├── data/
│   ├── raw/                      # Raw source documents
│   ├── processed/                # Cleaned documents used for ingestion
│   └── vector_store/             # ChromaDB storage (generated, gitignored)
├── docs/                         # Architecture and development docs
├── scripts/                      # Standalone batch-ingestion scripts
└── requirements.txt
```

## Setup

Requires Python 3.10+.

```bash
python -m venv venv
source venv/bin/activate          # Windows (PowerShell): .\venv\Scripts\Activate.ps1
pip install -r requirements.txt

cp config/.env.example config/.env  # then set OPENAI_API_KEY (or ANTHROPIC_API_KEY)
```

Providers and models are configured in `config/config.yaml` (`embedding` and `llm` sections).

## Usage

All commands are run from the project root.

### 1. Ingest documents (first run, or after adding documents)

```bash
python backend/cli.py ingest              # ingests everything in data/processed
python backend/cli.py ingest path/to/file.pdf
python backend/cli.py ingest -y           # skip the confirmation prompt
python backend/cli.py stats               # number of chunks in the vector store
```

Re-ingesting the same files adds duplicate chunks; delete `data/vector_store/` to start from a clean store.

### 2. Chat

```bash
python backend/cli.py                     # interactive chat (same as `chat`)
python backend/cli.py chat --show-chunks  # also print the retrieved chunk text
python backend/cli.py chat --no-sources   # answers only
python backend/cli.py ask "Comment appliquer SikaTop-141 ?"   # one question, then exit
```

Example session:

```
You: Quelle est la consommation de Sikalastic-560 ?

Assistant: ...

Sources:
  [1] data/processed/sika tunisie/Fiche Technique/Sikalastic-560.PDF, chunk 2 (relevance: 0.87)
  ...

You: exit
Goodbye!
```

In-chat commands:

| Command | Effect |
|---|---|
| `/help` | List commands |
| `/sources on\|off` | Show or hide retrieved sources |
| `/chunks on\|off` | Show or hide retrieved chunk text |
| `/rag on\|off` | Toggle retrieval (off = plain LLM answer) |
| `/stats` | Vector store statistics |
| `exit`, `quit`, `Ctrl+C`, `Ctrl+D` | Leave the chatbot |

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Development Guide](docs/DEVELOPMENT.md)

## License

MIT License
