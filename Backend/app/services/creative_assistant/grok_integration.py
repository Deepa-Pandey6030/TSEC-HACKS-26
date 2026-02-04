"""
Production-grade Groq API integration (alternative to Grok).
Handles retries, rate limiting, error handling, and token management.
"""

from openai import OpenAI, APIError, APIConnectionError, RateLimitError
import logging
import json
import time
from typing import Dict, Optional, Any
from functools import wraps
import asyncio

from app.config import settings
from .prompts.senior_writer_system import SENIOR_WRITER_SYSTEM_PROMPT
from .prompts.reasoning_templates import build_narrative_reasoning_prompt
from .models.reasoning_output import ReasoningOutput

logger = logging.getLogger(__name__)


def retry_with_exponential_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0
):
    """
    Decorator for exponential backoff retry logic.
    Professional error handling for production AI systems.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                
                except RateLimitError as e:
                    last_exception = e
                    logger.warning(f"Rate limit hit on attempt {attempt + 1}/{max_retries}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay)
                        delay = min(delay * 2, max_delay)
                    
                except APIConnectionError as e:
                    last_exception = e
                    logger.warning(f"API connection error on attempt {attempt + 1}/{max_retries}: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay)
                        delay = min(delay * 2, max_delay)
                
                except APIError as e:
                    # Don't retry on client errors (4xx)
                    if hasattr(e, 'status_code') and 400 <= e.status_code < 500:
                        logger.error(f"Client error, not retrying: {e}")
                        raise
                    
                    last_exception = e
                    logger.warning(f"API error on attempt {attempt + 1}/{max_retries}: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay)
                        delay = min(delay * 2, max_delay)
            
            # All retries exhausted
            logger.error(f"All {max_retries} retries exhausted")
            raise last_exception
        
        return wrapper
    return decorator


class GrokIntegration:
    """
    Production-grade Groq API integration.
    
    Features:
    - Exponential backoff retry
    - Rate limiting
    - Token counting
    - Error handling
    - Response parsing and validation
    - Caching support
    
    Note: Using Groq API (groq.com) - ultra-fast inference
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the API integration.
        Automatically detects whether to use Groq or xAI Grok based on API key format.
        """
        api_key = api_key or settings.xai_api_key
        
        # Detect API provider from key format
        if api_key.startswith("gsk_"):
            # Groq API key
            self.provider = "groq"
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self.model = "llama-3.3-70b-versatile"
            self.max_context_tokens = 32000
            logger.info("🚀 Using Groq API with Llama 3.3 70B")
            
        elif api_key.startswith("xai-"):
            # xAI Grok API key
            self.provider = "grok"
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.x.ai/v1"
            )
            self.model = "grok-beta"
            self.max_context_tokens = 128000
            logger.info("🚀 Using xAI Grok API")
            
        else:
            # Unknown format - try Groq as default
            logger.warning(f"Unknown API key format (starts with: {api_key[:4]}...), defaulting to Groq")
            self.provider = "groq"
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self.model = "llama-3.3-70b-versatile"
            self.max_context_tokens = 32000
        
        self.max_output_tokens = 8000
        
        # Rate limiting state
        self.request_count = 0
        self.last_request_time = 0
        
        logger.info(f"API integration initialized: {self.provider} - {self.model}")
    
    @retry_with_exponential_backoff(max_retries=3)
    async def generate_reasoning(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        json_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Generate AI reasoning using Groq.
        
        Args:
            system_prompt: System prompt defining AI persona
            user_prompt: User prompt with context and task
            temperature: Sampling temperature (0-1)
            max_tokens: Max tokens to generate
        
        Returns:
            Parsed JSON response from Groq
        """
        start_time = time.time()
        
        try:
            # Rate limiting (simple implementation)
            self._rate_limit_check()
            
            # Log request
            logger.info(f"Calling Groq API (temp={temperature}, max_tokens={max_tokens})")
            
            # Make API call (synchronous call wrapped for async context)
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extract content
            content = response.choices[0].message.content
            
            # Parse response
            if json_mode:
                parsed = self._parse_json_response(content)
            else:
                parsed = {"text": content}
            
            # Add metadata
            parsed["_metadata"] = {
                "model": self.model,
                "tokens_used": response.usage.total_tokens if response.usage else 0,
                "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                "output_tokens": response.usage.completion_tokens if response.usage else 0,
                "latency_seconds": time.time() - start_time
            }
            
            logger.info(
                f"Groq response received. "
                f"Tokens: {response.usage.total_tokens if response.usage else 0}, "
                f"Latency: {time.time() - start_time:.2f}s"
            )
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error in Groq API call: {e}", exc_info=True)
            raise
    
    async def generate_narrative_reasoning(
        self,
        context_dict: Dict[str, Any],
        interpretation: Dict[str, Any]
    ) -> ReasoningOutput:
        """
        Main method: Generate narrative reasoning from context.
        
        This is what the reasoning engine calls.
        
        Args:
            context_dict: Narrative context as dict
            interpretation: Pre-interpreted context
        
        Returns:
            ReasoningOutput model with AI's creative judgment
        """
        logger.info("Generating narrative reasoning via Groq")
        
        # Build prompts
        system_prompt = SENIOR_WRITER_SYSTEM_PROMPT
        user_prompt = build_narrative_reasoning_prompt(context_dict, interpretation)
        
        # Generate
        response = await self.generate_reasoning(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.7,
            max_tokens=4000
        )
        
        # Parse into ReasoningOutput model
        try:
            reasoning = ReasoningOutput(**response)
            
            # Add token usage
            if "_metadata" in response:
                reasoning.tokens_used = response["_metadata"]["tokens_used"]
            
            return reasoning
            
        except Exception as e:
            logger.error(f"Error parsing reasoning output: {e}", exc_info=True)
            logger.debug(f"Raw response: {response}")
            
            # Return minimal safe response on parse error
            return self._create_fallback_reasoning()
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """
        Parse JSON from Groq's response.
        Handles common formatting issues.
        """
        # Try direct parse
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # Try extracting from markdown code blocks
        if "```json" in content:
            try:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
                return json.loads(json_str)
            except:
                pass
        
        # Try extracting from code blocks without language
        if "```" in content:
            try:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                json_str = content[json_start:json_end].strip()
                return json.loads(json_str)
            except:
                pass
        
        # Last resort: look for {...} pattern
        try:
            first_brace = content.find("{")
            last_brace = content.rfind("}") + 1
            if first_brace != -1 and last_brace > first_brace:
                json_str = content[first_brace:last_brace]
                return json.loads(json_str)
        except:
            pass
        
        # Give up
        logger.error("Could not parse JSON from Groq response")
        raise ValueError(f"Invalid JSON response from Groq: {content[:500]}")
    
    def _rate_limit_check(self):
        """Simple rate limiting check."""
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self.last_request_time > 60:
            self.request_count = 0
            self.last_request_time = current_time
        
        self.request_count += 1
        
        # Log if getting close to limits
        if self.request_count > 50:
            logger.warning(f"Approaching rate limit: {self.request_count} requests in last minute")
    
    def _create_fallback_reasoning(self) -> ReasoningOutput:
        """Create minimal fallback reasoning on error."""
        from .models.reasoning_output import (
            MomentumAssessment, CharacterArcAssessment,
            EmotionalTrajectory, ThematicHealth,
            MomentumStatus, EmotionalTrend, ReinforcementQuality
        )
        
        return ReasoningOutput(
            momentum_assessment=MomentumAssessment(
                status=MomentumStatus.HEALTHY,
                evidence="Unable to analyze at this time",
                senior_writer_intuition="Analysis error occurred",
                pacing_score=0.5
            ),
            character_arc_assessment=CharacterArcAssessment(
                reasoning="Unable to analyze character arcs at this time",
                overall_arc_health="unknown"
            ),
            emotional_trajectory=EmotionalTrajectory(
                current_state="Unknown",
                trend=EmotionalTrend.STABLE,
                notes="Analysis error occurred"
            ),
            thematic_health=ThematicHealth(
                themes_present=[],
                reinforcement_quality=ReinforcementQuality.MODERATE,
                notes="Unable to analyze themes at this time"
            ),
            reasoning_confidence=0.0,
            overall_story_health="unknown",
            overall_health_reasoning="Analysis encountered an error",
            model_used=self.model
        )
