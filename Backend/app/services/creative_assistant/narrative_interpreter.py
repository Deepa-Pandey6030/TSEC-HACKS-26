"""
Narrative Interpreter - Context understanding and analysis.
INTERPRET step in the agentic reasoning loop.
"""

from typing import Dict, Any
import logging

from .models.narrative_context import NarrativeContext

logger = logging.getLogger(__name__)


class NarrativeInterpreter:
    """
    Interprets narrative context to extract high-level insights.
    
    This is the INTERPRET step of the agentic reasoning loop.
    """
    
    def __init__(self):
        logger.info("Narrative Interpreter initialized")
    
    async def interpret_context(self, context: NarrativeContext) -> Dict[str, Any]:
        """
        Interpret narrative context to extract actionable insights.
        
        Args:
            context: Complete narrative context
        
        Returns:
            Dictionary of interpreted insights
        """
        logger.info(f"Interpreting context for story: {context.story_progress.story_id}")
        
        interpretation = {
            "narrative_stage": context.get_narrative_stage(),
            "focus_areas": context.get_focus_areas(),
            "urgency_level": context.trigger.urgency,
            "context_quality": self._assess_context_quality(context),
            "story_momentum": self._assess_momentum(context),
            "character_health": self._assess_character_health(context),
            "thematic_presence": self._assess_thematic_presence(context),
            "continuity_status": self._assess_continuity(context),
            "writer_engagement": self._assess_writer_engagement(context),
            "key_insights": self._extract_key_insights(context)
        }
        
        logger.info(f"Interpretation complete. Key insights: {len(interpretation['key_insights'])}")
        
        return interpretation
    
    def _assess_context_quality(self, context: NarrativeContext) -> str:
        """Assess quality of available context data."""
        score = context.context_completeness_score
        
        if score >= 0.8:
            return "excellent"
        elif score >= 0.6:
            return "good"
        elif score >= 0.4:
            return "moderate"
        else:
            return "limited"
    
    def _assess_momentum(self, context: NarrativeContext) -> str:
        """Assess narrative momentum."""
        from .models.narrative_context import PacingTrend
        
        pacing = context.nlp_signals.pacing_trend
        
        if pacing == PacingTrend.STALLING:
            return "stalling"
        elif pacing == PacingTrend.ACCELERATING:
            return "accelerating"
        elif pacing == PacingTrend.DECELERATING:
            return "decelerating"
        else:
            return "steady"
    
    def _assess_character_health(self, context: NarrativeContext) -> str:
        """Assess character development health."""
        kg = context.knowledge_graph_state
        
        if not kg.character_states:
            return "no_data"
        
        total_chars = kg.character_count
        stagnant_chars = len(kg.characters_stagnant)
        
        if total_chars == 0:
            return "no_characters"
        
        stagnant_ratio = stagnant_chars / total_chars
        
        if stagnant_ratio > 0.5:
            return "concerning"
        elif stagnant_ratio > 0.3:
            return "needs_attention"
        else:
            return "healthy"
    
    def _assess_thematic_presence(self, context: NarrativeContext) -> str:
        """Assess thematic development."""
        kg = context.knowledge_graph_state
        
        theme_count = len(kg.thematic_threads)
        underutilized = len(kg.themes_underutilized)
        
        if theme_count == 0:
            return "absent"
        elif underutilized > theme_count / 2:
            return "weak"
        elif theme_count >= 2:
            return "strong"
        else:
            return "moderate"
    
    def _assess_continuity(self, context: NarrativeContext) -> str:
        """Assess continuity health."""
        cont = context.continuity_signals
        
        critical = cont.severity_distribution.get("critical", 0)
        major = cont.severity_distribution.get("major", 0)
        
        if critical > 0:
            return "critical_issues"
        elif major > 5:
            return "major_issues"
        elif len(cont.active_flags) > 10:
            return "minor_issues"
        else:
            return "clean"
    
    def _assess_writer_engagement(self, context: NarrativeContext) -> str:
        """Assess writer engagement with suggestions."""
        prefs = context.writer_preferences
        
        if prefs.total_suggestions_received == 0:
            return "new_writer"
        
        acceptance_rate = prefs.acceptance_rate
        
        if acceptance_rate > 0.7:
            return "highly_engaged"
        elif acceptance_rate > 0.4:
            return "moderately_engaged"
        else:
            return "low_engagement"
    
    def _extract_key_insights(self, context: NarrativeContext) -> list:
        """Extract key insights from context."""
        insights = []
        
        # Pacing insights
        if context.nlp_signals.pacing_trend.value == "stalling":
            insights.append("Pacing has stalled - story momentum needs attention")
        
        # Character insights
        if context.knowledge_graph_state.characters_stagnant:
            insights.append(f"{len(context.knowledge_graph_state.characters_stagnant)} characters showing no development")
        
        # Thematic insights
        if len(context.knowledge_graph_state.thematic_threads) < 2:
            insights.append("Limited thematic development - consider reinforcing themes")
        
        # Continuity insights
        critical_flags = context.continuity_signals.severity_distribution.get("critical", 0)
        if critical_flags > 0:
            insights.append(f"{critical_flags} critical continuity issues require immediate attention")
        
        # Plot insights
        if len(context.knowledge_graph_state.unresolved_plot_threads) > 10:
            insights.append("High number of unresolved plot threads - consider resolution strategy")
        
        # Relationship insights
        if not context.knowledge_graph_state.relationship_changes_recent:
            insights.append("No recent relationship development - characters may feel static")
        
        return insights
