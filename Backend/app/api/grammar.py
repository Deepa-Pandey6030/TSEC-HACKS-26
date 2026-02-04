from fastapi import APIRouter
from app.services.grammar_service import grammar_service
from app.api.schemas.grammar import GrammarCheckRequest, GrammarCheckResponse
import logging

router = APIRouter(prefix="/api/v1/grammar", tags=["Grammar"])
logger = logging.getLogger(__name__)

@router.post("/check", response_model=GrammarCheckResponse)
async def check_grammar(request: GrammarCheckRequest):
    """
    Check grammar for the given text.
    """
    try:
        result = await grammar_service.check_grammar(request.text, request.language)
        return result
    except Exception as e:
        logger.error(f"Failed to check grammar: {e}")
        # Graceful degradation
        return {"matches": [], "software": {}, "warnings": {}, "language": {}}
