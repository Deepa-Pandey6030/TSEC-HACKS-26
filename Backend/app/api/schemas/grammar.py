from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict, Any

class GrammarCheckRequest(BaseModel):
    text: str
    language: str = "en-US"

class CategoryInfo(BaseModel):
    id: str
    name: str

class GrammarRule(BaseModel):
    id: str
    description: str
    issueType: str
    category: Union[str, CategoryInfo]  # Accept both string and object formats

class Replacement(BaseModel):
    value: str

class GrammarMatch(BaseModel):
    message: str
    shortMessage: Optional[str] = None
    offset: int
    length: int
    replacements: List[Replacement]
    rule: GrammarRule
    ignoreForIncompleteSentence: bool = False
    contextForSureMatch: int = 0

class GrammarCheckResponse(BaseModel):
    matches: List[GrammarMatch]
    software: Optional[Dict[str, Any]] = None
    warnings: Optional[Dict[str, Any]] = None
    language: Optional[Dict[str, Any]] = None
