"""
Data models for the Creative AI Assistant
"""

from .narrative_context import (
    NarrativeContext,
    StoryProgress,
    NLPSignals,
    KnowledgeGraphState,
    ContinuitySignals,
    WriterPreferences,
    TriggerContext,
)

from .reasoning_output import (
    ReasoningOutput,
    MomentumAssessment,
    CharacterArcAssessment,
    EmotionalTrajectory,
    ThematicHealth,
    Opportunity,
)

from .intervention_plan import (
    InterventionPlan,
    PlannedIntervention,
    InterventionType,
    InterventionPriority,
)

__all__ = [
    # Narrative Context
    "NarrativeContext",
    "StoryProgress",
    "NLPSignals",
    "KnowledgeGraphState",
    "ContinuitySignals",
    "WriterPreferences",
    "TriggerContext",
    # Reasoning Output
    "ReasoningOutput",
    "MomentumAssessment",
    "CharacterArcAssessment",
    "EmotionalTrajectory",
    "ThematicHealth",
    "Opportunity",
    # Intervention Plan
    "InterventionPlan",
    "PlannedIntervention",
    "InterventionType",
    "InterventionPriority",
]
