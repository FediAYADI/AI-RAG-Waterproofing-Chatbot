"""
AI RAG Waterproofing Chatbot - Main Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from core.config import settings
from api.routes import chat, documents, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Starting AI RAG Waterproofing Chatbot...")
    # Initialize vector database
    # Initialize LLM connections
    yield
    # Shutdown
    print("Shutting down AI RAG Waterproofing Chatbot...")


app = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    description=settings.app.description,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.server.cors.origins,
    allow_credentials=settings.server.cors.allow_credentials,
    allow_methods=settings.server.cors.allow_methods,
    allow_headers=settings.server.cors.allow_headers,
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI RAG Waterproofing Chatbot API",
        "version": settings.app.version,
        "status": "running"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.reload,
        workers=settings.server.workers
    )
