from crewai_tools import BaseTool
from typing import Type, Dict, Any
from pydantic import BaseModel, Field
import json


class VoiceProfileSchema(BaseModel):
    """Schema for voice profile output"""
    character_name: str = Field(..., description="Name of the character")
    profile_data: dict = Field(..., description="Voice profile data")


class VoiceProfileSaver(BaseTool):
    name: str = "Voice Profile Saver"
    description: str = """Saves voice profiles to JSON files for later use with TTS systems.
    Input should be a dictionary containing character name and profile data."""
    
    def _run(self, character_name: str, profile_data: dict) -> str:
        """Save voice profile to file"""
        try:
            filename = f"outputs/{character_name.lower().replace(' ', '_')}_voice_profile.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)
            
            return f"Voice profile saved successfully to {filename}"
        except Exception as e:
            return f"Error saving voice profile: {str(e)}"


class EmotionAnalyzer(BaseTool):
    name: str = "Emotion Analyzer"
    description: str = """Analyzes text to identify emotional content, intensity, and transitions.
    Useful for understanding the emotional context of scenes."""
    
    def _run(self, text: str) -> Dict[str, Any]:
        """Analyze emotional content of text"""
        # This is a simplified version. In production, you might use NLP libraries
        emotions_map = {
            'happy': ['laugh', 'smile', 'joy', 'excited', 'cheerful', 'giggle'],
            'sad': ['cry', 'tears', 'sorrow', 'melancholy', 'depressed'],
            'angry': ['furious', 'mad', 'rage', 'annoyed', 'irritated'],
            'fearful': ['scared', 'afraid', 'terrified', 'anxious', 'worried'],
            'surprised': ['shocked', 'amazed', 'astonished', 'stunned'],
            'playful': ['teasing', 'mischievous', 'playful', 'naughty', 'cheeky']
        }
        
        text_lower = text.lower()
        detected_emotions = {}
        
        for emotion, keywords in emotions_map.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                detected_emotions[emotion] = count
        
        return {
            'detected_emotions': detected_emotions,
            'primary_emotion': max(detected_emotions, key=detected_emotions.get) if detected_emotions else 'neutral',
            'emotional_intensity': sum(detected_emotions.values()) if detected_emotions else 0
        }


class CharacterTraitExtractor(BaseTool):
    name: str = "Character Trait Extractor"
    description: str = """Extracts personality traits from character descriptions.
    Returns structured trait information."""
    
    def _run(self, description: str) -> Dict[str, Any]:
        """Extract traits from character description"""
        trait_keywords = {
            'bubbly': ['bubbly', 'energetic', 'lively', 'vivacious'],
            'serious': ['serious', 'stern', 'grave', 'solemn'],
            'playful': ['playful', 'mischievous', 'naughty', 'teasing'],
            'calm': ['calm', 'peaceful', 'serene', 'tranquil'],
            'intense': ['intense', 'passionate', 'fervent', 'ardent'],
            'shy': ['shy', 'timid', 'reserved', 'introverted'],
            'confident': ['confident', 'assertive', 'bold', 'self-assured']
        }
        
        desc_lower = description.lower()
        identified_traits = {}
        
        for trait, keywords in trait_keywords.items():
            for keyword in keywords:
                if keyword in desc_lower:
                    identified_traits[trait] = identified_traits.get(trait, 0) + 1
        
        return {
            'traits': identified_traits,
            'dominant_trait': max(identified_traits, key=identified_traits.get) if identified_traits else 'balanced'
        }
