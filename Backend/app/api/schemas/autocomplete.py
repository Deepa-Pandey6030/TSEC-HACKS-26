from pydantic import BaseModel, Field
from typing import Optional

class AutocompleteRequest(BaseModel):
    text: str = Field(..., description="The context text (usually last few sentences)")
    cursor_position: Optional[int] = None
    max_words: int = Field(5, description="Maximum words to predict")

class AutocompleteResponse(BaseModel):
    suggestion: str = ""
    confidence: float = 0.0
