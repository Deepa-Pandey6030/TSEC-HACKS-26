from crewai import Task
from typing import List


class CharacterVoiceTasks:
    """Factory class for creating tasks"""
    
    @staticmethod
    def character_analysis_task(agent, summary: str, character_name: str) -> Task:
        """Task for analyzing character behavior and personality"""
        
        return Task(
            description=f"""Analyze the character '{character_name}' from the following summary:
            
            SUMMARY:
            {summary}
            
            Provide an extremely detailed analysis including:
            
            1. PERSONALITY PROFILE:
               - Core personality traits (e.g., bubbly, serious, mischievous, calm)
               - Dominant characteristics
               - Social tendencies (extroverted/introverted)
               - Maturity level and age indicators
            
            2. EMOTIONAL CHARACTERISTICS:
               - Default emotional state
               - Emotional range and expressiveness
               - Common emotional responses (e.g., laughs often, cries easily)
               - Emotional triggers and patterns
            
            3. SPEECH PATTERNS:
               - Speaking speed (fast-talking, deliberate, rushed)
               - Verbal habits (giggles between words, thoughtful pauses)
               - Word choice tendencies (formal, casual, slang)
               - Sentence structure patterns
            
            4. ENERGY LEVEL:
               - Overall energy (high/medium/low)
               - Energy variations in different situations
               - Physical expressiveness
            
            5. BEHAVIORAL QUIRKS:
               - Unique mannerisms
               - Laugh/giggle characteristics
               - Emotional expression style
               - Playfulness indicators
            
            6. VOICE IMPLICATIONS:
               - How their personality would affect their voice
               - Natural voice modulation patterns
               - Emphasis and inflection tendencies
            
            Format your response as a detailed JSON structure that can be used for voice profile creation.
            Be extremely specific and detailed - this will directly drive voice generation.""",
            agent=agent,
            expected_output="""A comprehensive JSON-formatted character analysis containing:
            - personality_traits (list with intensity ratings)
            - emotional_profile (dict with baseline and patterns)
            - speech_characteristics (dict with detailed patterns)
            - energy_assessment (dict with levels and variations)
            - behavioral_quirks (list with descriptions)
            - voice_implications (dict with detailed recommendations)"""
        )
    
    @staticmethod
    def voice_profile_creation_task(agent, character_name: str) -> Task:
        """Task for creating detailed voice profile from character analysis"""
        
        return Task(
            description=f"""Based on the character analysis for '{character_name}', create a detailed 
            voice profile that can be used to configure TTS systems or guide voice actors.
            
            Create a comprehensive voice profile including:
            
            1. BASE VOICE CHARACTERISTICS:
               - Pitch: Specify exact range (very_high/high/medium_high/medium/medium_low/low/very_low)
               - Tone Quality: Describe timbre (bright/warm/neutral/dark/breathy/raspy/clear/rich)
               - Pace: Default speaking speed (very_fast/fast/moderate/slow/very_slow/variable)
               - Volume: Typical loudness (loud/moderate/soft/whisper/variable)
               - Resonance: Voice depth and body
            
            2. EMOTIONAL BASELINE:
               - Default emotional coloring
               - Emotional expressiveness level (1-10)
               - Common emotional states in voice
            
            3. MODULATION PATTERNS:
               - How voice changes with happiness (pitch up, pace faster, etc.)
               - How voice changes with sadness (pitch down, pace slower, etc.)
               - How voice changes with excitement (energy boost, volume up, etc.)
               - How voice changes with anger, fear, surprise, etc.
            
            4. SPECIAL VOCAL CHARACTERISTICS:
               - Laugh type and frequency (giggle/chuckle/hearty laugh)
               - Sigh patterns
               - Breathing patterns
               - Vocal fry, uptalk, or other features
               - Accent or dialectical features
            
            5. EMPHASIS AND INFLECTION:
               - Word emphasis patterns
               - Sentence inflection tendencies
               - Question intonation style
               - Exclamation patterns
            
            6. TTS CONFIGURATION PARAMETERS:
               - Suggested TTS settings (pitch: +X%, speed: X, energy: X)
               - SSML tags to use regularly
               - Emotion tags and their frequencies
               - Prosody recommendations
            
            7. CHARACTER-SPECIFIC EXAMPLES:
               - Sample sentences showing typical delivery
               - Examples of emotional variations
            
            Output as a detailed JSON structure ready for TTS integration.""",
            agent=agent,
            expected_output="""A complete voice profile in JSON format with:
            - base_voice_characteristics (all parameters defined)
            - emotional_baseline (default states and expressiveness)
            - modulation_patterns (emotion-specific changes)
            - special_characteristics (unique vocal features)
            - emphasis_patterns (inflection and stress)
            - tts_configuration (ready-to-use parameters)
            - example_deliveries (sample sentences with markup)"""
        )
    
    @staticmethod
    def scene_voice_direction_task(agent, character_name: str, scene_description: str, 
                                   base_profile: str = "") -> Task:
        """Task for generating scene-specific voice directions"""
        
        return Task(
            description=f"""For character '{character_name}' in this scene:
            
            SCENE:
            {scene_description}
            
            {f"BASE VOICE PROFILE: {base_profile}" if base_profile else ""}
            
            Create scene-specific voice direction that adapts the character's voice to this moment while 
            maintaining their core personality.
            
            Provide:
            
            1. SCENE EMOTIONAL ANALYSIS:
               - Primary emotion in this scene
               - Emotional intensity (1-10)
               - Emotional transitions within the scene
               - Subtext and underlying feelings
            
            2. VOICE ADJUSTMENTS FOR THIS SCENE:
               - Pitch modifications from baseline
               - Pace adjustments (faster/slower and why)
               - Energy level changes
               - Volume adjustments
               - Tone shifts
            
            3. SPECIFIC VOICE DIRECTIONS:
               - How to deliver specific lines or moments
               - Where to add emphasis
               - Where to pause
               - Where to modulate
               - Special vocal effects needed (laughter, sighs, gasps, etc.)
            
            4. EMOTIONAL DELIVERY NOTES:
               - How emotion should color the voice
               - Contrast with character's normal state
               - Building or releasing emotional tension
            
            5. TTS MARKUP FOR THIS SCENE:
               - Specific SSML tags to use
               - Prosody settings for different parts
               - Emotion and emphasis markup
               - Break and pause placements
            
            6. PERFORMANCE NOTES:
               - Key moments that need special attention
               - Character consistency reminders
               - Pitfalls to avoid
            
            Make sure the direction maintains character authenticity while fully expressing the scene's 
            emotional content. If the character is normally bubbly but the scene is sad, show how their 
            bubbliness might be subdued but still present.""",
            agent=agent,
            expected_output="""Scene-specific voice direction in JSON format containing:
            - scene_emotion_analysis (detailed breakdown)
            - voice_adjustments (specific modifications from baseline)
            - delivery_directions (line-by-line or moment-by-moment guidance)
            - emotional_coloring (how to express the emotion)
            - tts_markup (ready-to-use SSML/markup)
            - performance_notes (director's notes for consistency)"""
        )
    
    @staticmethod
    def create_task_sequence(agents: dict, summary: str, character_name: str, 
                           scene_description: str = None) -> List[Task]:
        """Create a complete sequence of tasks"""
        
        tasks = [
            CharacterVoiceTasks.character_analysis_task(
                agents['character_analyzer'], 
                summary, 
                character_name
            ),
            CharacterVoiceTasks.voice_profile_creation_task(
                agents['voice_profile_creator'],
                character_name
            )
        ]
        
        # Add scene-specific task if scene is provided
        if scene_description:
            tasks.append(
                CharacterVoiceTasks.scene_voice_direction_task(
                    agents['scene_voice_director'],
                    character_name,
                    scene_description
                )
            )
        
        return tasks
