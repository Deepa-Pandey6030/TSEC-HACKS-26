"""
API package initialization
"""

from .creative_assistant import router as creative_assistant_router
from .grammar import router as grammar_router
from .autocomplete import router as autocomplete_router

__all__ = ["creative_assistant_router", "grammar_router", "autocomplete_router"]
