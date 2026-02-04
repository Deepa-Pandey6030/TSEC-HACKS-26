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
    xai_api_key_2: str = ""  # Fallback key 2
    xai_api_key_3: str = ""  # Fallback key 3
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
api_keys = [settings.xai_api_key, settings.xai_api_key_2, settings.xai_api_key_3]
active_keys = [k for k in api_keys if k]

if active_keys:
    for idx, key in enumerate(active_keys, 1):
        key_preview = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "***"
        print(f"✅ API Key {idx} loaded: {key_preview}")
    print(f"📊 Total API keys configured: {len(active_keys)}")
else:
    print("❌ WARNING: No API key found in environment!")
    print(f"   Looking for XAI_API_KEY, XAI_API_KEY_2, XAI_API_KEY_3 in: {os.path.abspath('.env')}")

