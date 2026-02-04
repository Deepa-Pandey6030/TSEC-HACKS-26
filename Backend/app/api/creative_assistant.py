"""
API routes for Creative AI Assistant
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from app.services.creative_assistant import AgenticReasoningEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/creative-assistant", tags=["Creative AI Assistant"])

# Initialize reasoning engine (singleton)
reasoning_engine = AgenticReasoningEngine()


# Request/Response Models
class StoryAnalysisRequest(BaseModel):
    """Request model for story analysis."""
    story_id: str
    nlp_data: Dict[str, Any] = Field(default_factory=dict)
    knowledge_graph_data: Dict[str, Any] = Field(default_factory=dict)
    continuity_data: Dict[str, Any] = Field(default_factory=dict)
    writer_prefs_data: Dict[str, Any] = Field(default_factory=dict)
    recent_scenes: List[Dict[str, Any]] = Field(default_factory=list)
    trigger_event: str = "manual_request"
    trigger_metadata: Optional[Dict[str, Any]] = None


class InterventionResponse(BaseModel):
    """Response model for a single intervention."""
    intervention_type: str
    priority: str
    confidence: float
    what: str
    why: str
    how: Optional[str] = None
    expected_impact: str
    impact_areas: List[str] = []
    related_scenes: List[str] = []
    related_characters: List[str] = []
    related_themes: List[str] = []


class AnalysisResponse(BaseModel):
    """Response model for complete analysis."""
    story_id: str
    overall_story_health: str
    plan_confidence: float
    interventions: List[InterventionResponse]
    trigger_event: str
    why_these_interventions: str
    why_not_others: str
    created_at: str


class FeedbackRequest(BaseModel):
    """Request model for feedback."""
    story_id: str
    intervention_id: str
    action: str  # "accepted", "rejected", "modified"
    modified: bool = False
    writer_notes: Optional[str] = None


# Endpoints
@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_story(request: StoryAnalysisRequest):
    """
    Analyze a story and generate creative suggestions.
    
    This runs the complete agentic reasoning cycle:
    OBSERVE → INTERPRET → REASON → PLAN → SUGGEST
    """
    try:
        logger.info(f"Analyzing story: {request.story_id}")
        
        # Run reasoning cycle
        plan = await reasoning_engine.run_reasoning_cycle(
            story_id=request.story_id,
            nlp_data=request.nlp_data,
            knowledge_graph_data=request.knowledge_graph_data,
            continuity_data=request.continuity_data,
            writer_prefs_data=request.writer_prefs_data,
            recent_scenes=request.recent_scenes,
            trigger_event=request.trigger_event,
            trigger_metadata=request.trigger_metadata or {}
        )
        
        # Convert to response format
        interventions = [
            InterventionResponse(
                intervention_type=i.intervention_type.value,
                priority=i.priority.value,
                confidence=i.confidence,
                what=i.what,
                why=i.why,
                how=i.how,
                expected_impact=i.expected_impact,
                impact_areas=i.impact_areas,
                related_scenes=i.related_scenes,
                related_characters=i.related_characters,
                related_themes=i.related_themes
            )
            for i in plan.planned_interventions
        ]
        
        return AnalysisResponse(
            story_id=plan.story_id,
            overall_story_health=plan.overall_story_health,
            plan_confidence=plan.plan_confidence,
            interventions=interventions,
            trigger_event=plan.trigger_event,
            why_these_interventions=plan.why_these_interventions,
            why_not_others=plan.why_not_others,
            created_at=plan.plan_created_at
        )
        
    except Exception as e:
        logger.error(f"Error analyzing story: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest, background_tasks: BackgroundTasks):
    """
    Submit feedback on a suggestion.
    
    This triggers the REFLECT step of the reasoning loop.
    """
    try:
        logger.info(f"Processing feedback for intervention: {request.intervention_id}")
        
        # Process feedback in background
        background_tasks.add_task(
            reasoning_engine.process_feedback,
            story_id=request.story_id,
            intervention_id=request.intervention_id,
            feedback={
                "action": request.action,
                "modified": request.modified,
                "writer_notes": request.writer_notes
            }
        )
        
        return {
            "status": "success",
            "message": "Feedback received and processing"
        }
        
    except Exception as e:
        logger.error(f"Error processing feedback: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "creative_ai_assistant",
        "provider": reasoning_engine.grok.provider if hasattr(reasoning_engine.grok, 'provider') else "unknown",
        "model": reasoning_engine.grok.model if hasattr(reasoning_engine.grok, 'model') else "unknown"
    }


@router.post("/quick-analyze")
async def quick_analyze(
    story_title: str,
    genre: str,
    completion_percentage: float,
    recent_scene_summary: str
):
    """
    Quick analysis endpoint for simple use cases.
    Generates mock data for demonstration.
    """
    try:
        # Create minimal mock data
        request = StoryAnalysisRequest(
            story_id=f"story_{story_title.lower().replace(' ', '_')}",
            knowledge_graph_data={
                "story_metadata": {
                    "title": story_title,
                    "genre": genre,
                    "completion_percentage": completion_percentage,
                    "word_count": int(completion_percentage * 800),
                    "target_word_count": 80000,
                    "current_act": 2 if completion_percentage > 30 else 1,
                    "total_acts": 3
                }
            },
            recent_scenes=[{
                "id": "scene_latest",
                "title": "Recent Scene",
                "summary": recent_scene_summary
            }]
        )
        
        return await analyze_story(request)
        
    except Exception as e:
        logger.error(f"Error in quick analyze: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
