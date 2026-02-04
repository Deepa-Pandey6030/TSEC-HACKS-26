"""
API routes for Creative AI Assistant
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import io

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


class QuickAnalyzeRequest(BaseModel):
    """Request model for quick analysis."""
    story_title: str
    genre: str
    completion_percentage: float
    recent_scene_summary: str


class RewriteRequest(BaseModel):
    """Request model for content rewriting."""
    content: str
    style: str = "professional"  # professional, creative, concise, dramatic


class ImproveFlowRequest(BaseModel):
    """Request model for flow improvement."""
    content: str
    focus: str = "pacing"  # pacing, transitions, clarity, engagement


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
async def quick_analyze(request: QuickAnalyzeRequest):
    """
    Quick analysis endpoint for simple use cases.
    Generates mock data for demonstration.
    """
    try:
        # Create minimal mock data
        analysis_request = StoryAnalysisRequest(
            story_id=f"story_{request.story_title.lower().replace(' ', '_')}",
            knowledge_graph_data={
                "story_metadata": {
                    "title": request.story_title,
                    "genre": request.genre,
                    "completion_percentage": request.completion_percentage,
                    "word_count": int(request.completion_percentage * 800),
                    "target_word_count": 80000,
                    "current_act": 2 if request.completion_percentage > 30 else 1,
                    "total_acts": 3
                }
            },
            recent_scenes=[{
                "id": "scene_latest",
                "title": "Recent Scene",
                "summary": request.recent_scene_summary
            }]
        )
        
        return await analyze_story(analysis_request)
        
    except Exception as e:
        logger.error(f"Error in quick analyze: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rewrite")
async def rewrite_content(request: RewriteRequest):
    """
    Rewrite content with specified style using AI.
    """
    try:
        from openai import OpenAI
        from app.config import settings
        
        # Determine API provider
        api_key = settings.xai_api_key
        if api_key.startswith("gsk_"):
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            model = "llama-3.3-70b-versatile"
        else:
            client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
            model = settings.grok_model
        
        # Create rewrite prompt
        style_prompts = {
            "professional": "Rewrite this text in a professional, polished style while maintaining the core message.",
            "creative": "Rewrite this text with more creative flair, vivid imagery, and engaging language.",
            "concise": "Rewrite this text to be more concise and direct while keeping all key information.",
            "dramatic": "Rewrite this text with more dramatic tension and emotional impact."
        }
        
        prompt = f"""{style_prompts.get(request.style, style_prompts['professional'])}

Original text:
{request.content}

Rewritten text:"""
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a professional editor and writer with 30+ years of experience."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        rewritten = response.choices[0].message.content.strip()
        
        return {
            "original": request.content,
            "rewritten": rewritten,
            "style": request.style
        }
        
    except Exception as e:
        logger.error(f"Error in rewrite: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/improve-flow")
async def improve_flow(request: ImproveFlowRequest):
    """
    Improve the flow of content with AI suggestions.
    """
    try:
        from openai import OpenAI
        from app.config import settings
        import re
        
        # Determine API provider
        api_key = settings.xai_api_key
        if api_key.startswith("gsk_"):
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            model = "llama-3.3-70b-versatile"
        else:
            client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
            model = settings.grok_model
        
        # Create flow improvement prompt - request ONLY the improved text
        focus_prompts = {
            "pacing": "Improve the pacing of this text. Return ONLY the improved text, nothing else.",
            "transitions": "Improve the transitions between ideas in this text. Return ONLY the improved text, nothing else.",
            "clarity": "Improve the clarity of this text. Return ONLY the improved text, nothing else.",
            "engagement": "Make this text more engaging. Return ONLY the improved text, nothing else."
        }
        
        prompt = f"""{focus_prompts.get(request.focus, focus_prompts['pacing'])}

Original text:
{request.content}

Improved text (return ONLY the text, no explanations or markers):"""
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a professional editor. When asked to improve text, return ONLY the improved text without any explanations, markers, or formatting like **Improved Version:**. Just return the clean improved text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        result = response.choices[0].message.content.strip()
        
        # Clean up any remaining formatting markers
        result = re.sub(r'\*\*.*?\*\*:?\s*', '', result)  # Remove **markers**
        result = re.sub(r'^(Improved Version|Improved Text|Here is|Here\'s).*?:\s*', '', result, flags=re.IGNORECASE)
        result = result.strip()
        
        return {
            "original": request.content,
            "improved": result,
            "focus": request.focus
        }
        
    except Exception as e:
        logger.error(f"Error in improve flow: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and extract text from PDF, DOCX, or TXT files.
    """
    try:
        logger.info(f"Uploading file: {file.filename}")
        
        # Check file type
        filename = file.filename.lower()
        if not (filename.endswith('.pdf') or filename.endswith('.docx') or filename.endswith('.txt')):
            raise HTTPException(status_code=400, detail="Only PDF, DOCX, and TXT files are supported")
        
        # Read file content
        content = await file.read()
        extracted_text = ""
        
        # Extract text based on file type
        if filename.endswith('.txt'):
            extracted_text = content.decode('utf-8', errors='ignore')
        
        elif filename.endswith('.pdf'):
            try:
                import PyPDF2
                pdf_file = io.BytesIO(content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                for page in pdf_reader.pages:
                    extracted_text += page.extract_text() + "\n"
            except ImportError:
                raise HTTPException(status_code=500, detail="PDF support not available. Install PyPDF2.")
        
        elif filename.endswith('.docx'):
            try:
                import docx
                docx_file = io.BytesIO(content)
                doc = docx.Document(docx_file)
                for paragraph in doc.paragraphs:
                    extracted_text += paragraph.text + "\n"
            except ImportError:
                raise HTTPException(status_code=500, detail="DOCX support not available. Install python-docx.")
        
        return {
            "filename": file.filename,
            "text": extracted_text.strip(),
            "length": len(extracted_text.strip())
        }
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

