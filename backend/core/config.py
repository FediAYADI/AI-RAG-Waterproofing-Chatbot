"""
Configuration management using Pydantic Settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List
from pathlib import Path
from dotenv import load_dotenv
import yaml
import os

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"

# Expose API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, ...) to os.getenv()
load_dotenv(CONFIG_DIR / ".env")


class AppConfig(BaseSettings):
    name: str = "AI RAG Waterproofing Chatbot"
    version: str = "1.0.0"
    description: str = "RAG-based chatbot for waterproofing consultation"
    debug: bool = False


class VectorDBConfig(BaseSettings):
    type: str = "chromadb"
    path: str = "./data/vector_store"
    collection_name: str = "waterproofing_docs"
    dimension: int = 1536


class EmbeddingConfig(BaseSettings):
    model: str = "text-embedding-ada-002"
    provider: str = "openai"
    batch_size: int = 100
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
    rerank: bool = False
    rerank_model: str = "cross-encoder"


class ProcessingConfig(BaseSettings):
    max_file_size: int = 10485760
    allowed_extensions: List[str] = [".pdf", ".txt", ".docx", ".md", ".csv", ".xls", ".xlsx"]
    clean_text: bool = True
    remove_stopwords: bool = False


class Settings(BaseSettings):
    app: AppConfig = Field(default_factory=AppConfig)
    vector_db: VectorDBConfig = Field(default_factory=VectorDBConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)

    model_config = SettingsConfigDict(
        env_file=str(CONFIG_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


def load_config_from_yaml(config_path: str = str(CONFIG_DIR / "config.yaml")) -> Settings:
    """Load configuration from YAML file"""
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)
        settings = Settings(**config_data)
    else:
        settings = Settings()

    # Relative vector store paths are resolved from the project root so the
    # same store is used regardless of the current working directory.
    if not os.path.isabs(settings.vector_db.path):
        settings.vector_db.path = str((PROJECT_ROOT / settings.vector_db.path).resolve())
    return settings


settings = load_config_from_yaml()
