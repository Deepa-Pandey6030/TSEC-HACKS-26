"""
Models for Grok's reasoning output.
These capture the AI's creative judgment.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class MomentumStatus(str, Enum):
    HEALTHY = "healthy"
    STALLING = "stalling"
    RUSHING = "rushing"
    UNSTABLE = "unstable"


class EmotionalTrend(str, Enum):
    BUILDING = "building"
    PLATEAUING = "plateauing"
    DISSIPATING = "dissipating"
    VOLATILE = "volatile"


class ReinforcementQuality(str, Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    ABSENT = "absent"


class MomentumAssessment(BaseModel):
    """Assessment of narrative momentum."""
    status: MomentumStatus
    evidence: str
    senior_writer_intuition: str
    specific_concerns: List[str] = []
    pacing_score: float = Field(default=0.5, ge=0.0, le=1.0)


class CharacterTransformationIssue(BaseModel):
    """Specific character arc issue."""
    character: str
    issue: str
    suggestion: str
    severity: str = "moderate"  # "minor", "moderate", "major"


class CharacterArcAssessment(BaseModel):
    """Assessment of character development."""
    characters_at_risk: List[str] = []
    transformations_needing_attention: List[CharacterTransformationIssue] = []
    reasoning: str
    character_specific_notes: Dict[str, str] = {}
    overall_arc_health: str = "good"  # "excellent", "good", "needs_work", "problematic"


class EmotionalTrajectory(BaseModel):
    """Analysis of emotional journey."""
    current_state: str
    trend: EmotionalTrend
    notes: str
    next_beats_needed: List[str] = []
    emotional_coherence_score: float = Field(default=0.7, ge=0.0, le=1.0)


class StructuralConcern(BaseModel):
    """Specific structural issue."""
    concern: str
    severity: str  # "minor", "moderate", "major", "critical"
    affected_scenes: List[str] = []
    recommendation: Optional[str] = None


class ThematicHealth(BaseModel):
    """Assessment of thematic development."""
    themes_present: List[str]
    reinforcement_quality: ReinforcementQuality
    notes: str
    missed_opportunities: List[str] = []
    thematic_coherence_score: float = Field(default=0.7, ge=0.0, le=1.0)


class Opportunity(BaseModel):
    """A creative opportunity identified by the AI."""
    type: str  # "scene_addition", "character_moment", "thematic_echo", etc.
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str  # Why this opportunity exists
    would_a_senior_writer_consider_this: str  # "yes", "no", "maybe"
    why: str  # Detailed reasoning
    specific_suggestion: Optional[str] = None
    expected_impact: Optional[str] = None
    
    # Context
    related_scenes: List[str] = []
    related_characters: List[str] = []
    related_themes: List[str] = []
    
    # Alternatives (for plot forks)
    alternatives: Optional[List[Dict[str, str]]] = None


class ReasoningOutput(BaseModel):
    """
    Complete output from Grok's narrative reasoning.
    This is the AI's creative judgment on story health.
    """
    # Core assessments
    momentum_assessment: MomentumAssessment
    character_arc_assessment: CharacterArcAssessment
    emotional_trajectory: EmotionalTrajectory
    structural_concerns: List[StructuralConcern] = []
    thematic_health: ThematicHealth
    
    # Opportunities and questions
    opportunities: List[Opportunity] = []
    questions_for_writer: List[str] = []
    
    # Overall assessment
    overall_story_health: str = "good"  # "excellent", "good", "needs_attention", "critical"
    overall_health_reasoning: Optional[str] = None
    
    # Meta
    reasoning_confidence: float = Field(ge=0.0, le=1.0)
    reasoning_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # Model info
    model_used: str = "grok-beta"
    tokens_used: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "momentum_assessment": {
                    "status": "healthy",
                    "evidence": "Scenes progress naturally with clear cause-effect",
                    "senior_writer_intuition": "The pacing feels right for this genre"
                },
                "character_arc_assessment": {
                    "reasoning": "Main character showing incremental growth",
                    "overall_arc_health": "good"
                },
                "emotional_trajectory": {
                    "current_state": "Building tension with underlying hope",
                    "trend": "building",
                    "notes": "Emotional investment is strong"
                },
                "thematic_health": {
                    "themes_present": ["redemption", "family"],
                    "reinforcement_quality": "moderate",
                    "notes": "Themes emerging naturally"
                },
                "reasoning_confidence": 0.85
            }
        }
