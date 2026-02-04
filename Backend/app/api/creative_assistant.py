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
    # Predictive Risk Analysis (NEW)
    predictive_risks: Optional[Dict[str, Any]] = None
    risk_summary: Optional[str] = None
    primary_risk: Optional[str] = None


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
    focus: str = "pacing"  # pacing, transitions, clarity, engagement (legacy)
    tone: str = "default"  # default, academic, business, simple, creative
    preserve_formatting: bool = True


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
    Quick analysis endpoint with Predictive Plot Risk Analysis.
    Analyzes narrative structure and predicts future risks.
    """
    try:
        from app.services.creative_assistant.plot_risk_analyzer import PlotRiskAnalyzer
        
        logger.info(f"Quick analyze with plot risk analysis: {request.story_title}")
        
        # Run predictive plot risk analysis
        plot_analyzer = PlotRiskAnalyzer()
        risk_analysis = await plot_analyzer.analyze_plot_risks(
            content=request.recent_scene_summary,
            story_title=request.story_title,
            genre=request.genre,
            completion_percentage=request.completion_percentage
        )
        
        # Create minimal mock data for standard analysis
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
        
        # Run standard analysis
        standard_analysis = await analyze_story(analysis_request)
        
        # Enhance response with predictive risks
        standard_analysis.predictive_risks = risk_analysis
        standard_analysis.risk_summary = risk_analysis.get("predictive_summary", "")
        standard_analysis.primary_risk = risk_analysis.get("primary_risk", "")
        
        logger.info(f"Analysis complete with risk scores: {risk_analysis.get('risk_scores', {})}")
        
        return standard_analysis
        
    except Exception as e:
        logger.error(f"Error in quick analyze: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rewrite")
async def rewrite_content(request: RewriteRequest):
    """
    Advanced document rewriting with production-grade quality.
    Uses enterprise system prompt for professional editing.
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
        
        # Enterprise system prompt for professional document rewriting
        system_prompt = """You are a Senior Full-Stack Document Rewrite Engine with 30+ years of production experience.

PRIMARY OBJECTIVE: Rewrite and improve documents while:
- Preserving original meaning exactly
- Improving clarity, grammar, flow, and structure
- Maintaining formatting and section hierarchy
- Avoiding hallucinations or content loss

DOCUMENT PROCESSING STRATEGY:
1. Parse: Identify headings, sections, lists, paragraphs
2. Understand: Determine intent, track terminology
3. Rewrite: Improve readability while preserving semantics 100%
4. Maintain Continuity: Keep consistent terminology

REWRITING RULES (STRICT):
- Do NOT summarize unless asked
- Do NOT skip content
- Do NOT hallucinate missing sections
- Do NOT change technical meaning
- Do NOT add explanations

OUTPUT REQUIREMENTS:
- Output ONLY the rewritten content
- No commentary or explanations
- Clean formatting
- High editorial quality

QUALITY BAR: Senior human editor standard, publish-ready quality."""
        
        # Style-specific instructions
        style_instructions = {
            "professional": "Rewrite in professional, polished style. Maintain clarity and precision.",
            "creative": "Rewrite with creative flair and vivid imagery while preserving all facts.",
            "concise": "Rewrite more concisely while keeping all key information.",
            "dramatic": "Rewrite with dramatic tension and emotional impact while staying factual.",
            "academic": "Rewrite in formal academic style with precise language.",
            "business": "Rewrite in concise executive-friendly business style.",
            "simplified": "Rewrite in plain language for easy understanding."
        }
        
        instruction = style_instructions.get(request.style, style_instructions["professional"])
        
        user_prompt = f"""{instruction}

Original text:
{request.content}

Rewritten text:"""
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=4000  # Increased for longer documents
        )
        
        rewritten = response.choices[0].message.content.strip()
        
        return {
            "original": request.content,
            "rewritten": rewritten,
            "style": request.style,
            "quality": "enterprise-grade"
        }
        
    except Exception as e:
        logger.error(f"Error in rewrite: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/improve-flow")
async def improve_flow(request: ImproveFlowRequest):
    """
    Production-grade flow improvement using FlowEngine.
    Supports long documents, multiple tones, and strict content preservation.
    """
    try:
        from app.services.creative_assistant.flow_engine import FlowEngine
        
        logger.info(f"Flow improvement request: tone={request.tone}, length={len(request.content)}")
        
        # Initialize Flow Engine
        flow_engine = FlowEngine()
        
        # Process with Flow Engine
        result = await flow_engine.improve_flow(
            content=request.content,
            tone=request.tone,
            preserve_formatting=request.preserve_formatting
        )
        
        logger.info(f"Flow improvement complete: chunks={result['chunks_processed']}, tokens={result['tokens_used']}")
        
        return {
            "original": result["original"],
            "improved": result["improved"],
            "tone": result["tone"],
            "focus": request.focus,  # Legacy compatibility
            "metadata": {
                "chunks_processed": result["chunks_processed"],
                "total_chunks": result["total_chunks"],
                "tokens_used": result["tokens_used"],
                "provider": result["provider"],
                "model": result["model"]
            }
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

