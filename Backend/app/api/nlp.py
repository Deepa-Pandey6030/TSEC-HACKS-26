"""
API routes for NLP Extraction Engine
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from app.services.nlp import EntityExtractor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/nlp", tags=["NLP Extraction"])

# Initialize entity extractor (singleton)
entity_extractor = EntityExtractor()


# Request/Response Models
class NLPExtractionRequest(BaseModel):
    """Request model for NLP extraction."""
    text: str = Field(..., description="Text to analyze")
    manuscript_id: str = Field(..., description="Manuscript/story identifier")
    scene_id: Optional[str] = Field(None, description="Scene identifier")
    context: Optional[List[str]] = Field(default_factory=list, description="Active character memory")


class CharacterEntity(BaseModel):
    """Character entity extracted from text."""
    text: str
    archetype: str
    goal: str
    emotion: Optional[str] = "Neutral"


class LocationEntity(BaseModel):
    """Location entity extracted from text."""
    text: str
    type: str
    atmosphere: Optional[str] = "Neutral"


class RelationshipEntity(BaseModel):
    """Relationship between entities."""
    source: str
    target: str
    type: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class ExtractedEntities(BaseModel):
    """Extracted entities from NLP analysis."""
    characters: List[CharacterEntity] = Field(default_factory=list)
    locations: List[LocationEntity] = Field(default_factory=list)
    relationships: List[RelationshipEntity] = Field(default_factory=list)


class NLPExtractionResponse(BaseModel):
    """Response model for NLP extraction."""
    entities: ExtractedEntities
    metadata: Dict[str, Any]


# Endpoints
@router.post("/extract", response_model=NLPExtractionResponse)
async def extract_entities(request: NLPExtractionRequest):
    """
    Extract entities (characters, locations, relationships) from text.
    
    This endpoint uses the NLP Extraction Engine to analyze narrative text
    and extract structured entities for the Knowledge Graph.
    
    Args:
        request: NLP extraction request with text and metadata
        
    Returns:
        Extracted entities with metadata
        
    Example:
        ```
        POST /api/v1/nlp/extract
        {
            "text": "Alice met Bob at the old castle...",
            "manuscript_id": "story_123",
            "scene_id": "scene_45",
            "context": ["Alice"]
        }
        ```
    """
    try:
        logger.info(f"NLP extraction request for manuscript: {request.manuscript_id}")
        
        import time
        start_time = time.time()
        
        # Prepare metadata for entity extractor
        metadata = {
            "manuscript_id": request.manuscript_id,
            "scene_id": request.scene_id or "unknown",
            "paragraph": 0  # Could be enhanced to track paragraph numbers
        }
        
        # Extract entities
        extracted = await entity_extractor.extract(
            text=request.text,
            metadata=metadata,
            context=request.context or []
        )
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Convert to response format
        entities = ExtractedEntities(
            characters=[CharacterEntity(**char) for char in extracted.get("characters", [])],
            locations=[LocationEntity(**loc) for loc in extracted.get("locations", [])],
            relationships=[RelationshipEntity(**rel) for rel in extracted.get("relationships", [])]
        )
        
        # 🔥 CRITICAL: Save extracted entities to Neo4j Knowledge Graph
        from app.services.knowledge_graph.graph_manager import graph_db
        graph_db.save_extracted_entities(extracted, metadata)
        
        response_metadata = {
            "processing_time_ms": processing_time_ms,
            "model": "llama-3.1-8b-instant",
            "manuscript_id": request.manuscript_id,
            "scene_id": request.scene_id,
            "character_count": len(entities.characters),
            "location_count": len(entities.locations),
            "relationship_count": len(entities.relationships)
        }
        
        logger.info(
            f"Extraction complete: {len(entities.characters)} characters, "
            f"{len(entities.locations)} locations, {len(entities.relationships)} relationships "
            f"in {processing_time_ms}ms"
        )
        
        return NLPExtractionResponse(
            entities=entities,
            metadata=response_metadata
        )
        
    except Exception as e:
        logger.error(f"Error in NLP extraction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"NLP extraction failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for NLP service."""
    return {
        "status": "healthy",
        "service": "nlp_extraction",
        "model": "llama-3.1-8b-instant",
        "provider": "groq"
    }
