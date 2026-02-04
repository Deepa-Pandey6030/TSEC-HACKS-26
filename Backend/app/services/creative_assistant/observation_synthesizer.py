"""
Observation Synthesizer - Multi-source input aggregation.
OBSERVE step in the agentic reasoning loop.
"""

from typing import Dict, Any, List
import logging
from datetime import datetime

from .models.narrative_context import (
    NarrativeContext,
    StoryProgress,
    NLPSignals,
    KnowledgeGraphState,
    ContinuitySignals,
    WriterPreferences,
    TriggerContext,
)

logger = logging.getLogger(__name__)


class ObservationSynthesizer:
    """
    Synthesizes observations from multiple data sources into unified context.
    
    This is the OBSERVE step of the agentic reasoning loop.
    """
    
    def __init__(self):
        logger.info("Observation Synthesizer initialized")
    
    async def synthesize_context(
        self,
        story_id: str,
        nlp_data: Dict[str, Any],
        knowledge_graph_data: Dict[str, Any],
        continuity_data: Dict[str, Any],
        writer_prefs_data: Dict[str, Any],
        recent_scenes: List[Dict[str, Any]],
        trigger_event: str = "unknown",
        trigger_metadata: Dict[str, Any] = None
    ) -> NarrativeContext:
        """
        Synthesize all inputs into a unified NarrativeContext.
        
        Args:
            story_id: Story identifier
            nlp_data: Data from NLP Extraction Engine
            knowledge_graph_data: Data from Knowledge Graph
            continuity_data: Data from Continuity Validator
            writer_prefs_data: Data from Recall/Query Engine
            recent_scenes: Recent scene content
            trigger_event: What triggered this reasoning cycle
            trigger_metadata: Additional trigger context
        
        Returns:
            Complete NarrativeContext object
        """
        logger.info(f"Synthesizing context for story: {story_id}")
        
        try:
            # Parse story progress
            story_progress = self._parse_story_progress(story_id, knowledge_graph_data)
            
            # Parse NLP signals
            nlp_signals = self._parse_nlp_signals(nlp_data)
            
            # Parse knowledge graph state
            kg_state = self._parse_knowledge_graph(knowledge_graph_data)
            
            # Parse continuity signals
            continuity_signals = self._parse_continuity(continuity_data)
            
            # Parse writer preferences
            writer_prefs = self._parse_writer_preferences(writer_prefs_data)
            
            # Create trigger context
            trigger = TriggerContext(
                event=trigger_event,
                metadata=trigger_metadata or {},
                urgency=self._assess_urgency(continuity_data, nlp_data)
            )
            
            # Build complete context
            context = NarrativeContext(
                story_progress=story_progress,
                nlp_signals=nlp_signals,
                knowledge_graph_state=kg_state,
                continuity_signals=continuity_signals,
                writer_preferences=writer_prefs,
                recent_scenes=recent_scenes,
                trigger=trigger,
                analyzed_at=datetime.now()
            )
            
            # Compute completeness score
            context.compute_completeness()
            
            logger.info(
                f"Context synthesized. Completeness: {context.context_completeness_score:.2f}, "
                f"Focus areas: {context.get_focus_areas()}"
            )
            
            return context
            
        except Exception as e:
            logger.error(f"Error synthesizing context: {e}", exc_info=True)
            raise
    
    def _parse_story_progress(self, story_id: str, kg_data: Dict[str, Any]) -> StoryProgress:
        """Parse story progress from knowledge graph data."""
        metadata = kg_data.get("story_metadata", {})
        
        return StoryProgress(
            story_id=story_id,
            title=metadata.get("title", "Untitled"),
            genre=metadata.get("genre", "Unknown"),
            subgenre=metadata.get("subgenre"),
            current_act=metadata.get("current_act", 1),
            total_acts=metadata.get("total_acts", 3),
            current_scene_id=metadata.get("current_scene_id"),
            completion_percentage=metadata.get("completion_percentage", 0.0),
            word_count=metadata.get("word_count", 0),
            target_word_count=metadata.get("target_word_count", 80000),
            scenes_written=metadata.get("scenes_written", 0),
            author_id=metadata.get("author_id", ""),
            created_at=metadata.get("created_at"),
            last_updated=metadata.get("last_updated")
        )
    
    def _parse_nlp_signals(self, nlp_data: Dict[str, Any]) -> NLPSignals:
        """Parse NLP signals from NLP Extraction Engine."""
        from .models.narrative_context import PacingTrend, EmotionalDirection
        
        return NLPSignals(
            recent_scenes_analysis=nlp_data.get("recent_scenes_analysis", []),
            pacing_trend=PacingTrend(nlp_data.get("pacing_trend", "steady")),
            pacing_velocity=nlp_data.get("pacing_velocity", 0.0),
            emotional_arc=nlp_data.get("emotional_arc", {}),
            emotional_direction=EmotionalDirection(nlp_data.get("emotional_direction", "stable")),
            emotional_intensity=nlp_data.get("emotional_intensity", 0.5),
            voice_consistency=nlp_data.get("voice_consistency", {}),
            dialogue_density_trend=nlp_data.get("dialogue_density_trend", "stable"),
            tension_curve=nlp_data.get("tension_curve", []),
            tension_average=nlp_data.get("tension_average", 0.5),
            tension_variance=nlp_data.get("tension_variance", 0.0),
            avg_sentence_length_trend=nlp_data.get("avg_sentence_length_trend", []),
            vocabulary_complexity_trend=nlp_data.get("vocabulary_complexity_trend", [])
        )
    
    def _parse_knowledge_graph(self, kg_data: Dict[str, Any]) -> KnowledgeGraphState:
        """Parse knowledge graph state."""
        return KnowledgeGraphState(
            character_states=kg_data.get("character_states", {}),
            character_count=kg_data.get("character_count", 0),
            characters_with_recent_development=kg_data.get("characters_with_recent_development", []),
            characters_stagnant=kg_data.get("characters_stagnant", []),
            relationships=kg_data.get("relationships", []),
            relationship_changes_recent=kg_data.get("relationship_changes_recent", []),
            recent_events=kg_data.get("recent_events", []),
            event_causality_chains=kg_data.get("event_causality_chains", []),
            thematic_threads=kg_data.get("thematic_threads", []),
            theme_manifestation_count=kg_data.get("theme_manifestation_count", {}),
            themes_underutilized=kg_data.get("themes_underutilized", []),
            unresolved_plot_threads=kg_data.get("unresolved_plot_threads", []),
            plot_threads_aging=kg_data.get("plot_threads_aging", []),
            locations_used=kg_data.get("locations_used", []),
            world_state_changes=kg_data.get("world_state_changes", [])
        )
    
    def _parse_continuity(self, continuity_data: Dict[str, Any]) -> ContinuitySignals:
        """Parse continuity signals."""
        return ContinuitySignals(
            active_flags=continuity_data.get("active_flags", []),
            severity_distribution=continuity_data.get("severity_distribution", {}),
            categories_affected=continuity_data.get("categories_affected", []),
            category_distribution=continuity_data.get("category_distribution", {}),
            potentially_intentional=continuity_data.get("potentially_intentional", []),
            confirmed_errors=continuity_data.get("confirmed_errors", []),
            flags_increasing=continuity_data.get("flags_increasing", False),
            flags_resolved_recently=continuity_data.get("flags_resolved_recently", 0)
        )
    
    def _parse_writer_preferences(self, prefs_data: Dict[str, Any]) -> WriterPreferences:
        """Parse writer preferences."""
        return WriterPreferences(
            suggestion_type_weights=prefs_data.get("suggestion_type_weights", {}),
            confidence_threshold=prefs_data.get("confidence_threshold", 0.7),
            max_suggestions_per_session=prefs_data.get("max_suggestions_per_session", 5),
            acceptance_rate=prefs_data.get("acceptance_rate", 0.0),
            acceptance_by_type=prefs_data.get("acceptance_by_type", {}),
            rejection_reasons=prefs_data.get("rejection_reasons", {}),
            tone_preferences=prefs_data.get("tone_preferences", {}),
            structural_preferences=prefs_data.get("structural_preferences", {}),
            character_focus=prefs_data.get("character_focus", {}),
            prefers_questions_over_suggestions=prefs_data.get("prefers_questions_over_suggestions", False),
            detail_level=prefs_data.get("detail_level", "moderate"),
            total_suggestions_received=prefs_data.get("total_suggestions_received", 0),
            total_suggestions_accepted=prefs_data.get("total_suggestions_accepted", 0),
            total_suggestions_rejected=prefs_data.get("total_suggestions_rejected", 0),
            recent_decisions=prefs_data.get("recent_decisions", []),
            preference_confidence=prefs_data.get("preference_confidence", 0.5),
            last_updated=prefs_data.get("last_updated")
        )
    
    def _assess_urgency(self, continuity_data: Dict[str, Any], nlp_data: Dict[str, Any]) -> str:
        """Assess urgency based on signals."""
        # Critical continuity issues
        severity_dist = continuity_data.get("severity_distribution", {})
        if severity_dist.get("critical", 0) > 0:
            return "critical"
        
        # Major pacing issues
        pacing_trend = nlp_data.get("pacing_trend", "steady")
        if pacing_trend == "stalling":
            return "high"
        
        # Multiple major issues
        if severity_dist.get("major", 0) > 3:
            return "high"
        
        return "normal"
