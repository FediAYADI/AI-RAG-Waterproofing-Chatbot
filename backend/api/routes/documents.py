"""
Document management endpoints
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.rag_engine import rag_engine
from core.config import settings

router = APIRouter()


class DocumentResponse(BaseModel):
    filename: str
    status: str
    chunks: int
    message: str


class DocumentListResponse(BaseModel):
    documents: List[dict]
    total_count: int


@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document for the RAG system
    """
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        allowed_extensions = settings.processing.allowed_extensions
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Validate file size
        content = await file.read()
        file_size = len(content)
        max_size = settings.processing.max_file_size
        
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {max_size / (1024*1024):.2f}MB"
            )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Process document through RAG engine
            result = rag_engine.ingest_document(
                file_path=temp_file_path,
                metadata={"filename": file.filename}
            )
            
            if result["success"]:
                return DocumentResponse(
                    filename=file.filename,
                    status="processed",
                    chunks=result["chunks_processed"],
                    message=result["message"]
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=result["message"]
                )
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """
    List all processed documents (from vector store stats)
    """
    try:
        from backend.services.vector_service import vector_service
        stats = vector_service.get_collection_stats()
        
        return DocumentListResponse(
            documents=[stats],
            total_count=stats.get("document_count", 0)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing documents: {str(e)}"
        )


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document from the vector store
    """
    try:
        from backend.services.vector_service import vector_service
        success = vector_service.delete_documents([document_id])
        
        if success:
            return {"message": f"Document {document_id} deleted"}
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete document"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting document: {str(e)}"
        )


@router.post("/documents/process-directory")
async def process_directory(directory_path: str, metadata: Optional[dict] = None):
    """
    Process all documents in a directory
    """
    try:
        if not os.path.exists(directory_path):
            raise HTTPException(
                status_code=404,
                detail=f"Directory not found: {directory_path}"
            )
        
        result = rag_engine.ingest_directory(directory_path, metadata)
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing directory: {str(e)}"
        )
