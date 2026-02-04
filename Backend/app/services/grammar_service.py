import httpx
import logging
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class GrammarService:
    """
    Service to handle interactions with LanguageTool API.
    """
    
    def __init__(self, base_url: str = "https://api.languagetool.org/v2"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=10.0)

    async def check_grammar(self, text: str, language: str = "en-US") -> Dict[str, Any]:
        """
        Check grammar for the provided text using LanguageTool.
        """
        if not text or len(text.strip()) < 3:
            return {"matches": []}

        try:
            # LanguageTool public API has rate limits. 
            # In a production environment, you would use a local instance or paid API key.
            response = await self.client.post(
                f"{self.base_url}/check",
                data={
                    "text": text,
                    "language": language,
                    "enabledOnly": "false"
                }
            )
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error checking grammar: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error checking grammar: {e}")
            # Return empty matches on error to ensure non-blocking UI
            return {"matches": []}

    async def close(self):
        await self.client.aclose()

# Global instance
grammar_service = GrammarService()
