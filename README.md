# AI RAG Waterproofing Chatbot

A professional RAG (Retrieval-Augmented Generation) based chatbot API with an embeddable widget for waterproofing consultation and information retrieval.

## Project Overview

This chatbot leverages advanced AI technologies to provide expert advice on waterproofing solutions, product recommendations, and technical guidance for construction and home improvement projects. The solution consists of:

- **Backend API**: FastAPI-based REST API with RAG capabilities
- **Embeddable Widget**: A JavaScript widget that can be easily integrated into any existing website

## Architecture

### Backend
- **FastAPI** - High-performance web framework
- **LangChain** - RAG framework for AI orchestration
- **Vector Database** - ChromaDB/Faiss for semantic search
- **LLM Integration** - OpenAI/Anthropic/Local models

### Widget
- **Vanilla JavaScript** - No framework dependencies
- **Easy Integration** - Single script tag
- **Customizable** - Configurable appearance and behavior
- **Responsive** - Mobile-friendly design

## Project Structure

```
.
├── backend/              # Backend application
│   ├── api/             # API endpoints and routes
│   ├── core/            # Core business logic
│   ├── models/          # Data models and schemas
│   ├── services/        # Service layer (RAG, vector search)
│   └── utils/           # Utility functions
├── widget/              # Embeddable chat widget
│   ├── chat-widget.js  # Main widget script
│   └── integration-example.html
├── data/                # Data management
│   ├── raw/            # Raw documents and data
│   ├── processed/      # Processed/cleaned data
│   └── vector_store/   # Vector database storage
├── config/             # Configuration files
├── docs/               # Documentation
├── tests/              # Test suites
│   ├── unit/          # Unit tests
│   └── integration/   # Integration tests
├── scripts/            # Utility scripts
└── logs/              # Application logs
```

## Quick Start

### Prerequisites
- Python 3.10+
- Vector database (ChromaDB/Faiss)

### Installation

1. Clone the repository
2. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables (see config/.env.example)
4. Run the backend:
   ```bash
   python backend/main.py
   ```

### Website Integration

To integrate the chatbot into your existing website:

1. Copy `widget/chat-widget.js` to your website
2. Add the script and initialization code to your HTML:

```html
<script src="chat-widget.js"></script>
<script>
    WaterproofingChatbot.init({
        apiUrl: 'http://localhost:8000/api/v1',
        position: 'bottom-right',
        primaryColor: '#007bff',
        title: 'Waterproofing Assistant'
    });
</script>
```

See [Integration Guide](docs/INTEGRATION.md) for detailed instructions.

## Configuration

See `config/config.yaml` for application settings.

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System architecture overview
- [API Documentation](docs/API.md) - API endpoints and usage
- [Integration Guide](docs/INTEGRATION.md) - Website integration instructions
- [Development Guide](docs/DEVELOPMENT.md) - Development setup and guidelines

## Contributing

Please read CONTRIBUTING.md for guidelines on contributing to this project.

## License

MIT License


activate and deactivate virtual environment:
```bash
# activate
.\venv\Scripts\Activate.ps1

# deactivate
deactivate
```


api key opoenai : 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
