"""
Reasoning prompt templates for narrative analysis.
Builds dynamic prompts from context and interpretation.
"""

from typing import Dict, Any
import json


def build_narrative_reasoning_prompt(
    context_dict: Dict[str, Any],
    interpretation: Dict[str, Any]
) -> str:
    """
    Build the user prompt for narrative reasoning.
    
    Args:
        context_dict: Narrative context as dictionary
        interpretation: Pre-interpreted context insights
    
    Returns:
        Formatted prompt string
    """
    
    prompt = f"""# Narrative Analysis Request

## Story Overview

**Title:** {context_dict.get('story_progress', {}).get('title', 'Unknown')}
**Genre:** {context_dict.get('story_progress', {}).get('genre', 'Unknown')}
**Progress:** {context_dict.get('story_progress', {}).get('completion_percentage', 0):.1f}% complete
**Word Count:** {context_dict.get('story_progress', {}).get('word_count', 0):,} / {context_dict.get('story_progress', {}).get('target_word_count', 0):,}
**Current Act:** {context_dict.get('story_progress', {}).get('current_act', 1)} of {context_dict.get('story_progress', {}).get('total_acts', 3)}
**Narrative Stage:** {context_dict.get('narrative_stage', 'unknown')}

## Trigger Event

**Event:** {context_dict.get('trigger', {}).get('event', 'unknown')}
**Urgency:** {context_dict.get('trigger', {}).get('urgency', 'normal')}

## Context Interpretation

{_format_interpretation(interpretation)}

## Detailed Context Data

### NLP Signals (Tone, Pacing, Voice)

**Pacing Trend:** {context_dict.get('nlp_signals', {}).get('pacing_trend', 'unknown')}
**Emotional Arc:** {json.dumps(context_dict.get('nlp_signals', {}).get('emotional_arc', {}), indent=2)}
**Voice Consistency:** {json.dumps(context_dict.get('nlp_signals', {}).get('voice_consistency', {}), indent=2)}
**Tension Curve:** {context_dict.get('nlp_signals', {}).get('tension_curve', [])}

### Knowledge Graph State (Characters, Relationships, Themes)

**Character States:** {len(context_dict.get('knowledge_graph_state', {}).get('character_states', {}))} characters tracked
**Stagnant Characters:** {context_dict.get('knowledge_graph_state', {}).get('characters_stagnant', [])}
**Active Relationships:** {len(context_dict.get('knowledge_graph_state', {}).get('relationships', []))}
**Recent Relationship Changes:** {len(context_dict.get('knowledge_graph_state', {}).get('relationship_changes_recent', []))}
**Thematic Threads:** {[t.get('name', 'unknown') for t in context_dict.get('knowledge_graph_state', {}).get('thematic_threads', [])]}
**Underutilized Themes:** {context_dict.get('knowledge_graph_state', {}).get('themes_underutilized', [])}
**Unresolved Plot Threads:** {len(context_dict.get('knowledge_graph_state', {}).get('unresolved_plot_threads', []))} threads

### Continuity Signals (Flags, Inconsistencies)

**Active Flags:** {context_dict.get('continuity_signals', {}).get('active_flags_count', 0)}
**Severity Distribution:** {json.dumps(context_dict.get('continuity_signals', {}).get('severity_distribution', {}), indent=2)}

### Writer Preferences (Learning Data)

**Acceptance Rate:** {context_dict.get('writer_preferences', {}).get('acceptance_rate', 0):.1%}
**Confidence Threshold:** {context_dict.get('writer_preferences', {}).get('confidence_threshold', 0.7)}
**Suggestion Type Weights:** {json.dumps(context_dict.get('writer_preferences', {}).get('suggestion_type_weights', {}), indent=2)}

### Recent Scenes

{_format_recent_scenes(context_dict.get('recent_scenes', []))}

## Focus Areas Identified

{_format_focus_areas(context_dict.get('focus_areas', []))}

## Your Task

As a Senior Writer, analyze this narrative context and provide your creative judgment. Consider:

1. **What is the current story health?** (momentum, character arcs, emotional trajectory, themes)
2. **What opportunities exist?** (scenes to add, character moments, thematic echoes)
3. **What concerns need attention?** (pacing issues, stagnant characters, weak themes)
4. **What questions should the writer consider?** (plot forks, character motivations, thematic choices)

**CRITICAL:** Respond with valid JSON matching this exact structure:

```json
{{
  "momentum_assessment": {{
    "status": "healthy|stalling|rushing|unstable",
    "evidence": "specific evidence from the data",
    "senior_writer_intuition": "your professional judgment",
    "specific_concerns": ["concern 1", "concern 2"],
    "pacing_score": 0.0-1.0
  }},
  "character_arc_assessment": {{
    "characters_at_risk": ["character names"],
    "transformations_needing_attention": [
      {{
        "character": "name",
        "issue": "what's wrong",
        "suggestion": "what to do",
        "severity": "minor|moderate|major"
      }}
    ],
    "reasoning": "your analysis",
    "character_specific_notes": {{"character": "note"}},
    "overall_arc_health": "excellent|good|needs_work|problematic"
  }},
  "emotional_trajectory": {{
    "current_state": "description",
    "trend": "building|plateauing|dissipating|volatile",
    "notes": "your analysis",
    "next_beats_needed": ["beat 1", "beat 2"],
    "emotional_coherence_score": 0.0-1.0
  }},
  "structural_concerns": [
    {{
      "concern": "description",
      "severity": "minor|moderate|major|critical",
      "affected_scenes": ["scene ids"],
      "recommendation": "what to do"
    }}
  ],
  "thematic_health": {{
    "themes_present": ["theme 1", "theme 2"],
    "reinforcement_quality": "strong|moderate|weak|absent",
    "notes": "your analysis",
    "missed_opportunities": ["opportunity 1"],
    "thematic_coherence_score": 0.0-1.0
  }},
  "opportunities": [
    {{
      "type": "scene_addition|character_moment|thematic_echo|etc",
      "confidence": 0.0-1.0,
      "rationale": "why this exists",
      "would_a_senior_writer_consider_this": "yes|no|maybe",
      "why": "detailed reasoning",
      "specific_suggestion": "concrete suggestion",
      "expected_impact": "what this would achieve",
      "related_scenes": ["scene ids"],
      "related_characters": ["names"],
      "related_themes": ["themes"]
    }}
  ],
  "questions_for_writer": [
    "Question 1?",
    "Question 2?"
  ],
  "overall_story_health": "excellent|good|needs_attention|critical",
  "overall_health_reasoning": "your holistic assessment",
  "reasoning_confidence": 0.0-1.0
}}
```

**Remember:** Be specific, actionable, and respectful of the writer's vision. Focus on story health, not personal preferences."""

    return prompt


def _format_interpretation(interpretation: Dict[str, Any]) -> str:
    """Format the interpretation section."""
    if not interpretation:
        return "No pre-interpretation available."
    
    lines = []
    for key, value in interpretation.items():
        lines.append(f"**{key.replace('_', ' ').title()}:** {value}")
    
    return "\n".join(lines)


def _format_recent_scenes(scenes: list) -> str:
    """Format recent scenes for the prompt."""
    if not scenes:
        return "No recent scenes available."
    
    formatted = []
    for i, scene in enumerate(scenes[:5], 1):  # Limit to 5 most recent
        formatted.append(f"""
**Scene {i}:** {scene.get('title', 'Untitled')}
- **ID:** {scene.get('id', 'unknown')}
- **Word Count:** {scene.get('word_count', 0)}
- **Summary:** {scene.get('summary', 'No summary available')[:200]}...
""")
    
    return "\n".join(formatted)


def _format_focus_areas(focus_areas: list) -> str:
    """Format focus areas for the prompt."""
    if not focus_areas:
        return "No specific focus areas identified."
    
    return "- " + "\n- ".join(focus_areas)
