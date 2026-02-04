# NOLAN Creative AI Assistant

## Overview

The Creative AI Assistant is a sophisticated agentic reasoning system that operates as a Senior Writer with 30+ years of experience, providing intelligent creative guidance for narrative writing.

## Architecture

The system implements a complete agentic reasoning loop:

```
OBSERVE → INTERPRET → REASON → PLAN → SUGGEST → REFLECT → ADAPT
```

### Components

1. **Observation Synthesizer** - Aggregates multi-source inputs (NLP, Knowledge Graph, Continuity, Preferences)
2. **Narrative Interpreter** - Extracts high-level insights from context
3. **Grok Integration** - Production-grade xAI Grok API wrapper with retry logic
4. **Intervention Planner** - Converts reasoning into prioritized action plans
5. **Agentic Reasoning Engine** - Orchestrates the complete reasoning cycle

## Installation

### Prerequisites

- Python 3.11+
- xAI Grok API key
- MongoDB (for data storage)
- Redis (for caching)
- Neo4j (for Knowledge Graph)

### Setup

1. **Install dependencies:**

```bash
cd Backend
pip install -r requirements.txt
```

2. **Configure environment:**

```bash
cp .env.example .env
# Edit .env and add your API keys and configuration
```

3. **Required environment variables:**

```env
XAI_API_KEY=your_grok_api_key_here
GROK_MODEL=grok-beta
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379
NEO4J_URI=bolt://localhost:7687
```

## Usage

### Basic Usage

```python
from app.services.creative_assistant import AgenticReasoningEngine

# Initialize engine
engine = AgenticReasoningEngine()

# Run reasoning cycle
plan = await engine.run_reasoning_cycle(
    story_id="story_123",
    nlp_data=nlp_analysis,
    knowledge_graph_data=kg_data,
    continuity_data=continuity_flags,
    writer_prefs_data=preferences,
    recent_scenes=scenes,
    trigger_event="new_scene_added"
)

# Access interventions
for intervention in plan.planned_interventions:
    print(f"{intervention.priority}: {intervention.what}")
```

### Integration with Other Modules

The Creative AI Assistant receives inputs from:

- **NLP Extraction Engine** (Deepa) - Tone, pacing, voice analysis
- **Knowledge Graph** (Yash) - Characters, relationships, themes
- **Continuity Validator** (Hardik) - Flags and inconsistencies
- **Recall/Query Engine** (Yash) - Writer preferences and history

## Data Models

### NarrativeContext

Complete holistic context aggregating all inputs:

```python
@dataclass
class NarrativeContext:
    story_progress: StoryProgress
    nlp_signals: NLPSignals
    knowledge_graph_state: KnowledgeGraphState
    continuity_signals: ContinuitySignals
    writer_preferences: WriterPreferences
    recent_scenes: List[Dict[str, Any]]
    trigger: TriggerContext
```

### ReasoningOutput

AI's creative judgment from Grok:

```python
class ReasoningOutput(BaseModel):
    momentum_assessment: MomentumAssessment
    character_arc_assessment: CharacterArcAssessment
    emotional_trajectory: EmotionalTrajectory
    structural_concerns: List[StructuralConcern]
    thematic_health: ThematicHealth
    opportunities: List[Opportunity]
    questions_for_writer: List[str]
    overall_story_health: str
    reasoning_confidence: float
```

### InterventionPlan

Actionable plan with prioritized suggestions:

```python
class InterventionPlan(BaseModel):
    story_id: str
    trigger_event: str
    planned_interventions: List[PlannedIntervention]
    why_these_interventions: str
    overall_story_health: str
    plan_confidence: float
```

## API Integration

### Grok API

The system uses xAI's Grok API (OpenAI-compatible) for narrative reasoning:

- **Model:** grok-beta (configurable)
- **Context Window:** 128K tokens
- **Max Output:** 8K tokens
- **Features:** Exponential backoff retry, rate limiting, JSON parsing

### Error Handling

Production-grade error handling includes:

- Exponential backoff retry (3 attempts)
- Rate limit detection and waiting
- Graceful fallback on API errors
- Comprehensive logging

## Prompt Engineering

### System Prompt

The Senior Writer system prompt defines the AI persona:

- 30+ years of creative writing experience
- Expertise in narrative structure, character development, pacing
- Respectful of writer's vision
- Focused on story health, not personal preferences

### Reasoning Prompt

Dynamic prompt construction includes:

- Story overview and progress
- NLP signals (pacing, tone, voice)
- Knowledge graph state (characters, themes, plot)
- Continuity signals (flags, inconsistencies)
- Writer preferences (acceptance rates, style)
- Recent scenes and focus areas

## Development

### Project Structure

```
Backend/
├── app/
│   ├── __init__.py
│   ├── config.py
│   └── services/
│       └── creative_assistant/
│           ├── __init__.py
│           ├── agentic_reasoning_engine.py
│           ├── grok_integration.py
│           ├── observation_synthesizer.py
│           ├── narrative_interpreter.py
│           ├── intervention_planner.py
│           ├── models/
│           │   ├── __init__.py
│           │   ├── narrative_context.py
│           │   ├── reasoning_output.py
│           │   └── intervention_plan.py
│           └── prompts/
│               ├── __init__.py
│               ├── senior_writer_system.py
│               └── reasoning_templates.py
├── requirements.txt
└── .env.example
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app/services/creative_assistant
```

### Code Quality

```bash
# Format code
black app/
isort app/

# Type checking
mypy app/

# Linting
flake8 app/
```

## Configuration

### Settings

All configuration is managed through `app/config.py` using Pydantic Settings:

- Environment variable support
- Type validation
- Default values
- Comprehensive documentation

### Key Settings

- `xai_api_key` - Grok API key
- `grok_model` - Model version (default: grok-beta)
- `max_context_tokens` - Context window limit (128K)
- `min_confidence_threshold` - Minimum confidence for suggestions (0.6)
- `max_suggestions_per_cycle` - Max suggestions per cycle (5)

## Logging

Comprehensive logging at all levels:

```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
```

Log levels:
- **INFO** - Normal operations, cycle completion
- **WARNING** - Rate limits, retries, non-critical issues
- **ERROR** - API errors, parsing failures
- **DEBUG** - Detailed debugging information

## Performance

### Optimization

- Async/await throughout for non-blocking I/O
- Efficient JSON parsing with fallback strategies
- Token counting to manage context windows
- Rate limiting to prevent API throttling

### Monitoring

Key metrics to monitor:

- Reasoning cycle duration
- Grok API latency
- Token usage
- Intervention acceptance rates
- Context completeness scores

## Future Enhancements

- [ ] Preference learning system (REFLECT/ADAPT steps)
- [ ] Suggestion generator with formatting
- [ ] Caching layer for repeated contexts
- [ ] A/B testing framework for prompts
- [ ] Real-time feedback integration
- [ ] Multi-model support (fallback to other LLMs)

## License

Proprietary - NOLAN System

## Contact

For questions or issues, contact the development team.
