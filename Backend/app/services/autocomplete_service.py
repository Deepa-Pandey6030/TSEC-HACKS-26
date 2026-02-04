import logging
from app.services.creative_assistant.grok_integration import GrokIntegration
from app.config import settings

logger = logging.getLogger(__name__)

class AutocompleteService:
    def __init__(self):
        # Use existing GrokIntegration which handles Groq/xAI logic
        self.ai = GrokIntegration(api_key=settings.xai_api_key)
    
    async def predict_next_text(self, text: str, max_words: int = 5) -> str:
        """
        Predict the next few words for Smart Compose.
        """
        if not text or len(text) < 10:
            return ""

        # Limit context to last 200 chars to cover the immediate sentence flow
        context = text[-200:]
        
        system_prompt = (
            "You are a super-fast autocomplete engine. "
            "Your task is to complete the user's sentence naturally. "
            f"Output ONLY the completion, maximum {max_words} words. "
            "Do not repeat the input. Do not output anything else. "
            "If the sentence is complete or no obvious completion exists, output nothing."
        )

        try:
            # Call generate_reasoning with json_mode=False to get raw text
            # Increased token limit to ensure complete responses
            result = await self.ai.generate_reasoning(
                system_prompt=system_prompt,
                user_prompt=context,
                temperature=0.1,
                max_tokens=50,
                json_mode=False
            )
            
            completion = result.get("text", "").strip()
            
            # Sanity check: ensure it doesn't just repeat the input words
            if completion and completion.lower() not in context.lower():
                return completion
            
            return ""

        except Exception as e:
            logger.warning(f"Autocomplete failed: {e}")
            return ""

autocomplete_service = AutocompleteService()
