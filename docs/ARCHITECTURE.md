# Architecture Documentation

## System Overview

The AI RAG Waterproofing Chatbot is a backend API service with an embeddable JavaScript widget. The backend provides RAG-based conversational AI capabilities through RESTful APIs, while the widget allows easy integration into any existing website without framework dependencies.

## Components

### Backend Architecture

```
backend/
├── api/              # API Layer
│   ├── routes/       # Route definitions
│   └── middleware/   # CORS, auth, logging
├── core/             # Core Business Logic
│   ├── config.py     # Configuration management
│   ├── rag_engine.py # RAG orchestration
│   └── document_processor.py
├── models/           # Data Models
│   ├── schemas.py    # Pydantic schemas
│   └── database.py   # SQLAlchemy models
├── services/         # Service Layer
│   ├── vector_service.py    # Vector DB operations
│   ├── llm_service.py       # LLM interactions
│   └── embedding_service.py # Text embeddings
└── utils/            # Utilities
    ├── text_processing.py
    └── logger.py
```

### Widget Architecture

```
widget/
├── chat-widget.js            # Main widget script (vanilla JS)
└── integration-example.html  # Example integration
```

The widget is designed to be:
- **Framework-agnostic**: Works with any website (React, Vue, Angular, vanilla HTML, etc.)
- **Self-contained**: Single script file with embedded styles
- **Customizable**: Configurable via initialization options
- **Lightweight**: No external dependencies

### Data Flow

1. **Document Ingestion**
   - Admin uploads documents via API → Document Processor → Text Extraction → Chunking → Embedding → Vector Store

2. **Query Processing (via Widget)**
   - User types in widget → API → Query Embedding → Vector Search → Context Retrieval → LLM Generation → Response → Widget Display

3. **Conversation Management**
   - Messages stored in database → Session persistence → Context window management

## Technology Stack

### Backend
- **Framework**: FastAPI
- **RAG**: LangChain
- **Vector DB**: ChromaDB (primary), with support for Faiss and Pinecone
- **LLM**: OpenAI GPT-4 (primary), with Anthropic Claude support
- **Database**: SQLite (development), PostgreSQL (production)
- **Async**: asyncio, uvicorn

### Widget
- **Language**: Vanilla JavaScript (ES6+)
- **Styling**: Embedded CSS
- **HTTP Client**: Fetch API
- **No Dependencies**: Self-contained script

## Deployment Architecture

### Development
- Local development with hot reload
- SQLite database
- ChromaDB in-memory or persistent
- Widget served from local file or CDN

### Production
- Containerized deployment (Docker)
- PostgreSQL database
- Redis for caching
- Load balancer (Nginx)
- Vector DB: Pinecone or hosted ChromaDB
- Widget hosted on CDN for performance

## Integration Points

### Website Integration
The widget integrates into existing websites via:
1. Script tag inclusion
2. Initialization with configuration
3. REST API communication with backend
4. No backend changes required on the host website

### API Endpoints
- `POST /api/v1/chat` - Chat queries from widget
- `GET /api/v1/chat/sessions/{id}` - Chat history
- `POST /api/v1/documents/upload` - Document ingestion (admin)
- `GET /api/v1/documents` - List documents (admin)
- `DELETE /api/v1/documents/{id}` - Delete documents (admin)

## Security Considerations

- API key management through environment variables
- CORS configuration for widget API access
- Input validation and sanitization
- Rate limiting on API endpoints
- Secure file upload handling for document ingestion
- Database encryption at rest
- Widget domain whitelisting (optional)

## Scalability

- Horizontal scaling through load balancer
- Vector database sharding
- Caching layer (Redis)
- Asynchronous processing
- CDN hosting for widget script
- Session management with Redis
