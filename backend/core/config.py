"""
Configuration management using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import yaml
import os


class AppConfig(BaseSettings):
    name: str = "AI RAG Waterproofing Chatbot"
    version: str = "1.0.0"
    description: str = "RAG-based chatbot for waterproofing consultation"
    debug: bool = False


class ServerConfig(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    reload: bool = False


class CORSConfig(BaseSettings):
    enabled: bool = True
    origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    allow_credentials: bool = True
    allow_methods: List[str] = ["*"]
    allow_headers: List[str] = ["*"]


class VectorDBConfig(BaseSettings):
    type: str = "chromadb"
    path: str = "./data/vector_store"
    collection_name: str = "waterproofing_docs"
    dimension: int = 1536


class LLMConfig(BaseSettings):
    provider: str = "openai"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    streaming: bool = True


class RAGConfig(BaseSettings):
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_retrieval: int = 5
    retrieval_strategy: str = "similarity"


class Settings(BaseSettings):
    app: AppConfig = Field(default_factory=AppConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    cors: CORSConfig = Field(default_factory=CORSConfig)
    vector_db: VectorDBConfig = Field(default_factory=VectorDBConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)

    class Config:
        env_file = "../config/.env"
        env_file_encoding = "utf-8"


def load_config_from_yaml(config_path: str = "../config/config.yaml") -> Settings:
    """Load configuration from YAML file"""
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)
        return Settings(**config_data)
    return Settings()


settings = load_config_from_yaml()
