"""
Vector Database Service - Handles vector storage and retrieval
"""

from typing import List, Dict, Optional
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from chromadb.config import Settings
from core.config import settings


class VectorService:
    """Service for vector database operations using ChromaDB"""

    def __init__(self):
        self.client = None
        self.collection = None
        self.collection_name = settings.vector_db.collection_name
        self.dimension = settings.vector_db.dimension
        self._initialize()

    def _initialize(self):
        """Initialize ChromaDB client and collection"""
        try:
            if settings.vector_db.type == "chromadb":
                self.client = chromadb.PersistentClient(
                    path=settings.vector_db.path,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
                
                # Get or create collection
                self.collection = self.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
                
                print(f"Connected to ChromaDB at {settings.vector_db.path}")
                print(f"Collection: {self.collection_name}")
                print(f"Document count: {self.collection.count()}")
            else:
                raise ValueError(f"Unsupported vector DB type: {settings.vector_db.type}")
        except Exception as e:
            raise Exception(f"Failed to initialize vector database: {str(e)}")

    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ) -> bool:
        """
        Add documents to the vector store
        
        Args:
            texts: List of text chunks
            embeddings: List of embedding vectors
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of document IDs
            
        Returns:
            True if successful
        """
        try:
            if ids is None:
                ids = [f"doc_{i}_{hash(text)}" for i, text in enumerate(texts)]
            
            if metadatas is None:
                metadatas = [{} for _ in texts]
            
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"Added {len(texts)} documents to vector store")
            return True
        except Exception as e:
            print(f"Error adding documents: {str(e)}")
            return False

    def search(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict] = None,
        where_document: Optional[Dict] = None
    ) -> Dict:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where: Metadata filter
            where_document: Document content filter
            
        Returns:
            Dictionary with search results
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where,
                where_document=where_document
            )
            return results
        except Exception as e:
            print(f"Error searching documents: {str(e)}")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    def search_by_text(
        self,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> Dict:
        """
        Search using text query (will be embedded automatically)
        
        Args:
            query_text: Query text
            n_results: Number of results
            where: Metadata filter
            
        Returns:
            Dictionary with search results
        """
        from embedding_service import embedding_service
        
        try:
            query_embedding = embedding_service.embed_text(query_text)
            return self.search(query_embedding, n_results, where)
        except Exception as e:
            print(f"Error searching by text: {str(e)}")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    def delete_documents(self, ids: List[str]) -> bool:
        """
        Delete documents by IDs
        
        Args:
            ids: List of document IDs to delete
            
        Returns:
            True if successful
        """
        try:
            self.collection.delete(ids=ids)
            print(f"Deleted {len(ids)} documents")
            return True
        except Exception as e:
            print(f"Error deleting documents: {str(e)}")
            return False

    def delete_by_metadata(self, where: Dict) -> bool:
        """
        Delete documents by metadata filter
        
        Args:
            where: Metadata filter dictionary
            
        Returns:
            True if successful
        """
        try:
            # First get the IDs
            results = self.collection.get(where=where)
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                print(f"Deleted {len(results['ids'])} documents matching filter")
                return True
            return False
        except Exception as e:
            print(f"Error deleting by metadata: {str(e)}")
            return False

    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the collection
        
        Returns:
            Dictionary with collection stats
        """
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "dimension": self.dimension
            }
        except Exception as e:
            print(f"Error getting stats: {str(e)}")
            return {}

    def clear_collection(self) -> bool:
        """
        Clear all documents from the collection
        
        Returns:
            True if successful
        """
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"Cleared collection {self.collection_name}")
            return True
        except Exception as e:
            print(f"Error clearing collection: {str(e)}")
            return False


# Singleton instance
vector_service = VectorService()
