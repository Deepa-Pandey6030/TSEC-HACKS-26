"""
Prompt engineering templates for the Creative AI Assistant
"""

from .senior_writer_system import SENIOR_WRITER_SYSTEM_PROMPT
from .reasoning_templates import build_narrative_reasoning_prompt

__all__ = [
    "SENIOR_WRITER_SYSTEM_PROMPT",
    "build_narrative_reasoning_prompt",
]
