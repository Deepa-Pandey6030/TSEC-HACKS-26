import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from parent directory .env file
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Also try loading from current working directory
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # Default to groq
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
GROQ_MODEL = os.getenv("GROQ_MODEL", "groq/llama-3.3-70b-versatile")  # Groq's fast LLM with provider prefix

# Agent Configuration
AGENT_CONFIG = {
    "character_analyzer": {
        "role": "Character Behavior Analyst",
        "goal": "Analyze character personalities, emotions, and behavioral patterns from story summaries with extreme detail",
        "backstory": """You are a world-renowned expert in character psychology and narrative analysis.
        You have studied thousands of characters across literature, film, and theater.
        You can identify the subtlest personality traits, emotional states, speech patterns, and 
        behavioral characteristics from story descriptions. You understand how personality manifests
        in vocal patterns, body language, and emotional expression.""",
        "verbose": True,
        "allow_delegation": False
    },
    "voice_profile_creator": {
        "role": "Voice Profile Designer & Audio Director",
        "goal": "Create detailed, technically precise voice profiles that capture character essence for TTS systems",
        "backstory": """You are a master voice director and audio engineer with 20+ years of experience
        in voice acting, dubbing, and TTS system configuration. You understand how to translate
        personality traits into specific voice characteristics like tone, pitch, pace, energy level,
        and emotional coloring. You know exactly how to configure modern TTS systems to achieve
        specific emotional and character effects.""",
        "verbose": True,
        "allow_delegation": False
    },
    "scene_voice_director": {
        "role": "Scene-Based Voice Performance Director",
        "goal": "Generate scene-specific voice directions that match emotional context while maintaining character consistency",
        "backstory": """You are an acclaimed voice performance director who has worked on hundreds
        of audiobooks, animations, and voice-over projects. You excel at analyzing the emotional
        arc of scenes and providing precise instructions for voice modulation, emphasis, pacing,
        and delivery style. You ensure that voice performance matches the scene's emotional intensity
        while staying true to the character's core personality.""",
        "verbose": True,
        "allow_delegation": False
    }
}

# Voice Profile Parameters
VOICE_PARAMETERS = {
    "pitch_range": ["very_high", "high", "medium_high", "medium", "medium_low", "low", "very_low"],
    "tone_quality": ["bright", "warm", "neutral", "dark", "breathy", "raspy", "clear", "rich"],
    "pace": ["very_fast", "fast", "moderate", "slow", "very_slow", "variable"],
    "energy_level": ["very_high", "high", "moderate", "low", "very_low"],
    "volume": ["loud", "moderate", "soft", "whisper", "variable"],
    "emotional_range": ["expressive", "moderate", "subtle", "monotone"]
}

# Output Configuration
OUTPUT_DIR = "outputs"
DATA_DIR = "data"
