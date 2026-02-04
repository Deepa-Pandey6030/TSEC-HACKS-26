"""
Models for intervention planning.
Converts reasoning into actionable plans.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime


class InterventionType(str, Enum):
    SCENE_ADDITION = "scene_addition"
    CHARACTER_MOMENT = "character_moment"
    DIALOGUE_ADJUSTMENT = "dialogue_adjustment"
    PACING_ADJUSTMENT = "pacing_adjustment"
    THEMATIC_REINFORCEMENT = "thematic_reinforcement"
    RELATIONSHIP_DEVELOPMENT = "relationship_development"
    PLOT_THREAD_RESOLUTION = "plot_thread_resolution"
    CLARIFYING_QUESTION = "clarifying_question"
    VOICE_CONSISTENCY = "voice_consistency"
    STRUCTURAL_ADJUSTMENT = "structural_adjustment"


class InterventionPriority(str, Enum):
    CRITICAL = "critical"  # Story is broken without this
    HIGH = "high"          # Significant improvement
    MEDIUM = "medium"      # Nice to have
    LOW = "low"            # Optional polish


class PlannedIntervention(BaseModel):
    """A single planned intervention."""
    intervention_type: InterventionType
    priority: InterventionPriority
    confidence: float = Field(ge=0.0, le=1.0)
    
    # Core content
    what: str  # What to do
    why: str   # Why it matters
    how: Optional[str] = None  # How to implement (if applicable)
    
    # Context
    related_scenes: List[str] = []
    related_characters: List[str] = []
    related_themes: List[str] = []
    
    # For plot forks
    alternatives: Optional[List[Dict[str, str]]] = None
    
    # Expected outcome
    expected_impact: str
    impact_areas: List[str] = []  # ["pacing", "character_development", etc.]
    
    # Metadata
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class InterventionPlan(BaseModel):
    """
    Complete plan of interventions after reasoning.
    This gets converted into AgentSuggestion objects.
    """
    story_id: str
    trigger_event: str
    
    # Planned interventions (sorted by priority)
    planned_interventions: List[PlannedIntervention] = []
    
    # Rationale
    why_these_interventions: str
    why_not_others: str
    
    # Overall assessment
    overall_story_health: str  # "excellent", "good", "needs_attention", "critical"
    health_trend: Optional[str] = None  # "improving", "stable", "declining"
    
    # Meta
    plan_created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    plan_confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    
    def get_by_priority(self, priority: InterventionPriority) -> List[PlannedIntervention]:
        """Get interventions of specific priority."""
        return [i for i in self.planned_interventions if i.priority == priority]
    
    def get_by_type(self, intervention_type: InterventionType) -> List[PlannedIntervention]:
        """Get interventions of specific type."""
        return [i for i in self.planned_interventions if i.intervention_type == intervention_type]
