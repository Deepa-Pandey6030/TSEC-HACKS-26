"""
Authentication routes for user login/signup
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
import logging
import uuid
from typing import Optional
from pydantic import BaseModel

from app.models.user import UserCreate, UserLogin, UserResponse, LoginResponse
from app.db.user_db import MongoUserDB
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


class LogoutRequest(BaseModel):
    """Request body for logout endpoint."""
    session_token: Optional[str] = None

# Initialize MongoDB lazily (only when first needed)
user_db = None

def get_user_db():
    """Get or initialize user database connection."""
    global user_db
    if user_db is None:
        try:
            user_db = MongoUserDB(settings.mongodb_url, settings.mongodb_db_name)
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise HTTPException(status_code=503, detail="Database unavailable")
    return user_db

# In-memory session storage (for hackathon - simple session management)
# In production, use Redis or JWT
active_sessions = {}  # {session_token: user_id}


def create_session(user_id: str) -> str:
    """Create a session token for user."""
    session_token = str(uuid.uuid4())
    active_sessions[session_token] = user_id
    return session_token


def get_user_from_session(session_token: str, db: MongoUserDB) -> dict:
    """Get user from session token."""
    if session_token not in active_sessions:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    user_id = active_sessions[session_token]
    user = db.get_user_by_id(user_id)
    
    if not user:
        # Session exists but user doesn't - cleanup
        del active_sessions[session_token]
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


@router.post("/signup", response_model=LoginResponse)
async def signup(user_data: UserCreate):
    """Register a new user."""
    try:
        db = get_user_db()
        
        # Check if user already exists
        existing_user = db.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        new_user = db.create_user(
            email=user_data.email,
            name=user_data.name,
            password=user_data.password
        )
        
        # Create session
        session_token = create_session(new_user["id"])
        
        logger.info(f"✅ New user registered: {user_data.email}")
        
        return LoginResponse(
            success=True,
            message="Signup successful",
            user=UserResponse(
                id=new_user["id"],
                email=new_user["email"],
                name=new_user["name"]
            ),
            token=session_token
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail="Signup failed")


@router.post("/login", response_model=LoginResponse)
async def login(login_data: UserLogin):
    """Login user."""
    try:
        db = get_user_db()
        
        # Get user by email
        user = db.get_user_by_email(login_data.email)
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not db.verify_password(user["password"], login_data.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create session
        session_token = create_session(user["id"])
        
        logger.info(f"✅ User logged in: {login_data.email}")
        
        return LoginResponse(
            success=True,
            message="Login successful",
            user=UserResponse(
                id=user["id"],
                email=user["email"],
                name=user["name"]
            ),
            token=session_token
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.get("/me", response_model=UserResponse)
async def get_me(session_token: str = None):
    """Get current logged-in user."""
    if not session_token:
        raise HTTPException(status_code=401, detail="No session token provided")
    
    try:
        db = get_user_db()
        user = get_user_from_session(session_token, db)
        return UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user")


@router.post("/logout")
async def logout(request: LogoutRequest, authorization: Optional[str] = Header(None)):
    """Logout user by removing session."""
    session_token = request.session_token
    
    # Try to get token from Authorization header if not in body
    if not session_token and authorization:
        # Extract token from "Bearer <token>" format
        if authorization.startswith("Bearer "):
            session_token = authorization[7:]
    
    if not session_token:
        raise HTTPException(status_code=400, detail="No session token provided")
    
    if session_token in active_sessions:
        del active_sessions[session_token]
        logger.info("✅ User logged out")
        return {"success": True, "message": "Logged out successfully"}
    else:
        raise HTTPException(status_code=401, detail="Invalid or expired session token")


@router.post("/check-session")
async def check_session(session_token: str = None):
    """Check if session is valid."""
    if not session_token:
        return {"valid": False, "message": "No session token"}
    
    if session_token in active_sessions:
        try:
            db = get_user_db()
            user = get_user_from_session(session_token, db)
            return {
                "valid": True,
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "name": user["name"]
                }
            }
        except:
            return {"valid": False, "message": "Session invalid"}
    
    return {"valid": False, "message": "Session not found"}
