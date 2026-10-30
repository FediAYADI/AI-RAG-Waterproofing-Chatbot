"""
RAG Engine - Orchestrates the Retrieval-Augmented Generation pipeline
"""

from typing import List, Dict, Optional
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.embedding_service import embedding_service
from services.vector_service import vector_service
from services.llm_service import llm_service
from core.config import settings


class RAGEngine:
    """RAG Pipeline Engine"""

    def __init__(self):
        self.top_k = settings.rag.top_k_retrieval
        self.chunk_size = settings.rag.chunk_size
        self.chunk_overlap = settings.rag.chunk_overlap
    
    def process_query(
        self,
        query: str,
        conversation_history: Optional[List[Dict]] = None,
        use_rag: bool = True
    ) -> Dict:
        """
        Process a user query through the RAG pipeline
        
        Args:
            query: User's question
            conversation_history: Optional conversation history
            use_rag: Whether to use RAG retrieval
            
        Returns:
            Dictionary with answer and sources
        """
        if not use_rag:
            # Direct LLM response without RAG
            response = llm_service.generate_response(
                query=query,
                context="",
                conversation_history=conversation_history
            )
            return {
                "answer": response,
                "sources": [],
                "used_rag": False
            }
        
        # Step 1: Retrieve relevant documents
        search_results = vector_service.search_by_text(
            query_text=query,
            n_results=self.top_k
        )
        
        # Step 2: Format context from retrieved documents
        context = self._format_context(search_results)
        
        # Step 3: Generate response with context
        answer = llm_service.generate_response(
            query=query,
            context=context,
            conversation_history=conversation_history
        )
        
        # Step 4: Format sources
        sources = self._format_sources(search_results)
        
        return {
            "answer": answer,
            "sources": sources,
            "used_rag": True
        }
    
    def _format_context(self, search_results: Dict) -> str:
        """
        Format retrieved documents into context string
        
        Args:
            search_results: Results from vector search
            
        Returns:
            Formatted context string
        """
        documents = search_results.get("documents", [[]])
        metadatas = search_results.get("metadatas", [[]])
        distances = search_results.get("distances", [[]])
        
        if not documents or not documents[0]:
            return "No relevant documents found."
        
        context_parts = []
        for i, (doc, meta, dist) in enumerate(zip(documents[0], metadatas[0], distances[0])):
            source = meta.get("source", "Unknown") if meta else "Unknown"
            context_parts.append(f"[Source {i+1}: {source} (relevance: {1-dist:.2f})]\n{doc}")
        
        return "\n\n".join(context_parts)
    
    def _format_sources(self, search_results: Dict) -> List[Dict]:
        """
        Format sources from search results
        
        Args:
            search_results: Results from vector search
            
        Returns:
            List of source dictionaries
        """
        metadatas = search_results.get("metadatas", [[]])
        distances = search_results.get("distances", [[]])
        
        if not metadatas or not metadatas[0]:
            return []
        
        sources = []
        for meta, dist in zip(metadatas[0], distances[0]):
            source = {
                "source": meta.get("source", "Unknown") if meta else "Unknown",
                "page": meta.get("page", "N/A") if meta else "N/A",
                "relevance": round(1 - dist, 3)
            }
            sources.append(source)
        
        return sources
    
    def ingest_document(
        self,
        file_path: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Ingest a document into the RAG system
        
        Args:
            file_path: Path to the document
            metadata: Optional metadata to attach
            
        Returns:
            Dictionary with ingestion results
        """
        from document_processor import processor
        
        try:
            # Extract text
            text, chunks = processor.process_document(
                file_path,
                chunk_size=self.chunk_size,
                overlap=self.chunk_overlap
            )
            
            # Generate embeddings
            embeddings = embedding_service.embed_texts(chunks)
            
            # Prepare metadata for each chunk
            if metadata is None:
                metadata = {}
            
            chunk_metadata = []
            for i, chunk in enumerate(chunks):
                chunk_meta = metadata.copy()
                chunk_meta.update({
                    "chunk_index": i,
                    "source": file_path,
                    "total_chunks": len(chunks)
                })
                chunk_metadata.append(chunk_meta)
            
            # Add to vector store
            success = vector_service.add_documents(
                texts=chunks,
                embeddings=embeddings,
                metadatas=chunk_metadata
            )
            
            if success:
                return {
                    "success": True,
                    "file_path": file_path,
                    "chunks_processed": len(chunks),
                    "message": f"Successfully processed {len(chunks)} chunks"
                }
            else:
                return {
                    "success": False,
                    "file_path": file_path,
                    "message": "Failed to add documents to vector store"
                }
        
        except Exception as e:
            return {
                "success": False,
                "file_path": file_path,
                "message": f"Error processing document: {str(e)}"
            }
    
    def ingest_directory(
        self,
        directory_path: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Ingest all documents from a directory
        
        Args:
            directory_path: Path to the directory
            metadata: Optional metadata to attach to all documents
            
        Returns:
            Dictionary with ingestion results
        """
        import os
        from pathlib import Path
        
        results = {
            "total_files": 0,
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        supported_extensions = {'.pdf', '.txt', '.docx', '.md', '.csv', '.xls', '.xlsx'}
        
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_ext = Path(file_path).suffix.lower()
                
                if file_ext in supported_extensions:
                    results["total_files"] += 1
                    
                    result = self.ingest_document(file_path, metadata)
                    
                    if result["success"]:
                        results["successful"] += 1
                    else:
                        results["failed"] += 1
                        results["errors"].append({
                            "file": file_path,
                            "error": result["message"]
                        })
        
        return results


# Singleton instance
rag_engine = RAGEngine()
