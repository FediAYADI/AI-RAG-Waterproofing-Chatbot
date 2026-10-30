"""
LLM Service - Handles response generation using various LLM providers
"""

from typing import List, Dict, Optional
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
import anthropic
from core.config import settings


class LLMService:
    """Service for LLM-based text generation"""

    def __init__(self):
        self.provider = settings.llm.provider
        self.model = settings.llm.model
        self.temperature = settings.llm.temperature
        self.max_tokens = settings.llm.max_tokens
        self.streaming = settings.llm.streaming
        
        if self.provider == "openai":
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        elif self.provider == "anthropic":
            self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    def generate_response(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """
        Generate a response based on query and retrieved context
        
        Args:
            query: User's question
            context: Retrieved context from vector database
            conversation_history: Optional conversation history
            
        Returns:
            Generated response text
        """
        if self.provider == "openai":
            return self._generate_openai(query, context, conversation_history)
        elif self.provider == "anthropic":
            return self._generate_anthropic(query, context, conversation_history)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def _generate_openai(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """Generate response using OpenAI"""
        try:
            system_prompt = """You are a waterproofing expert assistant. Use the provided context to answer questions accurately and professionally. If the context doesn't contain enough information, say so clearly. Be helpful and specific."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ]
            
            # Add conversation history if provided
            if conversation_history:
                messages.insert(1, *conversation_history)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI generation failed: {str(e)}")
    
    def _generate_anthropic(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """Generate response using Anthropic Claude"""
        try:
            system_prompt = """You are a waterproofing expert assistant. Use the provided context to answer questions accurately and professionally. If the context doesn't contain enough information, say so clearly. Be helpful and specific."""
            
            user_message = f"Context:\n{context}\n\nQuestion: {query}"
            
            messages = [{"role": "user", "content": user_message}]
            
            if conversation_history:
                messages = conversation_history + messages
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=messages
            )
            
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Anthropic generation failed: {str(e)}")
    
    def generate_response_stream(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict]] = None
    ):
        """
        Generate a streaming response
        
        Args:
            query: User's question
            context: Retrieved context
            conversation_history: Optional conversation history
            
        Yields:
            Response chunks
        """
        if self.provider == "openai":
            yield from self._generate_openai_stream(query, context, conversation_history)
        else:
            # Anthropic streaming not implemented for simplicity
            yield self.generate_response(query, context, conversation_history)
    
    def _generate_openai_stream(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict]] = None
    ):
        """Generate streaming response using OpenAI"""
        try:
            system_prompt = """You are a waterproofing expert assistant. Use the provided context to answer questions accurately and professionally. If the context doesn't contain enough information, say so clearly. Be helpful and specific."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ]
            
            if conversation_history:
                messages.insert(1, *conversation_history)
            
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise Exception(f"OpenAI streaming failed: {str(e)}")


# Singleton instance
llm_service = LLMService()
