"""
Manuscript API Routes

REST endpoints for manuscript upload, retrieval, and listing.

Endpoints:
- POST /api/v1/manuscript/upload - Upload and process a manuscript
- GET /api/v1/manuscript/{id} - Get manuscript by ID
- GET /api/v1/manuscript - List all manuscripts
- DELETE /api/v1/manuscript/{id} - Delete a manuscript
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging

from app.services.manuscript import ManuscriptProcessor
from app.db.manuscript_repository import get_manuscript_repository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/manuscript", tags=["Manuscript"])


# Response Models
class ManuscriptSummaryResponse(BaseModel):
    """Response for manuscript listing (excludes full text)."""
    id: str
    title: str
    summary: str
    word_count: int
    created_at: str
    model_used: str
    file_type: Optional[str] = None
    file_name: Optional[str] = None


class ManuscriptDetailResponse(BaseModel):
    """Full manuscript response including original text."""
    id: str
    title: str
    original_text: str
    summary: str
    word_count: int
    created_at: str
    model_used: str
    file_type: Optional[str] = None
    file_name: Optional[str] = None


class ManuscriptListResponse(BaseModel):
    """Response for listing manuscripts."""
    manuscripts: List[ManuscriptSummaryResponse]
    total: int
    limit: int
    offset: int


class ManuscriptUploadResponse(BaseModel):
    """Response for successful upload."""
    id: str
    title: str
    summary: str
    word_count: int
    model_used: str
    message: str = "Manuscript processed successfully"


class TextSubmitRequest(BaseModel):
    """Request for submitting raw text."""
    title: str = Field(..., min_length=1, max_length=500)
    text: str = Field(..., min_length=10)


# Endpoints

@router.post("/upload", response_model=ManuscriptUploadResponse)
async def upload_manuscript(
    file: UploadFile = File(..., description="Manuscript file (PDF, DOCX, or TXT)"),
    title: Optional[str] = Form(None, description="Optional title (defaults to filename)")
):
    """
    Upload and process a manuscript file.
    
    Accepts PDF, DOCX, or TXT files.
    The file will be processed to extract text and generate an AI summary.
    
    - **file**: The manuscript file to upload
    - **title**: Optional title (defaults to filename without extension)
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Get file extension
    filename = file.filename.lower()
    if filename.endswith(".pdf"):
        file_type = "pdf"
    elif filename.endswith(".docx"):
        file_type = "docx"
    elif filename.endswith(".txt"):
        file_type = "txt"
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Accepted: PDF, DOCX, TXT. Got: {filename}"
        )
    
    # Use filename as title if not provided
    if not title:
        title = file.filename.rsplit(".", 1)[0]  # Remove extension
    
    # Read file content
    try:
        content = await file.read()
    except Exception as e:
        logger.error(f"Failed to read uploaded file: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
    
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="File is empty")
    
    # Process the manuscript
    try:
        processor = ManuscriptProcessor()
        result = await processor.process(
            file_content=content,
            file_type=file_type,
            title=title,
            file_name=file.filename,
        )
        
        return ManuscriptUploadResponse(
            id=result["id"],
            title=result["title"],
            summary=result["summary"],
            word_count=result["word_count"],
            model_used=result["model_used"],
        )
        
    except ValueError as e:
        logger.warning(f"Validation error during processing: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Manuscript processing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.post("/submit-text", response_model=ManuscriptUploadResponse)
async def submit_text(request: TextSubmitRequest):
    """
    Submit raw text for processing (no file upload).
    
    - **title**: Title for the manuscript
    - **text**: The text content to process
    """
    try:
        processor = ManuscriptProcessor()
        result = await processor.process_text(
            text=request.text,
            title=request.title,
        )
        
        return ManuscriptUploadResponse(
            id=result["id"],
            title=result["title"],
            summary=result["summary"],
            word_count=result["word_count"],
            model_used=result["model_used"],
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Text processing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.get("/{manuscript_id}", response_model=ManuscriptDetailResponse)
async def get_manuscript(manuscript_id: str):
    """
    Get a manuscript by ID.
    
    Returns the full manuscript including original text.
    """
    repository = get_manuscript_repository()
    manuscript = repository.get_by_id(manuscript_id)
    
    if not manuscript:
        raise HTTPException(status_code=404, detail="Manuscript not found")
    
    # Convert datetime to string
    created_at = manuscript.get("created_at")
    if created_at:
        created_at = created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at)
    
    return ManuscriptDetailResponse(
        id=manuscript["id"],
        title=manuscript["title"],
        original_text=manuscript["original_text"],
        summary=manuscript["summary"],
        word_count=manuscript["word_count"],
        created_at=created_at or "",
        model_used=manuscript["model_used"],
        file_type=manuscript.get("file_type"),
        file_name=manuscript.get("file_name"),
    )


@router.get("", response_model=ManuscriptListResponse)
async def list_manuscripts(
    limit: int = Query(50, ge=1, le=100, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
):
    """
    List all manuscripts.
    
    Returns paginated list without full text content.
    """
    repository = get_manuscript_repository()
    
    manuscripts = repository.list_all(limit=limit, offset=offset, include_text=False)
    total = repository.count()
    
    results = []
    for m in manuscripts:
        created_at = m.get("created_at")
        if created_at:
            created_at = created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at)
        
        results.append(ManuscriptSummaryResponse(
            id=m["id"],
            title=m["title"],
            summary=m["summary"],
            word_count=m["word_count"],
            created_at=created_at or "",
            model_used=m["model_used"],
            file_type=m.get("file_type"),
            file_name=m.get("file_name"),
        ))
    
    return ManuscriptListResponse(
        manuscripts=results,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.delete("/{manuscript_id}")
async def delete_manuscript(manuscript_id: str):
    """
    Delete a manuscript by ID.
    """
    repository = get_manuscript_repository()
    
    if not repository.get_by_id(manuscript_id):
        raise HTTPException(status_code=404, detail="Manuscript not found")
    
    success = repository.delete(manuscript_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete manuscript")
    
    return {"message": "Manuscript deleted successfully", "id": manuscript_id}


@router.get("/health/check")
async def health_check():
    """Health check for manuscript service."""
    try:
        repository = get_manuscript_repository()
        count = repository.count()
        return {"status": "healthy", "manuscript_count": count}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
