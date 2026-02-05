"""
Manuscript Repository

Handles all CRUD operations for manuscripts in MongoDB.
Follows the Repository pattern to isolate data access logic.

MongoDB Collection: manuscripts
Document Schema:
{
    _id: ObjectId,
    title: str,
    original_text: str,
    summary: str,
    word_count: int,
    created_at: datetime (UTC),
    model_used: str,
    file_type: str (optional - pdf, docx, txt),
    file_name: str (optional - original filename)
}
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from bson.objectid import ObjectId
import logging

from app.db.mongodb import get_database

logger = logging.getLogger(__name__)


class ManuscriptRepository:
    """
    Repository for manuscript documents.
    Provides clean CRUD interface over MongoDB.
    """
    
    COLLECTION_NAME = "manuscripts"
    
    def __init__(self):
        """Initialize with database connection."""
        self.db = get_database()
        self.collection = self.db[self.COLLECTION_NAME]
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Create indexes for common query patterns."""
        try:
            # Index on created_at for sorting by recency
            self.collection.create_index("created_at", background=True)
            # Text index on title for search
            self.collection.create_index([("title", "text")], background=True)
            logger.debug("Manuscript indexes ensured")
        except Exception as e:
            logger.warning(f"Index creation warning: {e}")
    
    def create(
        self,
        title: str,
        original_text: str,
        summary: str,
        word_count: int,
        model_used: str,
        file_type: Optional[str] = None,
        file_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new manuscript document.
        
        Args:
            title: Document title
            original_text: Full extracted text
            summary: AI-generated summary
            word_count: Number of words in original text
            model_used: LLM model used for summarization
            file_type: Original file format (pdf, docx, txt)
            file_name: Original filename
            
        Returns:
            Created document with string ID
        """
        document = {
            "title": title,
            "original_text": original_text,
            "summary": summary,
            "word_count": word_count,
            "created_at": datetime.now(timezone.utc),
            "model_used": model_used,
            "file_type": file_type,
            "file_name": file_name,
        }
        
        try:
            result = self.collection.insert_one(document)
            document["id"] = str(result.inserted_id)
            if "_id" in document:
                del document["_id"]
            
            logger.info(f"📝 Manuscript created: {title} (ID: {document['id']})")
            return document
            
        except Exception as e:
            logger.error(f"Failed to create manuscript: {e}")
            raise
    
    def get_by_id(self, manuscript_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a manuscript by its ID.
        
        Args:
            manuscript_id: String representation of MongoDB ObjectId
            
        Returns:
            Manuscript document or None if not found
        """
        try:
            doc = self.collection.find_one({"_id": ObjectId(manuscript_id)})
            if doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                return doc
            return None
        except Exception as e:
            logger.error(f"Failed to get manuscript {manuscript_id}: {e}")
            return None
    
    def list_all(
        self,
        limit: int = 50,
        offset: int = 0,
        include_text: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List manuscripts with pagination.
        
        Args:
            limit: Maximum number of results (default 50)
            offset: Number of documents to skip
            include_text: Whether to include full original_text (heavy)
            
        Returns:
            List of manuscript documents
        """
        try:
            # Projection to exclude heavy fields by default
            projection = None
            if not include_text:
                projection = {"original_text": 0}
            
            cursor = (
                self.collection
                .find({}, projection)
                .sort("created_at", -1)  # Most recent first
                .skip(offset)
                .limit(limit)
            )
            
            results = []
            for doc in cursor:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                results.append(doc)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to list manuscripts: {e}")
            return []
    
    def count(self) -> int:
        """Get total count of manuscripts."""
        try:
            return self.collection.count_documents({})
        except Exception as e:
            logger.error(f"Failed to count manuscripts: {e}")
            return 0
    
    def delete(self, manuscript_id: str) -> bool:
        """
        Delete a manuscript by ID.
        
        Args:
            manuscript_id: String representation of MongoDB ObjectId
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            result = self.collection.delete_one({"_id": ObjectId(manuscript_id)})
            if result.deleted_count > 0:
                logger.info(f"🗑️ Manuscript deleted: {manuscript_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete manuscript {manuscript_id}: {e}")
            return False


# Singleton instance for easy import
_repository: Optional[ManuscriptRepository] = None


def get_manuscript_repository() -> ManuscriptRepository:
    """Get or create the manuscript repository instance."""
    global _repository
    if _repository is None:
        _repository = ManuscriptRepository()
    return _repository
