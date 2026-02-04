"""
API package initialization
"""

from .creative_assistant import router as creative_assistant_router
from .grammar import router as grammar_router
from .autocomplete import router as autocomplete_router
from .nlp import router as nlp_router
from .graph import router as graph_router

__all__ = ["creative_assistant_router", "grammar_router", "autocomplete_router", "nlp_router", "graph_router"]
