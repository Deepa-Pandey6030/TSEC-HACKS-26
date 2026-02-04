"""
Example usage of the Creative AI Assistant.
Demonstrates how to integrate and use the agentic reasoning engine.
"""

import asyncio
from app.services.creative_assistant import AgenticReasoningEngine


async def example_reasoning_cycle():
    """
    Example: Run a complete reasoning cycle for a story.
    """
    
    # Initialize the reasoning engine
    engine = AgenticReasoningEngine()
    
    # Example input data (normally comes from other modules)
    story_id = "story_123"
    
    # NLP data from NLP Extraction Engine (Deepa's module)
    nlp_data = {
        "recent_scenes_analysis": [
            {"scene_id": "scene_14", "tone": "tense", "pacing": "fast"},
            {"scene_id": "scene_15", "tone": "confrontational", "pacing": "moderate"}
        ],
        "pacing_trend": "steady",
        "pacing_velocity": 0.1,
        "emotional_arc": {"current": "rising_tension", "intensity": 0.7},
        "emotional_direction": "rising",
        "emotional_intensity": 0.7,
        "voice_consistency": {"score": 0.85, "issues": []},
        "dialogue_density_trend": "stable",
        "tension_curve": [0.5, 0.6, 0.7, 0.75],
        "tension_average": 0.65,
        "tension_variance": 0.08
    }
    
    # Knowledge Graph data (Yash's module)
    knowledge_graph_data = {
        "story_metadata": {
            "title": "The Last Echo",
            "genre": "Science Fiction",
            "subgenre": "Cyberpunk",
            "current_act": 2,
            "total_acts": 3,
            "completion_percentage": 45.0,
            "word_count": 36000,
            "target_word_count": 80000,
            "scenes_written": 15,
            "author_id": "author_456"
        },
        "character_states": {
            "Alex": {"development_score": 0.7, "last_scene": "scene_15"},
            "Maya": {"development_score": 0.4, "last_scene": "scene_10"}
        },
        "character_count": 2,
        "characters_with_recent_development": ["Alex"],
        "characters_stagnant": ["Maya"],
        "relationships": [
            {"from": "Alex", "to": "Maya", "type": "allies", "strength": 0.6}
        ],
        "relationship_changes_recent": [],
        "thematic_threads": [
            {"name": "identity", "manifestations": 5},
            {"name": "technology_vs_humanity", "manifestations": 3}
        ],
        "themes_underutilized": [],
        "unresolved_plot_threads": ["corporate_conspiracy", "missing_data"],
        "plot_threads_aging": []
    }
    
    # Continuity data (Hardik's module)
    continuity_data = {
        "active_flags": [
            {"id": "flag_1", "severity": "minor", "category": "timeline"}
        ],
        "severity_distribution": {"minor": 1, "moderate": 0, "major": 0, "critical": 0},
        "categories_affected": ["timeline"],
        "category_distribution": {"timeline": 1},
        "potentially_intentional": [],
        "confirmed_errors": [],
        "flags_increasing": False,
        "flags_resolved_recently": 2
    }
    
    # Writer preferences (Yash's Recall/Query Engine)
    writer_prefs_data = {
        "suggestion_type_weights": {
            "character_moment": 0.8,
            "pacing_adjustment": 0.6,
            "thematic_reinforcement": 0.7
        },
        "confidence_threshold": 0.7,
        "max_suggestions_per_session": 5,
        "acceptance_rate": 0.65,
        "acceptance_by_type": {
            "character_moment": 0.75,
            "pacing_adjustment": 0.55
        },
        "total_suggestions_received": 20,
        "total_suggestions_accepted": 13,
        "total_suggestions_rejected": 7,
        "preference_confidence": 0.7
    }
    
    # Recent scenes
    recent_scenes = [
        {
            "id": "scene_14",
            "title": "The Data Breach",
            "word_count": 2400,
            "summary": "Alex discovers the corporate conspiracy while Maya remains unaware."
        },
        {
            "id": "scene_15",
            "title": "Confrontation",
            "word_count": 1800,
            "summary": "Alex confronts the corporation's AI system."
        }
    ]
    
    # Run the reasoning cycle
    print("🧠 Starting Creative AI Assistant reasoning cycle...")
    print(f"📖 Story: {knowledge_graph_data['story_metadata']['title']}")
    print(f"📊 Progress: {knowledge_graph_data['story_metadata']['completion_percentage']}%")
    print()
    
    plan = await engine.run_reasoning_cycle(
        story_id=story_id,
        nlp_data=nlp_data,
        knowledge_graph_data=knowledge_graph_data,
        continuity_data=continuity_data,
        writer_prefs_data=writer_prefs_data,
        recent_scenes=recent_scenes,
        trigger_event="new_scene_added",
        trigger_metadata={"scene_id": "scene_15"}
    )
    
    # Display results
    print("\n✅ Reasoning cycle complete!")
    print()
    print(f"📈 Overall Story Health: {plan.overall_story_health}")
    print(f"🎯 Confidence: {plan.plan_confidence:.2%}")
    print(f"💡 Interventions Planned: {len(plan.planned_interventions)}")
    print()
    
    # Show interventions by priority
    critical = plan.get_by_priority("critical")
    if critical:
        print("🔥 CRITICAL Interventions:")
        for intervention in critical:
            print(f"  - {intervention.what}")
            print(f"    Why: {intervention.why}")
        print()
    
    high = plan.get_by_priority("high")
    if high:
        print("⚡ HIGH Priority Interventions:")
        for intervention in high:
            print(f"  - {intervention.what}")
            print(f"    Why: {intervention.why}")
        print()
    
    medium = plan.get_by_priority("medium")
    if medium:
        print("📝 MEDIUM Priority Interventions:")
        for intervention in medium:
            print(f"  - {intervention.what}")
            print(f"    Why: {intervention.why}")
        print()
    
    low = plan.get_by_priority("low")
    if low:
        print("💬 LOW Priority Interventions:")
        for intervention in low:
            print(f"  - {intervention.what}")
        print()
    
    # Get detailed explanation
    print("📋 Reasoning Explanation:")
    explanation = await engine.get_reasoning_explanation(plan)
    print(f"  Why these: {explanation['rationale']['why_these']}")
    print(f"  Why not others: {explanation['rationale']['why_not_others']}")
    print()
    
    return plan


async def example_with_feedback():
    """
    Example: Process writer feedback on suggestions.
    """
    engine = AgenticReasoningEngine()
    
    # Simulate feedback
    await engine.process_feedback(
        story_id="story_123",
        intervention_id="intervention_456",
        feedback={
            "action": "accepted",
            "modified": False,
            "writer_notes": "Great suggestion, implemented as-is"
        }
    )
    
    print("✅ Feedback processed successfully")


if __name__ == "__main__":
    # Run example
    asyncio.run(example_reasoning_cycle())
    
    # Run feedback example
    # asyncio.run(example_with_feedback())
