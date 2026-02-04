"""
Data models for narrative context.
These structures hold all inputs from other modules.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class PacingTrend(str, Enum):
    ACCELERATING = "accelerating"
    STEADY = "steady"
    DECELERATING = "decelerating"
    STALLING = "stalling"


class EmotionalDirection(str, Enum):
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    VOLATILE = "volatile"


@dataclass
class NLPSignals:
    """
    Signals from NLP Extraction Engine (Deepa's module).
    Contains tone, pacing, voice analysis from recent scenes.
    """
    # Per-scene analysis
    recent_scenes_analysis: List[Dict[str, Any]] = field(default_factory=list)
    
    # Aggregated trends
    pacing_trend: PacingTrend = PacingTrend.STEADY
    pacing_velocity: float = 0.0  # Rate of change
    
    # Emotional analysis
    emotional_arc: Dict[str, Any] = field(default_factory=dict)
    emotional_direction: EmotionalDirection = EmotionalDirection.STABLE
    emotional_intensity: float = 0.5  # 0-1
    
    # Voice analysis
    voice_consistency: Dict[str, Any] = field(default_factory=dict)
    dialogue_density_trend: str = "stable"
    
    # Tension tracking
    tension_curve: List[float] = field(default_factory=list)  # Last N scenes
    tension_average: float = 0.5
    tension_variance: float = 0.0
    
    # Word-level metrics
    avg_sentence_length_trend: List[float] = field(default_factory=list)
    vocabulary_complexity_trend: List[float] = field(default_factory=list)


@dataclass
class KnowledgeGraphState:
    """
    State from Knowledge Graph (Yash's module).
    Contains character states, relationships, events, themes.
    """
    # Characters
    character_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    character_count: int = 0
    characters_with_recent_development: List[str] = field(default_factory=list)
    characters_stagnant: List[str] = field(default_factory=list)
    
    # Relationships
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    relationship_changes_recent: List[Dict[str, Any]] = field(default_factory=list)
    
    # Events
    recent_events: List[Dict[str, Any]] = field(default_factory=list)
    event_causality_chains: List[List[str]] = field(default_factory=list)
    
    # Themes
    thematic_threads: List[Dict[str, Any]] = field(default_factory=list)
    theme_manifestation_count: Dict[str, int] = field(default_factory=dict)
    themes_underutilized: List[str] = field(default_factory=list)
    
    # Plot tracking
    unresolved_plot_threads: List[str] = field(default_factory=list)
    plot_threads_aging: List[Dict[str, Any]] = field(default_factory=list)  # Unresolved for N+ scenes
    
    # Locations and world state
    locations_used: List[str] = field(default_factory=list)
    world_state_changes: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ContinuitySignals:
    """
    Signals from Continuity Validator (Hardik's module).
    Contains flags and inconsistency analysis.
    """
    # All active flags
    active_flags: List[Dict[str, Any]] = field(default_factory=list)
    
    # Severity distribution
    severity_distribution: Dict[str, int] = field(default_factory=dict)  # {"critical": 0, "major": 2, ...}
    
    # Category breakdown
    categories_affected: List[str] = field(default_factory=list)
    category_distribution: Dict[str, int] = field(default_factory=dict)
    
    # Intentionality assessment
    potentially_intentional: List[Dict[str, Any]] = field(default_factory=list)
    confirmed_errors: List[Dict[str, Any]] = field(default_factory=list)
    
    # Trend analysis
    flags_increasing: bool = False
    flags_resolved_recently: int = 0


@dataclass
class WriterPreferences:
    """
    Historical preferences from Recall/Query Engine (Yash's module).
    Learning data about writer's style and responses.
    """
    # Suggestion preferences
    suggestion_type_weights: Dict[str, float] = field(default_factory=dict)
    confidence_threshold: float = 0.7
    max_suggestions_per_session: int = 5
    
    # Response patterns
    acceptance_rate: float = 0.0
    acceptance_by_type: Dict[str, float] = field(default_factory=dict)
    rejection_reasons: Dict[str, int] = field(default_factory=dict)
    
    # Style preferences
    tone_preferences: Dict[str, float] = field(default_factory=dict)
    structural_preferences: Dict[str, float] = field(default_factory=dict)
    
    # Character focus
    character_focus: Dict[str, float] = field(default_factory=dict)
    
    # Interaction style
    prefers_questions_over_suggestions: bool = False
    detail_level: str = "moderate"  # "minimal", "moderate", "detailed"
    
    # History
    total_suggestions_received: int = 0
    total_suggestions_accepted: int = 0
    total_suggestions_rejected: int = 0
    recent_decisions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Learning metadata
    preference_confidence: float = 0.5  # How confident we are in these preferences
    last_updated: Optional[datetime] = None


@dataclass
class StoryProgress:
    """High-level story state and metadata."""
    story_id: str
    title: str
    genre: str
    subgenre: Optional[str] = None
    
    # Structure
    current_act: int = 1
    total_acts: int = 3
    current_scene_id: Optional[str] = None
    
    # Progress metrics
    completion_percentage: float = 0.0
    word_count: int = 0
    target_word_count: int = 80000
    scenes_written: int = 0
    
    # Metadata
    author_id: str = ""
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None


@dataclass
class TriggerContext:
    """Context about what triggered this reasoning cycle."""
    event: str  # "new_scene_added", "continuity_flag_raised", "writer_request", etc.
    metadata: Dict[str, Any] = field(default_factory=dict)
    scene_id: Optional[str] = None
    urgency: str = "normal"  # "low", "normal", "high", "critical"


@dataclass
class NarrativeContext:
    """
    Complete holistic context for AI reasoning.
    This aggregates all inputs from different modules.
    
    This is the SINGLE SOURCE OF TRUTH for the reasoning engine.
    """
    # Core components
    story_progress: StoryProgress
    nlp_signals: NLPSignals
    knowledge_graph_state: KnowledgeGraphState
    continuity_signals: ContinuitySignals
    writer_preferences: WriterPreferences
    
    # Recent content (for detailed analysis)
    recent_scenes: List[Dict[str, Any]] = field(default_factory=list)
    
    # Trigger information
    trigger: TriggerContext = field(default_factory=lambda: TriggerContext(event="unknown"))
    
    # Timestamps
    analyzed_at: datetime = field(default_factory=datetime.now)
    
    # Quality metrics
    context_completeness_score: float = 0.0  # Computed: how complete is our data?
    data_source_reliability: Dict[str, float] = field(default_factory=dict)
    
    def compute_completeness(self) -> float:
        """
        Compute how complete our context data is.
        Returns score 0-1.
        """
        score = 0.0
        total_components = 5
        
        # Check each component
        if self.recent_scenes and len(self.recent_scenes) >= 3:
            score += 0.2
        
        if self.knowledge_graph_state.character_states:
            score += 0.2
        
        if self.nlp_signals.recent_scenes_analysis:
            score += 0.2
        
        if self.writer_preferences.total_suggestions_received > 5:
            score += 0.2
        
        if self.story_progress.completion_percentage > 10:
            score += 0.2
        
        self.context_completeness_score = score
        return score
    
    def get_narrative_stage(self) -> str:
        """Identify narrative stage based on completion."""
        completion = self.story_progress.completion_percentage
        
        if completion < 20:
            return "early_setup"
        elif completion < 40:
            return "world_establishment"
        elif completion < 60:
            return "rising_action"
        elif completion < 80:
            return "climax_approach"
        elif completion < 95:
            return "climax_and_resolution"
        else:
            return "final_polish"
    
    def get_focus_areas(self) -> List[str]:
        """Identify what needs attention based on signals."""
        focus = []
        
        # Pacing issues
        if self.nlp_signals.pacing_trend == PacingTrend.STALLING:
            focus.append("pacing")
        
        # Character development
        if self.knowledge_graph_state.characters_stagnant:
            focus.append("character_development")
        
        # Continuity
        if len(self.continuity_signals.active_flags) > 5:
            focus.append("continuity")
        
        # Themes
        if len(self.knowledge_graph_state.thematic_threads) < 2:
            focus.append("thematic_development")
        
        # Plot threads
        if len(self.knowledge_graph_state.unresolved_plot_threads) > 10:
            focus.append("plot_management")
        
        # Relationships
        if not self.knowledge_graph_state.relationship_changes_recent:
            focus.append("relationship_dynamics")
        
        return focus
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "story_progress": {
                "story_id": self.story_progress.story_id,
                "title": self.story_progress.title,
                "genre": self.story_progress.genre,
                "completion_percentage": self.story_progress.completion_percentage,
                "word_count": self.story_progress.word_count,
                "target_word_count": self.story_progress.target_word_count,
                "current_act": self.story_progress.current_act,
                "total_acts": self.story_progress.total_acts
            },
            "nlp_signals": {
                "pacing_trend": self.nlp_signals.pacing_trend.value,
                "emotional_arc": self.nlp_signals.emotional_arc,
                "voice_consistency": self.nlp_signals.voice_consistency,
                "tension_curve": self.nlp_signals.tension_curve
            },
            "knowledge_graph_state": {
                "character_states": self.knowledge_graph_state.character_states,
                "relationships": self.knowledge_graph_state.relationships,
                "thematic_threads": self.knowledge_graph_state.thematic_threads,
                "unresolved_plot_threads": self.knowledge_graph_state.unresolved_plot_threads
            },
            "continuity_signals": {
                "active_flags_count": len(self.continuity_signals.active_flags),
                "severity_distribution": self.continuity_signals.severity_distribution
            },
            "writer_preferences": {
                "acceptance_rate": self.writer_preferences.acceptance_rate,
                "confidence_threshold": self.writer_preferences.confidence_threshold,
                "suggestion_type_weights": self.writer_preferences.suggestion_type_weights
            },
            "recent_scenes": self.recent_scenes,
            "trigger": {
                "event": self.trigger.event,
                "metadata": self.trigger.metadata
            },
            "narrative_stage": self.get_narrative_stage(),
            "focus_areas": self.get_focus_areas(),
            "context_completeness": self.context_completeness_score
        }
