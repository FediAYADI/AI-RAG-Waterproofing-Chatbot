# Development Guide

## Setup Instructions

### Backend Setup

1. **Create virtual environment**
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
   # Edit config/.env with your API keys and settings
   ```

4. **Run the backend**
   ```bash
   cd backend
   python main.py
   ```

### Widget Development

The widget is a standalone JavaScript file that can be tested locally:

1. **Start the backend server**
   ```bash
   python backend/main.py
   ```

2. **Open the integration example**
   ```bash
   # Open widget/integration-example.html in your browser
   # Or use a simple HTTP server:
   python -m http.server 8080 --directory widget
   # Then visit http://localhost:8080/integration-example.html
   ```

3. **Make changes to `widget/chat-widget.js`**
   - Refresh the browser to see changes
   - Check browser console for errors

## Development Workflow

### Backend Development

1. **Adding new API endpoints**: Add routes in `backend/api/routes/`
2. **Implementing services**: Add services in `backend/services/`
3. **RAG improvements**: Modify `backend/core/rag_engine.py`
4. **Document processing**: Update `backend/core/document_processor.py`

### Widget Development

1. **Modifying widget behavior**: Edit `widget/chat-widget.js`
2. **Styling changes**: Modify the CSS in the `injectStyles()` method
3. **Adding configuration options**: Add to the config object in the constructor
4. **Testing**: Use `widget/integration-example.html` for testing

### Code Style

- **Backend**: Follow PEP 8, use Black for formatting
- **Widget**: Follow modern JavaScript (ES6+) conventions

### Testing

```bash
# Run backend tests
pytest

# Run with coverage
pytest --cov=backend

# Test widget manually using integration-example.html
```

## Common Tasks

### Adding a New Document Type

1. Add parser in `backend/core/document_processor.py`
2. Update allowed extensions in `config/config.yaml`
3. Add tests in `tests/unit/test_document_processor.py`

### Adding a New LLM Provider

1. Create service in `backend/services/llm_service.py`
2. Update config in `config/config.yaml`
3. Add provider to `backend/core/config.py`

### Updating Vector Database

1. Modify `backend/services/vector_service.py`
2. Update config in `config/config.yaml`
3. Test with sample documents

### Customizing Widget Appearance

1. Edit the CSS in `widget/chat-widget.js` (in `injectStyles()` method)
2. Add new configuration options to the config object
3. Test with different websites to ensure compatibility

## Production Deployment

### Backend

1. **Use production database** (PostgreSQL instead of SQLite)
2. **Set environment variables** for sensitive data
3. **Configure CORS** to allow only your domains
4. **Use production-grade vector database** (Pinecone or hosted ChromaDB)
5. **Enable caching** with Redis
6. **Set up monitoring** and logging

### Widget

1. **Minify the JavaScript** for production
2. **Host on CDN** for better performance
3. **Use versioned filenames** (e.g., `chat-widget-v1.0.0.min.js`)
4. **Update apiUrl** to production API endpoint
5. **Test on different browsers and devices**

## Troubleshooting

### Common Issues

1. **Vector DB connection errors**: Check API keys and network connectivity
2. **LLM rate limits**: Implement retry logic and caching
3. **Memory issues**: Reduce chunk size or batch size in config
4. **Widget not loading**: Check script path and browser console errors
5. **CORS errors**: Verify CORS configuration in backend

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [Widget Integration Guide](INTEGRATION.md)
- [API Documentation](API.md)
