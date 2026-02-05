"""
MongoDB Connection Manager

Provides a centralized, singleton-like connection to MongoDB.
All services should use get_database() to access the database.

Design Decision:
- We use a module-level client to avoid connection overhead per request.
- The client is initialized lazily on first access.
- Connection pooling is handled automatically by pymongo.
"""

from pymongo import MongoClient
from pymongo.database import Database
from typing import Optional
import logging
import os

logger = logging.getLogger(__name__)

# Module-level client (singleton pattern)
_client: Optional[MongoClient] = None
_database: Optional[Database] = None


def get_client() -> MongoClient:
    """
    Get or create the MongoDB client.
    Uses connection pooling internally.
    """
    global _client
    
    if _client is None:
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        
        try:
            _client = MongoClient(
                mongodb_url,
                maxPoolSize=50,          # Connection pool size
                minPoolSize=10,          # Minimum connections to maintain
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000,
            )
            # Verify connection works
            _client.admin.command('ping')
            logger.info(f"✅ MongoDB connected: {mongodb_url}")
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            raise
    
    return _client


def get_database() -> Database:
    """
    Get the application database.
    This is the primary method services should use.
    """
    global _database
    
    if _database is None:
        client = get_client()
        db_name = os.getenv("MONGODB_DB_NAME", "nolan_db")
        _database = client[db_name]
        logger.info(f"📚 Using database: {db_name}")
    
    return _database


def close_connection():
    """
    Close the MongoDB connection.
    Call this during application shutdown.
    """
    global _client, _database
    
    if _client is not None:
        _client.close()
        _client = None
        _database = None
        logger.info("🔌 MongoDB connection closed")


# Health check utility
def check_connection() -> bool:
    """
    Verify MongoDB is accessible.
    Returns True if connected, False otherwise.
    """
    try:
        client = get_client()
        client.admin.command('ping')
        return True
    except Exception as e:
        logger.error(f"MongoDB health check failed: {e}")
        return False
