# API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Endpoints

### Health Check

#### GET /health

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### Chat

#### POST /chat

Process a user query using RAG. This is the main endpoint used by the widget.

**Request Body:**
```json
{
  "query": "What is the best waterproofing for basements?",
  "session_id": "session-123",
  "use_rag": true
}
```

**Parameters:**
- `query` (string, required): The user's question
- `session_id` (string, optional): Session identifier for conversation context
- `use_rag` (boolean, optional): Whether to use RAG retrieval (default: true)

**Response:**
```json
{
  "answer": "Based on the documents, the best waterproofing method for basements is...",
  "sources": [
    {
      "document": "waterproofing-guide.pdf",
      "page": 15,
      "relevance": 0.95
    }
  ],
  "session_id": "session-123"
}
```

#### GET /chat/sessions/{session_id}

Retrieve chat history for a session.

**Parameters:**
- `session_id` (string, required): Session identifier

**Response:**
```json
{
  "session_id": "session-123",
  "messages": [
    {
      "role": "user",
      "content": "What is...",
      "timestamp": "2024-01-01T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "Based on...",
      "timestamp": "2024-01-01T10:00:05Z"
    }
  ]
}
```

### Documents (Admin)

#### POST /documents/upload

Upload and process a document for the RAG system. This is typically used by administrators to add knowledge base content.

**Request:** Multipart form data with file

**Parameters:**
- `file` (file, required): Document file (PDF, TXT, DOCX, MD)

**Response:**
```json
{
  "filename": "document.pdf",
  "status": "processed",
  "chunks": 150,
  "message": "Document successfully processed"
}
```

#### GET /documents

List all processed documents.

**Response:**
```json
{
  "documents": [
    {
      "id": "doc-1",
      "filename": "waterproofing-guide.pdf",
      "chunks": 150,
      "uploaded_at": "2024-01-01T10:00:00Z"
    }
  ]
}
```

#### DELETE /documents/{document_id}

Delete a document from the vector store.

**Parameters:**
- `document_id` (string, required): Document identifier

**Response:**
```json
{
  "message": "Document doc-1 deleted"
}
```

## Error Responses

All endpoints may return error responses:

```json
{
  "detail": "Error message here"
}
```

Common HTTP status codes:
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required (if implemented)
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## CORS Configuration

The API supports CORS for cross-origin requests from the widget. Configure allowed origins in `config/config.yaml`:

```yaml
server:
  cors:
    origins:
      - "https://your-website.com"
      - "https://www.your-website.com"
```

## Rate Limiting

Consider implementing rate limiting to prevent abuse:
- Per IP address
- Per session
- Global limits

## Authentication (Optional)

For document management endpoints, consider adding authentication:
- API key authentication
- JWT tokens
- OAuth integration

## Widget Integration

The widget automatically calls the `/chat` endpoint. Ensure:
1. CORS is configured for your widget's domain
2. The API is accessible from the widget's origin
3. Response times are optimized for real-time chat

See [Integration Guide](INTEGRATION.md) for widget setup instructions.
