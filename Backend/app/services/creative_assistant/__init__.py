"""
Creative AI Assistant - Agentic Reasoning Engine

This module implements a sophisticated agentic system that operates as a 
Senior Writer with 30+ years of experience, providing creative guidance
for narrative writing.

Main Components:
- Agentic Reasoning Engine: Core OBSERVE → INTERPRET → REASON → PLAN → SUGGEST → REFLECT → ADAPT loop
- Grok Integration: Production-grade xAI Grok API wrapper
- Observation Synthesizer: Multi-source input aggregation
- Narrative Interpreter: Context understanding
- Intervention Planner: Decision logic
- Suggestion Generator: Output formatting
- Preference Learner: Adaptation system
"""

from .agentic_reasoning_engine import AgenticReasoningEngine
from .grok_integration import GrokIntegration

__all__ = [
    "AgenticReasoningEngine",
    "GrokIntegration",
]
