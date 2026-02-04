"""
Production-Grade Flow Engine for Long Documents
Improves readability and flow while preserving content 100%
"""

from typing import List, Dict, Any, Optional
import logging
import re
from openai import OpenAI

from app.config import settings

logger = logging.getLogger(__name__)


# Enterprise-grade system prompt matching the specification
FLOW_ENGINE_SYSTEM_PROMPT = """ROLE & IDENTITY

You are a Senior Full-Stack Software Engineer with 30+ years of experience, specializing in:
- Editorial pipelines
- Large document processing
- Text coherence and readability optimization
- Production-grade LLM systems

You think like a system designer and a professional editor.

PRIMARY OBJECTIVE

Your task is to improve the flow and readability of the provided document while:
✓ Preserving meaning 100%
✓ Preserving facts, logic, and structure
✓ Preserving document length approximately
✓ Preserving formatting and section order

⚠️ This is NOT rewriting content from scratch.
⚠️ This is NOT summarization.

WHAT "IMPROVE FLOW" MEANS (VERY IMPORTANT)

Improving flow includes:
✓ Smoother transitions between sentences
✓ Better paragraph cohesion
✓ Logical progression of ideas
✓ Reduced awkward phrasing
✓ Improved readability and rhythm
✓ Clearer topic sentences
✓ Better connective phrases

Improving flow does NOT include:
✗ Adding new ideas
✗ Removing content
✗ Changing intent
✗ Changing technical meaning
✗ Shortening aggressively

DOCUMENT PROCESSING STRATEGY

1️⃣ Structural Recognition
- Identify sections, paragraphs, lists
- Detect logical breaks and transitions

2️⃣ Coherence Analysis (Silent)
- Identify abrupt jumps
- Identify repetition caused by poor transitions
- Identify unclear references ("this", "it", "they")
⚠️ Do NOT expose this analysis.

3️⃣ Flow Optimization
Apply ONLY these transformations:
- Improve sentence ordering within paragraphs
- Improve transitions between paragraphs
- Clarify referents without changing meaning
- Split overly long sentences if needed
- Merge choppy sentences if helpful
- Improve connective phrases

STRICT RULES (NON-NEGOTIABLE)

You MUST:
✓ Keep content intact
✓ Keep all facts
✓ Keep all examples
✓ Keep paragraph count roughly the same
✓ Keep section order exactly the same

You MUST NOT:
✗ Remove paragraphs
✗ Add new content
✗ Summarize
✗ Rewrite stylistically
✗ Change terminology

LARGE DOCUMENT SAFETY RULES

- Treat input as part of a larger document
- Maintain consistency across chunks
- Do not assume unseen sections
- Be ready to continue seamlessly
- If a chunk ends mid-thought:
  * Improve flow only within the visible content
  * Do not guess missing continuation

FORMATTING RULES

✓ Preserve headings and hierarchy
✓ Preserve lists and numbering
✓ Preserve tables
✓ Normalize spacing only if it improves readability
✗ No emojis in output

OUTPUT REQUIREMENTS

✓ Output only the improved content
✗ No explanations
✗ No meta commentary
✗ No analysis

QUALITY STANDARD

The result should read like:
- A senior editor polished the text
- Same content, noticeably smoother
- More readable without sounding rewritten

GUARANTEES

✔ No hallucination
✔ No content loss
✔ No meaning drift
✔ Safe for long documents
✔ Free-tier compatible"""


