"""
FastAPI dependencies for authentication and authorization.

Provides reusable dependency functions for protected routes.
"""
from fastapi import Header, HTTPException
from typing import Optional
import logging

from app.api.auth import active_sessions, get_user_db

logger = logging.getLogger(__name__)


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Extract and validate user from Authorization header.
    
    Args:
        authorization: Authorization header value (Bearer <token>)
        
    Returns:
        User dict with 'id', 'email', 'name' fields
        
    Raises:
        HTTPException: 401 if not authenticated or session invalid
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Extract token from "Bearer <token>" format
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    session_token = authorization[7:]  # Remove "Bearer " prefix
    
    # Validate session exists
    if session_token not in active_sessions:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    # Get user from session
    user_id = active_sessions[session_token]
    db = get_user_db()
    user = db.get_user_by_id(user_id)
    
    if not user:
        # Session exists but user doesn't - cleanup
        del active_sessions[session_token]
        raise HTTPException(status_code=401, detail="User not found")
    
    logger.debug(f"Authenticated user: {user['email']}")
    return user
