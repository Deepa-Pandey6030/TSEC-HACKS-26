"""
Intervention Planner - Decision logic for creative interventions.
PLAN step in the agentic reasoning loop.
"""

from typing import List
import logging

from .models.reasoning_output import ReasoningOutput
from .models.intervention_plan import (
    InterventionPlan,
    PlannedIntervention,
    InterventionType,
    InterventionPriority,
)
from .models.narrative_context import NarrativeContext

logger = logging.getLogger(__name__)


class InterventionPlanner:
    """
    Plans interventions based on AI reasoning output.
    
    This is the PLAN step of the agentic reasoning loop.
    """
    
    def __init__(self):
        logger.info("Intervention Planner initialized")
    
    async def plan_interventions(
        self,
        context: NarrativeContext,
        reasoning: ReasoningOutput
    ) -> InterventionPlan:
        """
        Plan interventions based on reasoning output.
        
        Args:
            context: Narrative context
            reasoning: AI reasoning output
        
        Returns:
            Complete intervention plan
        """
        logger.info(f"Planning interventions for story: {context.story_progress.story_id}")
        
        interventions = []
        
        # Plan based on momentum assessment
        interventions.extend(self._plan_momentum_interventions(reasoning))
        
        # Plan based on character arcs
        interventions.extend(self._plan_character_interventions(reasoning))
        
        # Plan based on structural concerns
        interventions.extend(self._plan_structural_interventions(reasoning))
        
        # Plan based on thematic health
        interventions.extend(self._plan_thematic_interventions(reasoning))
        
        # Plan based on opportunities
        interventions.extend(self._plan_opportunity_interventions(reasoning))
        
        # Plan clarifying questions
        interventions.extend(self._plan_question_interventions(reasoning))
        
        # Sort by priority
        interventions.sort(key=lambda x: self._priority_score(x.priority), reverse=True)
        
        # Limit based on writer preferences
        max_suggestions = context.writer_preferences.max_suggestions_per_session
        interventions = interventions[:max_suggestions]
        
        # Create plan
        plan = InterventionPlan(
            story_id=context.story_progress.story_id,
            trigger_event=context.trigger.event,
            planned_interventions=interventions,
            why_these_interventions=self._explain_selection(interventions),
            why_not_others=self._explain_exclusions(len(interventions), max_suggestions),
            overall_story_health=reasoning.overall_story_health,
            plan_confidence=reasoning.reasoning_confidence
        )
        
        logger.info(f"Planned {len(interventions)} interventions")
        
        return plan
    
    def _plan_momentum_interventions(self, reasoning: ReasoningOutput) -> List[PlannedIntervention]:
        """Plan interventions for momentum issues."""
        from .models.reasoning_output import MomentumStatus
        
        interventions = []
        momentum = reasoning.momentum_assessment
        
        if momentum.status == MomentumStatus.STALLING:
            interventions.append(PlannedIntervention(
                intervention_type=InterventionType.PACING_ADJUSTMENT,
                priority=InterventionPriority.HIGH,
                confidence=0.8,
                what="Address stalling narrative momentum",
                why=momentum.senior_writer_intuition,
                expected_impact="Restore forward momentum and reader engagement",
                impact_areas=["pacing", "engagement"]
            ))
        
        elif momentum.status == MomentumStatus.RUSHING:
            interventions.append(PlannedIntervention(
                intervention_type=InterventionType.PACING_ADJUSTMENT,
                priority=InterventionPriority.MEDIUM,
                confidence=0.7,
                what="Slow down pacing to allow emotional beats",
                why="Story is rushing through important moments",
                expected_impact="Better emotional resonance and character development",
                impact_areas=["pacing", "emotional_depth"]
            ))
        
        return interventions
    
    def _plan_character_interventions(self, reasoning: ReasoningOutput) -> List[PlannedIntervention]:
        """Plan interventions for character development."""
        interventions = []
        char_assessment = reasoning.character_arc_assessment
        
        for transformation in char_assessment.transformations_needing_attention:
            priority = self._map_severity_to_priority(transformation.severity)
            
            interventions.append(PlannedIntervention(
                intervention_type=InterventionType.CHARACTER_MOMENT,
                priority=priority,
                confidence=0.75,
                what=transformation.suggestion,
                why=transformation.issue,
                expected_impact=f"Develop {transformation.character}'s arc",
                impact_areas=["character_development"],
                related_characters=[transformation.character]
            ))
        
        return interventions
    
    def _plan_structural_interventions(self, reasoning: ReasoningOutput) -> List[PlannedIntervention]:
        """Plan interventions for structural concerns."""
        interventions = []
        
        for concern in reasoning.structural_concerns:
            priority = self._map_severity_to_priority(concern.severity)
            
            interventions.append(PlannedIntervention(
                intervention_type=InterventionType.STRUCTURAL_ADJUSTMENT,
                priority=priority,
                confidence=0.7,
                what=concern.recommendation or "Address structural issue",
                why=concern.concern,
                expected_impact="Improve story structure and coherence",
                impact_areas=["structure"],
                related_scenes=concern.affected_scenes
            ))
        
        return interventions
    
    def _plan_thematic_interventions(self, reasoning: ReasoningOutput) -> List[PlannedIntervention]:
        """Plan interventions for thematic development."""
        from .models.reasoning_output import ReinforcementQuality
        
        interventions = []
        thematic = reasoning.thematic_health
        
        if thematic.reinforcement_quality in [ReinforcementQuality.WEAK, ReinforcementQuality.ABSENT]:
            interventions.append(PlannedIntervention(
                intervention_type=InterventionType.THEMATIC_REINFORCEMENT,
                priority=InterventionPriority.MEDIUM,
                confidence=0.7,
                what="Strengthen thematic reinforcement",
                why=thematic.notes,
                expected_impact="Deeper thematic resonance and meaning",
                impact_areas=["themes"],
                related_themes=thematic.themes_present
            ))
        
        return interventions
    
    def _plan_opportunity_interventions(self, reasoning: ReasoningOutput) -> List[PlannedIntervention]:
        """Plan interventions based on identified opportunities."""
        interventions = []
        
        for opp in reasoning.opportunities:
            if opp.confidence < 0.6:
                continue  # Skip low-confidence opportunities
            
            interventions.append(PlannedIntervention(
                intervention_type=self._map_opportunity_type(opp.type),
                priority=self._assess_opportunity_priority(opp),
                confidence=opp.confidence,
                what=opp.specific_suggestion or opp.rationale,
                why=opp.why,
                expected_impact=opp.expected_impact or "Enhance narrative quality",
                impact_areas=[opp.type],
                related_scenes=opp.related_scenes,
                related_characters=opp.related_characters,
                related_themes=opp.related_themes,
                alternatives=opp.alternatives
            ))
        
        return interventions
    
    def _plan_question_interventions(self, reasoning: ReasoningOutput) -> List[PlannedIntervention]:
        """Plan clarifying questions as interventions."""
        interventions = []
        
        for question in reasoning.questions_for_writer[:3]:  # Limit to 3 questions
            interventions.append(PlannedIntervention(
                intervention_type=InterventionType.CLARIFYING_QUESTION,
                priority=InterventionPriority.LOW,
                confidence=0.8,
                what=question,
                why="Clarification needed for better guidance",
                expected_impact="Better understanding of writer's intent",
                impact_areas=["clarity"]
            ))
        
        return interventions
    
    def _map_severity_to_priority(self, severity: str) -> InterventionPriority:
        """Map severity to intervention priority."""
        mapping = {
            "critical": InterventionPriority.CRITICAL,
            "major": InterventionPriority.HIGH,
            "moderate": InterventionPriority.MEDIUM,
            "minor": InterventionPriority.LOW
        }
        return mapping.get(severity, InterventionPriority.MEDIUM)
    
    def _map_opportunity_type(self, opp_type: str) -> InterventionType:
        """Map opportunity type to intervention type."""
        mapping = {
            "scene_addition": InterventionType.SCENE_ADDITION,
            "character_moment": InterventionType.CHARACTER_MOMENT,
            "thematic_echo": InterventionType.THEMATIC_REINFORCEMENT,
            "dialogue_adjustment": InterventionType.DIALOGUE_ADJUSTMENT,
            "relationship_development": InterventionType.RELATIONSHIP_DEVELOPMENT,
        }
        return mapping.get(opp_type, InterventionType.STRUCTURAL_ADJUSTMENT)
    
    def _assess_opportunity_priority(self, opportunity) -> InterventionPriority:
        """Assess priority of an opportunity."""
        if opportunity.confidence >= 0.9:
            return InterventionPriority.HIGH
        elif opportunity.confidence >= 0.7:
            return InterventionPriority.MEDIUM
        else:
            return InterventionPriority.LOW
    
    def _priority_score(self, priority: InterventionPriority) -> int:
        """Convert priority to numeric score for sorting."""
        scores = {
            InterventionPriority.CRITICAL: 4,
            InterventionPriority.HIGH: 3,
            InterventionPriority.MEDIUM: 2,
            InterventionPriority.LOW: 1
        }
        return scores.get(priority, 0)
    
    def _explain_selection(self, interventions: List[PlannedIntervention]) -> str:
        """Explain why these interventions were selected."""
        if not interventions:
            return "No interventions needed at this time."
        
        priority_counts = {}
        for intervention in interventions:
            priority_counts[intervention.priority.value] = priority_counts.get(intervention.priority.value, 0) + 1
        
        return f"Selected {len(interventions)} interventions based on story health assessment and writer preferences. Priority distribution: {priority_counts}"
    
    def _explain_exclusions(self, selected: int, max_allowed: int) -> str:
        """Explain why some interventions were excluded."""
        if selected < max_allowed:
            return "All high-priority interventions included."
        else:
            return f"Limited to {max_allowed} suggestions per writer preferences. Lower-priority items deferred."
