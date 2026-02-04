"""
MongoDB User Database Operations
"""
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from typing import Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MongoUserDB:
    def __init__(self, mongodb_url: str, db_name: str):
        """Initialize MongoDB connection."""
        try:
            self.client = MongoClient(mongodb_url)
            self.db = self.client[db_name]
            self.users_collection = self.db["users"]
            
            # Create unique index on email
            self.users_collection.create_index("email", unique=True)
            print(f"✅ Database connected: {db_name}")
            logger.info("✅ MongoDB User DB Connected")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            logger.error(f"❌ MongoDB Connection Failed: {e}")
            raise

    def create_user(self, email: str, name: str, password: str) -> dict:
        """Create a new user."""
        user_doc = {
            "email": email,
            "name": name,
            "password": password,  # Plain password (for hackathon only!)
            "created_at": datetime.utcnow(),
        }
        try:
            result = self.users_collection.insert_one(user_doc)
            user_doc["id"] = str(result.inserted_id)
            return user_doc
        except DuplicateKeyError:
            raise ValueError(f"User with email {email} already exists")

    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email."""
        user = self.users_collection.find_one({"email": email})
        if user:
            user["id"] = str(user["_id"])
            return user
        return None

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID."""
        try:
            user = self.users_collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user["id"] = str(user["_id"])
                return user
            return None
        except Exception:
            return None

    def verify_password(self, stored_password: str, provided_password: str) -> bool:
        """Verify password (simple comparison for hackathon)."""
        return stored_password == provided_password

    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
