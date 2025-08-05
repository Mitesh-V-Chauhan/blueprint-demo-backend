import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    
    # Redis (for context management and caching)
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Gemini API Keys
    GEMINI_API_KEY_1: str = Field(..., env="GEMINI_API_KEY_1")
    GEMINI_API_KEY_2: Optional[str] = Field(default=None, env="GEMINI_API_KEY_2")
    GEMINI_API_KEY_3: Optional[str] = Field(default=None, env="GEMINI_API_KEY_3")
    GEMINI_API_KEY_4: Optional[str] = Field(default=None, env="GEMINI_API_KEY_4")
    GEMINI_API_KEY_5: Optional[str] = Field(default=None, env="GEMINI_API_KEY_5")
    GEMINI_API_KEY_6: Optional[str] = Field(default=None, env="GEMINI_API_KEY_6")
    
    # Pinecone Vector Database
    PINECONE_API_KEY: str = Field(..., env="PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: str = Field(default="us-east-1", env="PINECONE_ENVIRONMENT")
    
    # Firebase (for auth verification)
    FIREBASE_SERVICE_ACCOUNT_PATH: Optional[str] = Field(default=None, env="FIREBASE_SERVICE_ACCOUNT_PATH")
    
    # Application
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        env="ALLOWED_ORIGINS"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1"],
        env="ALLOWED_HOSTS"
    )
    
    # File uploads
    MAX_FILE_SIZE: int = Field(default=50 * 1024 * 1024, env="MAX_FILE_SIZE")  # 50MB
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    
    # Agent configuration
    MAX_AGENT_RETRIES: int = Field(default=3, env="MAX_AGENT_RETRIES")
    AGENT_TIMEOUT: int = Field(default=300, env="AGENT_TIMEOUT")  # 5 minutes
    
    # RAG configuration
    VECTOR_DIMENSION: int = Field(default=768, env="VECTOR_DIMENSION")  # Gemini embedding dimension
    CHUNK_SIZE: int = Field(default=1000, env="CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(default=200, env="CHUNK_OVERLAP")
    
    @property
    def gemini_api_keys(self) -> List[str]:
        """Get all available Gemini API keys"""
        keys = []
        for i in range(1, 7):
            key = getattr(self, f"GEMINI_API_KEY_{i}", None)
            if key:
                keys.append(key)
        return keys
    
    class Config:
        env_file = ".env"
        case_sensitive = True