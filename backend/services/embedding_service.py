"""
Embedding Service - Handles text embeddings using various providers
"""

from typing import List
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from sentence_transformers import SentenceTransformer
from core.config import settings


class EmbeddingService:
    """Service for generating text embeddings"""

    def __init__(self):
        self.provider = settings.embedding.provider
        self.model = settings.embedding.model
        self.dimension = settings.embedding.dimension
        
        if self.provider == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif self.provider == "huggingface":
            self.model = SentenceTransformer(self.model)
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            List of embedding values
        """
        if self.provider == "openai":
            return self._embed_openai(text)
        elif self.provider == "huggingface":
            return self._embed_huggingface(text)
        else:
            raise ValueError(f"Unsupported embedding provider: {self.provider}")
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing)
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        if self.provider == "openai":
            return self._embed_openai_batch(texts)
        elif self.provider == "huggingface":
            return self._embed_huggingface_batch(texts)
        else:
            raise ValueError(f"Unsupported embedding provider: {self.provider}")
    
    def _embed_openai(self, text: str) -> List[float]:
        """Generate embedding using OpenAI"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"OpenAI embedding failed: {str(e)}")
    
    def _embed_openai_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts using OpenAI"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            raise Exception(f"OpenAI batch embedding failed: {str(e)}")
    
    def _embed_huggingface(self, text: str) -> List[float]:
        """Generate embedding using HuggingFace SentenceTransformers"""
        try:
            embedding = self.model.encode(text)
            return embedding.tolist()
        except Exception as e:
            raise Exception(f"HuggingFace embedding failed: {str(e)}")
    
    def _embed_huggingface_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts using HuggingFace"""
        try:
            embeddings = self.model.encode(texts)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            raise Exception(f"HuggingFace batch embedding failed: {str(e)}")


# Singleton instance
embedding_service = EmbeddingService()
