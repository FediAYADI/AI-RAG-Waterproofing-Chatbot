"""
LLM Service - Handles response generation using various LLM providers
"""

from typing import List, Dict, Optional
import os
import sys

# Add backend to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from openai import OpenAI
import anthropic
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
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
        elif self.provider == "local":
            # Load local HuggingFace model
            print(f"Loading local model: {self.model}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model)
            self.model_obj = AutoModelForCausalLM.from_pretrained(
                self.model,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
            if not torch.cuda.is_available():
                self.model_obj = self.model_obj.to('cpu')
            print("Local model loaded successfully")
    
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
        elif self.provider == "local":
            return self._generate_local(query, context, conversation_history)
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
    
    def _generate_local(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """Generate response using local HuggingFace model"""
        try:
            system_prompt = "You are a waterproofing expert assistant. Use the provided context to answer questions accurately and professionally."
            
            prompt = f"{system_prompt}\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer:"
            
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model_obj.generate(
                    **inputs,
                    max_new_tokens=self.max_tokens,
                    temperature=self.temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract just the answer part
            answer = response[len(prompt):].strip()
            
            return answer if answer else "I apologize, but I couldn't generate a response."
        except Exception as e:
            raise Exception(f"Local model generation failed: {str(e)}")
    
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
