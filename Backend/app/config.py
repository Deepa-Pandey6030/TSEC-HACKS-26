"""
Configuration settings for NOLAN Backend
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application
    app_name: str = "NOLAN Creative AI Assistant"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # xAI Grok/Groq API Configuration
    xai_api_key: str = ""
    grok_model: str = "llama-3.3-70b-versatile"  # Groq model
    
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "nolan_db"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    
    # Neo4j Configuration (for Knowledge Graph)
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    
    # AI Model Configuration
    max_context_tokens: int = 32000  # Groq context window
    max_output_tokens: int = 8000
    default_temperature: float = 0.7
    
    # Reasoning Engine Configuration
    min_confidence_threshold: float = 0.6
    max_suggestions_per_cycle: int = 5
    preference_learning_enabled: bool = True
    
    # Rate Limiting
    max_requests_per_minute: int = 60
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Create settings instance
settings = Settings()

# Debug: Print API key status (first/last 4 chars only)
if settings.xai_api_key:
    key_preview = f"{settings.xai_api_key[:4]}...{settings.xai_api_key[-4:]}" if len(settings.xai_api_key) > 8 else "***"
    print(f"✅ API Key loaded: {key_preview}")
else:
    print("❌ WARNING: No API key found in environment!")
    print(f"   Looking for XAI_API_KEY in: {os.path.abspath('.env')}")

