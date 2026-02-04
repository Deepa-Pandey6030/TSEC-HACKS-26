from fastapi import APIRouter, HTTPException
from app.api.schemas.autocomplete import AutocompleteRequest, AutocompleteResponse
from app.services.autocomplete_service import autocomplete_service

router = APIRouter(prefix="/api/v1/autocomplete", tags=["Autocomplete"])

@router.post("/predict", response_model=AutocompleteResponse)
async def predict(request: AutocompleteRequest):
    """
    Get smart compose suggestion.
    """
    suggestion = await autocomplete_service.predict_next_text(request.text, request.max_words)
    return {"suggestion": suggestion, "confidence": 1.0 if suggestion else 0.0}
