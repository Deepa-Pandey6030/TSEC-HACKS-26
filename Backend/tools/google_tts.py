"""
Text-to-Speech Integration using edge-tts (Microsoft Edge TTS)

This module provides TTS functionality with natural-sounding voices
and the ability to match voice characteristics to character profiles.
"""

import asyncio
import edge_tts
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import json


class GoogleTTS:
    """edge-tts Text-to-Speech wrapper for character voice generation
    
    Note: Class name kept as GoogleTTS for backward compatibility with imports.
    Uses Microsoft Edge TTS which provides high-quality, natural-sounding voices.
    """
    
    # Voice mapping based on character traits
    VOICE_MAPPING = {
        # Female voices - Cheerful/Energetic
        'female_cheerful': 'en-US-AriaNeural',
        'female_friendly': 'en-US-JennyNeural', 
        'female_warm': 'en-US-SaraNeural',
        'female_professional': 'en-US-MichelleNeural',
        
        # Female voices - Other accents for variety
        'female_expressive': 'en-GB-SoniaNeural',
        'female_soft': 'en-AU-NatashaNeural',
        
        # Male voices
        'male_friendly': 'en-US-GuyNeural',
        'male_professional': 'en-US-DavisNeural',
        'male_warm': 'en-US-TonyNeural',
        'male_deep': 'en-US-ChristopherNeural',
        'male_narrator': 'en-GB-RyanNeural',
        
        # Neutral/Default
        'default': 'en-US-AriaNeural',
    }
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize edge-tts TTS engine
        
        Args:
            credentials_path: Not used, kept for API compatibility
        """
        self.output_dir = Path("outputs/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.reference_audio_path = None
    
    def set_reference_audio(self, audio_path: str):
        """
        Set a reference audio file for voice matching guidance
        
        Args:
            audio_path: Path to the reference audio file
        """
        self.reference_audio_path = audio_path
        print(f"📎 Reference audio set: {audio_path}")
        print("   Using this to guide voice selection")
    
    def select_voice_for_character(self, voice_profile: Dict[str, Any]) -> str:
        """
        Select appropriate voice based on character voice profile
        
        Args:
            voice_profile: Character voice profile dictionary
            
        Returns:
            Voice name string
        """
        profile_str = str(voice_profile).lower()
        
        # Determine voice based on profile attributes
        voice = self.VOICE_MAPPING['default']
        
        # Check for gender/character type
        if any(trait in profile_str for trait in ['bubbly', 'cheerful', 'energetic', 'excited', 'playful']):
            voice = self.VOICE_MAPPING['female_cheerful']
        elif any(trait in profile_str for trait in ['warm', 'gentle', 'soft', 'kind']):
            voice = self.VOICE_MAPPING['female_warm']
        elif any(trait in profile_str for trait in ['professional', 'serious', 'formal']):
            voice = self.VOICE_MAPPING['female_professional']
        elif any(trait in profile_str for trait in ['friendly', 'casual', 'approachable']):
            voice = self.VOICE_MAPPING['female_friendly']
        elif any(trait in profile_str for trait in ['deep', 'authoritative', 'commanding']):
            voice = self.VOICE_MAPPING['male_deep']
        elif any(trait in profile_str for trait in ['male', 'man', 'guy', 'he', 'him']):
            voice = self.VOICE_MAPPING['male_friendly']
        
        return voice
    
    def get_speech_parameters(self, voice_profile: Dict[str, Any]) -> Dict[str, str]:
        """
        Get speech rate and pitch parameters based on voice profile
        
        Args:
            voice_profile: Character voice profile dictionary
            
        Returns:
            Dict with rate and pitch adjustments
        """
        profile_str = str(voice_profile).lower()
        
        # Default values
        rate = "+0%"
        pitch = "+0Hz"
        
        # Adjust rate based on character traits
        if any(trait in profile_str for trait in ['fast', 'quick', 'energetic', 'excited', 'rushed']):
            rate = "+20%"
        elif any(trait in profile_str for trait in ['slow', 'calm', 'deliberate', 'thoughtful']):
            rate = "-15%"
        elif any(trait in profile_str for trait in ['very slow', 'drawl']):
            rate = "-25%"
        
        # Adjust pitch based on character traits
        if any(trait in profile_str for trait in ['high', 'bubbly', 'cheerful', 'young']):
            pitch = "+10Hz"
        elif any(trait in profile_str for trait in ['deep', 'low', 'bass', 'mature']):
            pitch = "-10Hz"
        
        return {"rate": rate, "pitch": pitch}
    
    async def _synthesize_async(
        self,
        text: str,
        output_path: str,
        voice: str,
        rate: str = "+0%",
        pitch: str = "+0Hz"
    ):
        """Async synthesis using edge-tts"""
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate,
            pitch=pitch
        )
        await communicate.save(output_path)
    
    def synthesize_speech(
        self,
        text: str,
        character_name: str,
        voice_profile: Optional[Dict[str, Any]] = None,
        use_ssml: bool = True,
        output_filename: Optional[str] = None
    ) -> str:
        """
        Synthesize speech from text using edge-tts
        
        Args:
            text: Text to synthesize
            character_name: Name of the character (for filename)
            voice_profile: Character voice profile for voice selection
            use_ssml: Not directly used, kept for API compatibility
            output_filename: Custom output filename (optional)
            
        Returns:
            Path to the generated audio file
        """
        # Select voice based on profile
        if voice_profile:
            voice = self.select_voice_for_character(voice_profile)
            params = self.get_speech_parameters(voice_profile)
        else:
            voice = self.VOICE_MAPPING['default']
            params = {"rate": "+0%", "pitch": "+0Hz"}
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if output_filename:
            filename = output_filename
        else:
            filename = f"{character_name.lower().replace(' ', '_')}_{timestamp}.mp3"
        
        output_path = self.output_dir / filename
        
        print(f"🔊 Synthesizing speech for {character_name}...")
        print(f"   Voice: {voice}")
        print(f"   Rate: {params['rate']}, Pitch: {params['pitch']}")
        
        # Run async synthesis - handle both async and sync contexts
        try:
            # Check if we're already in an event loop (e.g., FastAPI)
            loop = asyncio.get_running_loop()
            # We're in an async context, use nest_asyncio or run in thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    self._synthesize_async(
                        text=text,
                        output_path=str(output_path),
                        voice=voice,
                        rate=params['rate'],
                        pitch=params['pitch']
                    )
                )
                future.result()  # Wait for completion
        except RuntimeError:
            # No event loop running, use asyncio.run directly
            asyncio.run(self._synthesize_async(
                text=text,
                output_path=str(output_path),
                voice=voice,
                rate=params['rate'],
                pitch=params['pitch']
            ))
        
        print(f"✅ Audio saved to: {output_path}")
        return str(output_path)
    
    def speak(self, text: str, voice_profile: Optional[Dict[str, Any]] = None):
        """
        Generate speech (saves to temp file)
        
        Args:
            text: Text to speak
            voice_profile: Character voice profile
        """
        output = self.synthesize_speech(text, "temp", voice_profile)
        print(f"Audio generated: {output}")
        return output
    
    async def _list_voices_async(self) -> List[Dict]:
        """Async method to list available voices"""
        voices = await edge_tts.list_voices()
        return voices
    
    def list_available_voices(self, language_filter: str = "en") -> list:
        """
        List available voices
        
        Args:
            language_filter: Filter voices by language code
            
        Returns:
            List of available voice info
        """
        voices = asyncio.run(self._list_voices_async())
        
        filtered = []
        for voice in voices:
            if language_filter.lower() in voice['Locale'].lower():
                filtered.append({
                    'name': voice['ShortName'],
                    'gender': voice['Gender'],
                    'locale': voice['Locale'],
                    'friendly_name': voice['FriendlyName']
                })
        
        return filtered


def generate_character_voice(
    text: str,
    character_name: str,
    voice_profile: Optional[Dict[str, Any]] = None,
    credentials_path: Optional[str] = None,
    reference_audio: Optional[str] = None
) -> str:
    """
    Convenience function to generate voice for a character
    
    Args:
        text: Text to speak
        character_name: Character name
        voice_profile: Voice profile dict
        credentials_path: Not used, kept for API compatibility
        reference_audio: Path to reference audio file
        
    Returns:
        Path to generated audio file
    """
    tts = GoogleTTS()
    if reference_audio:
        tts.set_reference_audio(reference_audio)
    return tts.synthesize_speech(text, character_name, voice_profile)


if __name__ == "__main__":
    # Test the TTS
    tts = GoogleTTS()
    
    # List available voices
    print("\nAvailable English voices:")
    for voice in tts.list_available_voices("en-US")[:10]:
        print(f"  - {voice['name']} ({voice['gender']})")
    
    # Example voice profile (cheerful character)
    test_profile = {
        'tone': 'cheerful',
        'energy': 'high',
        'pace': 'fast',
        'traits': ['bubbly', 'energetic', 'playful'],
        'gender': 'female'
    }
    
    test_text = "Oh my gosh! This is amazing! I can't believe you're all here!"
    
    output = tts.synthesize_speech(
        text=test_text,
        character_name="Maya",
        voice_profile=test_profile
    )
    
    print(f"\nGenerated: {output}")
