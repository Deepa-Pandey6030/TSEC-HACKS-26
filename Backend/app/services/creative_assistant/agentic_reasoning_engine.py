"""
Agentic Reasoning Engine - Core reasoning loop.
Orchestrates the complete OBSERVE → INTERPRET → REASON → PLAN → SUGGEST → REFLECT → ADAPT cycle.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from .models.narrative_context import NarrativeContext
from .models.reasoning_output import ReasoningOutput
from .models.intervention_plan import InterventionPlan
from .observation_synthesizer import ObservationSynthesizer
from .narrative_interpreter import NarrativeInterpreter
from .grok_integration import GrokIntegration
from .intervention_planner import InterventionPlanner

logger = logging.getLogger(__name__)


class AgenticReasoningEngine:
    """
    Main agentic reasoning engine for the Creative AI Assistant.
    
    Implements the complete reasoning cycle:
    1. OBSERVE - Synthesize multi-source inputs
    2. INTERPRET - Understand narrative context
    3. REASON - Apply senior writer judgment (via Grok)
    4. PLAN - Identify intervention points
    5. SUGGEST - Generate actionable suggestions
    6. REFLECT - Learn from feedback
    7. ADAPT - Update preferences
    
    This is the intelligence core of NOLAN.
    """
    
    def __init__(self, grok_api_key: Optional[str] = None):
        """
        Initialize the reasoning engine.
        
        Args:
            grok_api_key: Optional Grok API key (uses config if not provided)
        """
        self.observer = ObservationSynthesizer()
        self.interpreter = NarrativeInterpreter()
        self.grok = GrokIntegration(api_key=grok_api_key)
        self.planner = InterventionPlanner()
        
        logger.info("Agentic Reasoning Engine initialized")
    
    async def run_reasoning_cycle(
        self,
        story_id: str,
        nlp_data: Dict[str, Any],
        knowledge_graph_data: Dict[str, Any],
        continuity_data: Dict[str, Any],
        writer_prefs_data: Dict[str, Any],
        recent_scenes: List[Dict[str, Any]],
        trigger_event: str = "unknown",
        trigger_metadata: Dict[str, Any] = None
    ) -> InterventionPlan:
        """
        Run complete reasoning cycle and return intervention plan.
        
        This is the main entry point for the reasoning engine.
        
        Args:
            story_id: Story identifier
            nlp_data: Data from NLP Extraction Engine
            knowledge_graph_data: Data from Knowledge Graph
            continuity_data: Data from Continuity Validator
            writer_prefs_data: Data from Recall/Query Engine
            recent_scenes: Recent scene content
            trigger_event: What triggered this cycle
            trigger_metadata: Additional trigger context
        
        Returns:
            Complete intervention plan with suggestions
        """
        logger.info(f"Starting reasoning cycle for story: {story_id}")
        cycle_start = datetime.now()
        
        try:
            # STEP 1: OBSERVE - Synthesize context
            logger.info("STEP 1: OBSERVE - Synthesizing context")
            context = await self.observer.synthesize_context(
                story_id=story_id,
                nlp_data=nlp_data,
                knowledge_graph_data=knowledge_graph_data,
                continuity_data=continuity_data,
                writer_prefs_data=writer_prefs_data,
                recent_scenes=recent_scenes,
                trigger_event=trigger_event,
                trigger_metadata=trigger_metadata
            )
            
            # STEP 2: INTERPRET - Understand context
            logger.info("STEP 2: INTERPRET - Interpreting context")
            interpretation = await self.interpreter.interpret_context(context)
            
            # STEP 3: REASON - Apply AI judgment
            logger.info("STEP 3: REASON - Generating AI reasoning via Grok")
            reasoning = await self.grok.generate_narrative_reasoning(
                context_dict=context.to_dict(),
                interpretation=interpretation
            )
            
            # STEP 4: PLAN - Create intervention plan
            logger.info("STEP 4: PLAN - Planning interventions")
            plan = await self.planner.plan_interventions(
                context=context,
                reasoning=reasoning
            )
            
            # STEP 5: SUGGEST - Format suggestions (handled by suggestion_generator)
            # This step is delegated to the suggestion_generator module
            
            # Log cycle completion
            cycle_duration = (datetime.now() - cycle_start).total_seconds()
            logger.info(
                f"Reasoning cycle complete. "
                f"Duration: {cycle_duration:.2f}s, "
                f"Interventions: {len(plan.planned_interventions)}, "
                f"Confidence: {plan.plan_confidence:.2f}"
            )
            
            return plan
            
        except Exception as e:
            logger.error(f"Error in reasoning cycle: {e}", exc_info=True)
            raise
    
    async def process_feedback(
        self,
        story_id: str,
        intervention_id: str,
        feedback: Dict[str, Any]
    ) -> None:
        """
        Process writer feedback on suggestions.
        
        This is the REFLECT step of the reasoning loop.
        
        Args:
            story_id: Story identifier
            intervention_id: Intervention that received feedback
            feedback: Feedback data (accepted, rejected, modified, etc.)
        """
        logger.info(f"Processing feedback for intervention: {intervention_id}")
        
        # STEP 6: REFLECT - Learn from feedback
        # This would update the preference learning system
        # Implementation depends on your database/storage layer
        
        # For now, just log
        logger.info(f"Feedback: {feedback}")
        
        # TODO: Implement preference learning update
        # await self.preference_learner.update_from_feedback(story_id, intervention_id, feedback)
    
    async def adapt_preferences(
        self,
        story_id: str,
        writer_id: str
    ) -> Dict[str, Any]:
        """
        Adapt writer preferences based on historical feedback.
        
        This is the ADAPT step of the reasoning loop.
        
        Args:
            story_id: Story identifier
            writer_id: Writer identifier
        
        Returns:
            Updated preferences
        """
        logger.info(f"Adapting preferences for writer: {writer_id}")
        
        # STEP 7: ADAPT - Update preference model
        # This would analyze historical feedback and update preferences
        # Implementation depends on your database/storage layer
        
        # TODO: Implement preference adaptation
        # return await self.preference_learner.adapt_preferences(story_id, writer_id)
        
        return {}
    
    async def get_reasoning_explanation(
        self,
        plan: InterventionPlan
    ) -> Dict[str, Any]:
        """
        Get detailed explanation of reasoning process.
        
        Useful for debugging and transparency.
        
        Args:
            plan: Intervention plan to explain
        
        Returns:
            Explanation dictionary
        """
        return {
            "story_id": plan.story_id,
            "trigger_event": plan.trigger_event,
            "overall_health": plan.overall_story_health,
            "health_trend": plan.health_trend,
            "confidence": plan.plan_confidence,
            "intervention_count": len(plan.planned_interventions),
            "intervention_breakdown": {
                "critical": len(plan.get_by_priority("critical")),
                "high": len(plan.get_by_priority("high")),
                "medium": len(plan.get_by_priority("medium")),
                "low": len(plan.get_by_priority("low"))
            },
            "rationale": {
                "why_these": plan.why_these_interventions,
                "why_not_others": plan.why_not_others
            },
            "created_at": plan.plan_created_at
        }
