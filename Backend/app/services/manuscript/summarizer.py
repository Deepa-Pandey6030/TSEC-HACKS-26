"""
AI Summarizer Service

Provides LLM-powered summarization with provider abstraction.
Currently implements Groq (using existing API keys from config).

Design Decisions:
- Abstract BaseSummarizer allows easy swapping to OpenAI, Gemini, etc.
- Uses hierarchical summarization for long documents:
  1. Summarize each chunk individually
  2. Combine chunk summaries and produce final summary
- Configurable prompts for different summarization styles.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import logging
import os
import httpx

logger = logging.getLogger(__name__)


class BaseSummarizer(ABC):
    """
    Abstract base class for LLM summarizers.
    
    Implement this interface to add new LLM providers.
    """
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model identifier."""
        pass
    
    @abstractmethod
    async def summarize(self, text: str, context: Optional[str] = None) -> str:
        """
        Generate a summary of the text.
        
        Args:
            text: Text to summarize
            context: Optional context (e.g., "This is a fiction novel")
            
        Returns:
            Summary text
        """
        pass
    
    @abstractmethod
    async def summarize_chunks(
        self,
        chunks: List[str],
        context: Optional[str] = None
    ) -> str:
        """
        Summarize multiple chunks and combine into final summary.
        
        Args:
            chunks: List of text chunks
            context: Optional context
            
        Returns:
            Combined summary
        """
        pass


class GroqSummarizer(BaseSummarizer):
    """
    Groq-based summarizer using LLaMA models.
    
    Uses the existing API keys configured in the application.
    """
    
    API_URL = "https://api.groq.com/openai/v1/chat/completions"
    DEFAULT_MODEL = "llama-3.3-70b-versatile"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.3,  # Lower temperature for factual summaries
    ):
        """
        Initialize Groq summarizer.
        
        Args:
            api_key: Groq API key (defaults to env XAI_API_KEY)
            model: Model to use (defaults to llama-3.3-70b-versatile)
            temperature: Sampling temperature (default 0.3)
        """
        self.api_key = api_key or self._get_api_key()
        self._model = model or os.getenv("GROK_MODEL", self.DEFAULT_MODEL)
        self.temperature = temperature
        
        if not self.api_key:
            raise ValueError(
                "No Groq API key found. Set XAI_API_KEY environment variable."
            )
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment, trying multiple options."""
        for key_name in ["XAI_API_KEY", "XAI_API_KEY_2", "XAI_API_KEY_3"]:
            key = os.getenv(key_name)
            if key:
                return key
        return None
    
    @property
    def model_name(self) -> str:
        return self._model
    
    async def _call_api(self, messages: List[dict]) -> str:
        """Make API call to Groq."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": 2000,
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                self.API_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            return data["choices"][0]["message"]["content"]
    
    async def summarize(self, text: str, context: Optional[str] = None) -> str:
        """
        Generate a summary of the text.
        """
        context_str = f"\nContext: {context}" if context else ""
        
        system_prompt = """You are an expert summarizer. Your task is to create clear, 
concise, and comprehensive summaries that capture the key points, themes, and 
important details of the provided text.

Guidelines:
- Focus on main ideas and key points
- Preserve important names, places, and events
- Maintain the tone and style of the original
- Be concise but thorough
- Use clear, accessible language"""
        
        user_prompt = f"""Please summarize the following text:{context_str}

---
{text}
---

Provide a well-structured summary that captures the essence of the content."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            summary = await self._call_api(messages)
            logger.info(f"✨ Generated summary: {len(summary)} chars")
            return summary.strip()
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            raise
    
    async def summarize_chunks(
        self,
        chunks: List[str],
        context: Optional[str] = None
    ) -> str:
        """
        Hierarchical summarization for chunked documents.
        
        1. Summarize each chunk
        2. Combine chunk summaries
        3. Generate final summary from combined summaries
        """
        if len(chunks) == 1:
            return await self.summarize(chunks[0], context)
        
        logger.info(f"📚 Summarizing {len(chunks)} chunks...")
        
        # Step 1: Summarize each chunk
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            logger.info(f"  Processing chunk {i+1}/{len(chunks)}...")
            summary = await self.summarize(
                chunk,
                context=f"{context or 'Document'} - Part {i+1} of {len(chunks)}"
            )
            chunk_summaries.append(f"[Part {i+1}]\n{summary}")
        
        # Step 2: Combine and summarize the summaries
        combined = "\n\n".join(chunk_summaries)
        
        logger.info("📝 Generating final summary from chunk summaries...")
        
        final_context = context or "a multi-part document"
        final_prompt = f"""The following are summaries of different parts of {final_context}. 
Please create a unified, coherent summary that combines all parts into a single 
comprehensive overview.

{combined}

Create a final, unified summary that flows naturally and captures the complete picture."""
        
        messages = [
            {"role": "system", "content": "You are an expert at synthesizing multiple summaries into a coherent whole."},
            {"role": "user", "content": final_prompt}
        ]
        
        try:
            final_summary = await self._call_api(messages)
            logger.info(f"✅ Final summary generated: {len(final_summary)} chars")
            return final_summary.strip()
        except Exception as e:
            logger.error(f"Final summarization failed: {e}")
            raise


# Factory for getting summarizer
_default_summarizer: Optional[BaseSummarizer] = None


def get_summarizer(provider: str = "groq") -> BaseSummarizer:
    """
    Get a summarizer instance.
    
    Args:
        provider: LLM provider ("groq", future: "openai", "gemini")
        
    Returns:
        Summarizer instance
    """
    global _default_summarizer
    
    if provider == "groq":
        if _default_summarizer is None:
            _default_summarizer = GroqSummarizer()
        return _default_summarizer
    else:
        raise ValueError(f"Unknown summarizer provider: {provider}")