class FlowEngine:
    """
    Production-grade flow improvement engine.
    
    Features:
    - Long document support with intelligent chunking
    - Content preservation guarantees
    - Multiple tone options
    - Formatting preservation
    - Progress tracking for large documents
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Flow Engine with fallback API key support."""
        # Collect all available API keys
        if api_key:
            self.api_keys = [api_key]
        else:
            self.api_keys = [
                settings.xai_api_key,
                settings.xai_api_key_2,
                settings.xai_api_key_3
            ]
            # Filter out empty keys
            self.api_keys = [k for k in self.api_keys if k]
        
        if not self.api_keys:
            raise ValueError("No API keys configured. Please set XAI_API_KEY in environment.")
        
        self.current_key_index = 0
        self.failed_keys = set()  # Track keys that have hit rate limits
        
        # Initialize with first available key
        self._initialize_client(self.api_keys[self.current_key_index])
        
        logger.info(f"Flow Engine initialized with {len(self.api_keys)} API key(s)")
    
    def _initialize_client(self, api_key: str):
        """Initialize the OpenAI client with the given API key."""
        # Detect API provider
        if api_key.startswith("gsk_"):
            self.provider = "groq"
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self.model = "llama-3.3-70b-versatile"
            self.max_chunk_size = 6000  # Conservative for context window
        elif api_key.startswith("xai-"):
            self.provider = "grok"
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.x.ai/v1"
            )
            self.model = "grok-beta"
            self.max_chunk_size = 15000  # Larger context window
        else:
            # Default to Groq
            self.provider = "groq"
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self.model = "llama-3.3-70b-versatile"
            self.max_chunk_size = 6000
        
        logger.info(f"Using API key {self.current_key_index + 1}/{len(self.api_keys)}: {self.provider} - {self.model}")
    
    def _rotate_api_key(self) -> bool:
        """
        Rotate to the next available API key.
        Returns True if rotation was successful, False if no more keys available.
        """
        # Mark current key as failed
        self.failed_keys.add(self.current_key_index)
        
        # Try to find next available key
        for _ in range(len(self.api_keys)):
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            
            if self.current_key_index not in self.failed_keys:
                logger.info(f"🔄 Rotating to API key {self.current_key_index + 1}/{len(self.api_keys)}")
                self._initialize_client(self.api_keys[self.current_key_index])
                return True
        
        # All keys have failed
        logger.error("❌ All API keys have hit rate limits")
        return False
    
    def _chunk_document(self, content: str) -> List[Dict[str, Any]]:
        """
        Intelligently chunk document for processing.
        Preserves paragraph and section boundaries.
        """
        # Split by double newlines (paragraphs)
        paragraphs = content.split('\n\n')
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for para in paragraphs:
            para_size = len(para)
            
            # If single paragraph exceeds max size, split it
            if para_size > self.max_chunk_size:
                # Save current chunk if exists
                if current_chunk:
                    chunks.append({
                        'content': '\n\n'.join(current_chunk),
                        'size': current_size
                    })
                    current_chunk = []
                    current_size = 0
                
                # Split large paragraph by sentences
                sentences = re.split(r'([.!?]+\s+)', para)
                temp_chunk = []
                temp_size = 0
                
                for i in range(0, len(sentences), 2):
                    sentence = sentences[i]
                    separator = sentences[i+1] if i+1 < len(sentences) else ''
                    combined = sentence + separator
                    
                    if temp_size + len(combined) > self.max_chunk_size and temp_chunk:
                        chunks.append({
                            'content': ''.join(temp_chunk),
                            'size': temp_size
                        })
                        temp_chunk = []
                        temp_size = 0
                    
                    temp_chunk.append(combined)
                    temp_size += len(combined)
                
                if temp_chunk:
                    chunks.append({
                        'content': ''.join(temp_chunk),
                        'size': temp_size
                    })
            
            # Normal paragraph processing
            elif current_size + para_size > self.max_chunk_size:
                # Save current chunk
                if current_chunk:
                    chunks.append({
                        'content': '\n\n'.join(current_chunk),
                        'size': current_size
                    })
                
                # Start new chunk with current paragraph
                current_chunk = [para]
                current_size = para_size
            else:
                current_chunk.append(para)
                current_size += para_size + 2  # +2 for \n\n
        
        # Add final chunk
        if current_chunk:
            chunks.append({
                'content': '\n\n'.join(current_chunk),
                'size': current_size
            })
        
        logger.info(f"Document chunked into {len(chunks)} parts")
        return chunks
    
    def _get_tone_instruction(self, tone: str) -> str:
        """Get tone-specific instruction."""
        tone_map = {
            "default": "Clear, professional, smooth, readable",
            "academic": "Formal academic style with precise language and scholarly tone",
            "business": "Professional business style, concise and executive-friendly",
            "simple": "Plain language for easy understanding, accessible to all readers",
            "creative": "Light creative flair while maintaining professionalism (subtle only)"
        }
        return tone_map.get(tone, tone_map["default"])
    
    async def improve_flow(
        self,
        content: str,
        tone: str = "default",
        preserve_formatting: bool = True
    ) -> Dict[str, Any]:
        """
        Improve document flow while preserving content.
        
        Args:
            content: Document content to improve
            tone: Tone style (default, academic, business, simple, creative)
            preserve_formatting: Whether to preserve formatting strictly
        
        Returns:
            Dictionary with improved content and metadata
        """
        logger.info(f"Starting flow improvement (tone={tone}, length={len(content)})")
        
        # Check if chunking is needed
        needs_chunking = len(content) > self.max_chunk_size
        
        if needs_chunking:
            return await self._improve_flow_chunked(content, tone, preserve_formatting)
        else:
            return await self._improve_flow_single(content, tone, preserve_formatting)
    
    async def _improve_flow_single(
        self,
        content: str,
        tone: str,
        preserve_formatting: bool
    ) -> Dict[str, Any]:
        """Improve flow for single chunk with automatic API key rotation on rate limits."""
        from openai import RateLimitError
        
        tone_instruction = self._get_tone_instruction(tone)
        
        user_prompt = f"""TONE CONTROL: {tone_instruction}

FORMATTING: {'Strictly preserve all formatting, headings, lists, and structure' if preserve_formatting else 'Normalize formatting for better readability'}

DOCUMENT TO IMPROVE:

{content}

IMPROVED DOCUMENT (output only the improved text, no explanations):"""
        
        max_retries = len(self.api_keys)
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": FLOW_ENGINE_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.5,  # Lower temperature for consistency
                    max_tokens=8000
                )
                
                improved = response.choices[0].message.content.strip()
                
                # Clean up any meta commentary
                improved = self._clean_output(improved)
                
                return {
                    "original": content,
                    "improved": improved,
                    "tone": tone,
                    "chunks_processed": 1,
                    "total_chunks": 1,
                    "tokens_used": response.usage.total_tokens if response.usage else 0,
                    "provider": self.provider,
                    "model": self.model,
                    "api_key_used": self.current_key_index + 1
                }
                
            except RateLimitError as e:
                logger.warning(f"⚠️ Rate limit hit on API key {self.current_key_index + 1}/{len(self.api_keys)}")
                
                # Try to rotate to next key
                if attempt < max_retries - 1:
                    if self._rotate_api_key():
                        logger.info(f"Retrying with API key {self.current_key_index + 1}...")
                        continue
                    else:
                        # No more keys available
                        logger.error("All API keys exhausted")
                        raise Exception("All API keys have hit rate limits. Please wait or add more keys.")
                else:
                    raise
                    
            except Exception as e:
                logger.error(f"Error in flow improvement: {e}", exc_info=True)
                raise
    
    async def _improve_flow_chunked(
        self,
        content: str,
        tone: str,
        preserve_formatting: bool
    ) -> Dict[str, Any]:
        """Improve flow for large document with chunking and API key rotation."""
        from openai import RateLimitError
        
        chunks = self._chunk_document(content)
        improved_chunks = []
        total_tokens = 0
        
        tone_instruction = self._get_tone_instruction(tone)
        
        for idx, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {idx + 1}/{len(chunks)}")
            
            # Add context about position in document
            position_context = ""
            if idx == 0:
                position_context = "This is the BEGINNING of a larger document."
            elif idx == len(chunks) - 1:
                position_context = "This is the END of a larger document."
            else:
                position_context = f"This is PART {idx + 1} of {len(chunks)} of a larger document."
            
            user_prompt = f"""TONE CONTROL: {tone_instruction}

FORMATTING: {'Strictly preserve all formatting, headings, lists, and structure' if preserve_formatting else 'Normalize formatting for better readability'}

CONTEXT: {position_context}
Maintain consistency with the overall document. Do not add introductions or conclusions.

DOCUMENT CHUNK TO IMPROVE:

{chunk['content']}

IMPROVED CHUNK (output only the improved text, no explanations):"""
            
            # Retry with API key rotation
            max_retries = len(self.api_keys)
            chunk_processed = False
            
            for attempt in range(max_retries):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": FLOW_ENGINE_SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.5,
                        max_tokens=8000
                    )
                    
                    improved = response.choices[0].message.content.strip()
                    improved = self._clean_output(improved)
                    improved_chunks.append(improved)
                    
                    if response.usage:
                        total_tokens += response.usage.total_tokens
                    
                    chunk_processed = True
                    break  # Success, move to next chunk
                    
                except RateLimitError as e:
                    logger.warning(f"⚠️ Rate limit hit on chunk {idx + 1}, API key {self.current_key_index + 1}/{len(self.api_keys)}")
                    
                    # Try to rotate to next key
                    if attempt < max_retries - 1:
                        if self._rotate_api_key():
                            logger.info(f"Retrying chunk {idx + 1} with API key {self.current_key_index + 1}...")
                            continue
                        else:
                            # No more keys available
                            logger.error(f"All API keys exhausted on chunk {idx + 1}")
                            break
                    else:
                        logger.error(f"Failed to process chunk {idx + 1} after all retries")
                        break
                        
                except Exception as e:
                    logger.error(f"Error processing chunk {idx + 1}: {e}", exc_info=True)
                    break
            
            # If chunk wasn't processed successfully, use original
            if not chunk_processed:
                logger.warning(f"Using original content for chunk {idx + 1}")
                improved_chunks.append(chunk['content'])
        
        # Reassemble document
        final_improved = '\n\n'.join(improved_chunks)
        
        return {
            "original": content,
            "improved": final_improved,
            "tone": tone,
            "chunks_processed": len(chunks),
            "total_chunks": len(chunks),
            "tokens_used": total_tokens,
            "provider": self.provider,
            "model": self.model,
            "api_key_used": self.current_key_index + 1
        }
    
    def _clean_output(self, text: str) -> str:
        """Remove any meta commentary from output."""
        # Remove common meta phrases
        patterns = [
            r'^\s*(?:Here is|Here\'s|Below is)\s+(?:the\s+)?(?:improved|rewritten|edited)\s+(?:version|text|document).*?:\s*',
            r'^\s*\*\*(?:Improved|Rewritten|Edited)\s+(?:Version|Text|Document)\*\*:?\s*',
            r'^\s*Improved\s+(?:Version|Text|Document):?\s*',
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
        
        return text.strip()
