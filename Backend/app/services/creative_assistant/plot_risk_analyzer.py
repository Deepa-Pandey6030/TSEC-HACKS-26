"""
Predictive Plot Risk Analyzer
Senior Plot Analyst with 30+ years of narrative structure expertise

Predicts downstream narrative risks before they occur.
"""

from typing import Dict, Any, List, Optional
import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# System prompt with 30+ years plot analysis experience
PLOT_ANALYST_SYSTEM_PROMPT = """ROLE & IDENTITY

You are a Senior Plot Analyst with 30+ years of experience analyzing narrative structures across:
- Feature films and television
- Literary fiction and genre fiction
- Stage plays and screenplays
- Interactive narratives and games

You have analyzed over 10,000 stories and can predict narrative failures before they occur.

PRIMARY OBJECTIVE

Analyze the current script/scene and predict future narrative risks with quantifiable metrics.
You must identify problems that will emerge in later acts, not just current issues.

ANALYSIS FRAMEWORK

You use a proven 4-stage predictive model:

1. STRUCTURAL EXTRACTION
   - Identify acts (implicit or explicit)
   - Map key reveals and their timing
   - Track character arc trajectories
   - Detect tension peaks and valleys

2. NARRATIVE SIGNAL SCORING
   - Tension Delta: Change in dramatic tension
   - Information Density: Reveal concentration
   - Emotional Variance: Emotional range and volatility
   - Arc Dependency: Character interconnectedness

3. PREDICTIVE PROJECTION
   - Model tension decay from early reveals
   - Predict arc collapse from weak setup
   - Forecast pacing fatigue from poor rhythm
   - Estimate climax impact reduction

4. RISK QUANTIFICATION
   - Continuity Conflict Risk (0-1)
   - Arc Collapse Probability (0-1)
   - Pacing Fatigue Risk (0-1)
   - Reveal Timing Penalty (0-1)

OUTPUT REQUIREMENTS

Return ONLY a valid JSON object with this exact structure:
{
  "predictive_summary": "Specific impact prediction with numbers",
  "risk_scores": {
    "continuity_conflict": 0.0-1.0,
    "arc_collapse": 0.0-1.0,
    "pacing_fatigue": 0.0-1.0,
    "reveal_timing_penalty": 0.0-1.0
  },
  "primary_risk": "Most critical issue identified",
  "recommended_action": "Specific, actionable fix",
  "confidence_level": 0.0-1.0,
  "affected_scenes": ["scene_id_1", "scene_id_2"],
  "tension_curve": [0.3, 0.5, 0.7, 0.6, 0.9],
  "risk_breakdown": {
    "continuity_conflict": {"reason": "Why this is a risk", "severity": 0.0-1.0},
    "arc_collapse": {"reason": "Why this is a risk", "severity": 0.0-1.0},
    "pacing_fatigue": {"reason": "Why this is a risk", "severity": 0.0-1.0},
    "reveal_timing_penalty": {"reason": "Why this is a risk", "severity": 0.0-1.0}
  }
}

CRITICAL RULES

✓ Every insight must have a number
✓ Be predictive, not reactive
✓ Provide specific cause → effect chains
✓ Give actionable recommendations
✓ Be honest about confidence levels
✗ No vague language
✗ No generic advice
✗ No assumptions without evidence

EXPERTISE LEVEL

With 30+ years of experience, you:
- Recognize patterns across 10,000+ stories
- Predict Act 3 problems from Act 1 setup
- Identify subtle tension decay curves
- Spot premature reveals instantly
- Understand genre-specific pacing requirements
- Know when to break rules effectively"""


@dataclass
class RiskScore:
    """Individual risk score with explanation."""
    score: float  # 0-1
    reason: str
    severity: float  # 0-1


