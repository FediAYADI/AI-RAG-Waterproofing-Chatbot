"""
Chat endpoints for RAG-based Q&A
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.rag_engine import rag_engine

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    use_rag: bool = True


class ChatResponse(BaseModel):
    answer: str
    sources: list
    session_id: str
    used_rag: bool


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process user query using RAG
    """
    try:
        result = rag_engine.process_query(
            query=request.query,
            conversation_history=None,  # TODO: Implement conversation history
            use_rag=request.use_rag
        )
        
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            session_id=request.session_id or "default",
            used_rag=result["used_rag"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@router.get("/chat/sessions/{session_id}")
async def get_chat_history(session_id: str):
    """
    Retrieve chat history for a session
    """
    # TODO: Implement chat history retrieval with database
    return {"session_id": session_id, "messages": []}
