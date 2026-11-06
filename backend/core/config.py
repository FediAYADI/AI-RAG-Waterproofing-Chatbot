"""
Configuration management using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from typing import List
import yaml
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "config", ".env"))


class AppConfig(BaseSettings):
    name: str = "AI RAG Waterproofing Chatbot"
    version: str = "1.0.0"
    description: str = "RAG-based chatbot for waterproofing consultation"
    debug: bool = False


class CORSConfig(BaseSettings):
    enabled: bool = True
    origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    allow_credentials: bool = True
    allow_methods: List[str] = ["*"]
    allow_headers: List[str] = ["*"]


class ServerConfig(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    reload: bool = False
    cors: CORSConfig = Field(default_factory=CORSConfig)


class VectorDBConfig(BaseSettings):
    type: str = "chromadb"
    path: str = "./data/vector_store"
    collection_name: str = "waterproofing_docs"
    dimension: int = 384


class LLMConfig(BaseSettings):
    provider: str = "local"
    model: str = "microsoft/phi-2"
    temperature: float = 0.7
    max_tokens: int = 500
    streaming: bool = False


class RAGConfig(BaseSettings):
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_retrieval: int = 5
    retrieval_strategy: str = "similarity"
    rerank: bool = False
    rerank_model: str = "cross-encoder"


class EmbeddingConfig(BaseSettings):
    model: str = "sentence-transformers/all-MiniLM-L6-v2"
    provider: str = "huggingface"
    batch_size: int = 100
    dimension: int = 384


class ProcessingConfig(BaseSettings):
    max_file_size: int = 10485760
    allowed_extensions: List[str] = Field(default_factory=lambda: [".pdf", ".txt", ".docx", ".md", ".csv", ".xls", ".xlsx"])
    clean_text: bool = True
    remove_stopwords: bool = False


class Settings(BaseSettings):
    app: AppConfig = Field(default_factory=AppConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    vector_db: VectorDBConfig = Field(default_factory=VectorDBConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)

    model_config = ConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "config", ".env"),
        env_file_encoding="utf-8",
        extra="allow"
    )


def load_config_from_yaml(config_path: str = None) -> Settings:
    """Load configuration from YAML file"""
    if config_path is None:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "config", "config.yaml")
    
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)
        return Settings(**config_data)
    return Settings()


settings = load_config_from_yaml()