class PlotRiskAnalyzer:
    """
    Predictive Plot Risk Analyzer with 30+ years expertise.
    
    Analyzes narrative structure and predicts future risks.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the analyzer."""
        from openai import OpenAI
        from app.config import settings
        
        api_key = api_key or settings.xai_api_key
        
        # Use same API detection as FlowEngine
        if api_key.startswith("gsk_"):
            self.provider = "groq"
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self.model = "llama-3.3-70b-versatile"
        elif api_key.startswith("xai-"):
            self.provider = "grok"
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.x.ai/v1"
            )
            self.model = "grok-beta"
        else:
            self.provider = "groq"
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self.model = "llama-3.3-70b-versatile"
        
        logger.info(f"Plot Risk Analyzer initialized: {self.provider} - {self.model}")
    
    async def analyze_plot_risks(
        self,
        content: str,
        story_title: str = "Untitled",
        genre: str = "General",
        completion_percentage: float = 50.0
    ) -> Dict[str, Any]:
        """
        Analyze plot and predict future narrative risks.
        
        Args:
            content: Script or scene content to analyze
            story_title: Title of the story
            genre: Genre of the story
            completion_percentage: How much of the story is complete (0-100)
        
        Returns:
            Dictionary with predictive risk analysis
        """
        logger.info(f"Analyzing plot risks for: {story_title} ({genre}, {completion_percentage}% complete)")
        
        # Build analysis prompt
        user_prompt = f"""STORY CONTEXT
Title: {story_title}
Genre: {genre}
Completion: {completion_percentage}%

CONTENT TO ANALYZE:
{content[:8000]}  # Limit to prevent token overflow

TASK:
Analyze this content and predict future narrative risks.
Focus on problems that will emerge in later acts.

Return a JSON object with your predictive analysis following the exact structure specified in your system prompt."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": PLOT_ANALYST_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6,  # Balanced for analytical consistency
                max_tokens=2000
            )
            
            content_response = response.choices[0].message.content.strip()
            
            # Parse JSON response
            import json
            analysis = self._parse_json_response(content_response)
            
            # Add metadata
            analysis["_metadata"] = {
                "model": self.model,
                "provider": self.provider,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
                "story_title": story_title,
                "genre": genre,
                "completion_percentage": completion_percentage
            }
            
            logger.info(f"Plot analysis complete. Primary risk: {analysis.get('primary_risk', 'Unknown')}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in plot risk analysis: {e}", exc_info=True)
            return self._create_fallback_analysis()
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON from AI response, handling common formatting issues."""
        import json
        
        # Try direct parse
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # Try extracting from markdown code blocks
        if "```json" in content:
            try:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
                return json.loads(json_str)
            except:
                pass
        
        # Try extracting from code blocks without language
        if "```" in content:
            try:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
                return json.loads(json_str)
            except:
                pass
        
        # Last resort: look for {...} pattern
        try:
            first_brace = content.find("{")
            last_brace = content.rfind("}") + 1
            if first_brace != -1 and last_brace > first_brace:
                json_str = content[first_brace:last_brace]
                return json.loads(json_str)
        except:
            pass
        
        logger.error("Could not parse JSON from plot analysis response")
        raise ValueError(f"Invalid JSON response: {content[:500]}")
    
    def _create_fallback_analysis(self) -> Dict[str, Any]:
        """Create fallback analysis on error."""
        return {
            "predictive_summary": "Unable to complete predictive analysis at this time. Please try again.",
            "risk_scores": {
                "continuity_conflict": 0.0,
                "arc_collapse": 0.0,
                "pacing_fatigue": 0.0,
                "reveal_timing_penalty": 0.0
            },
            "primary_risk": "Analysis unavailable",
            "recommended_action": "Retry analysis or check content length",
            "confidence_level": 0.0,
            "affected_scenes": [],
            "tension_curve": [0.5, 0.5, 0.5, 0.5, 0.5],
            "risk_breakdown": {
                "continuity_conflict": {"reason": "Analysis error", "severity": 0.0},
                "arc_collapse": {"reason": "Analysis error", "severity": 0.0},
                "pacing_fatigue": {"reason": "Analysis error", "severity": 0.0},
                "reveal_timing_penalty": {"reason": "Analysis error", "severity": 0.0}
            }
        }
