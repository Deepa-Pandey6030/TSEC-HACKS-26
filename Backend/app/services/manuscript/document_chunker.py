"""
Document Chunker

Splits long documents into chunks that fit within LLM context limits.
Uses token-aware splitting to ensure each chunk is processable.

Design Decisions:
- We estimate tokens using a character-based heuristic (4 chars ≈ 1 token).
  This is conservative and works across LLMs without requiring tiktoken.
- Chunks overlap slightly to preserve context at boundaries.
- We split on paragraph boundaries when possible for coherence.
"""

from typing import List, Tuple
import logging
import re

logger = logging.getLogger(__name__)


class DocumentChunker:
    """
    Token-aware document chunker for LLM processing.
    
    Usage:
        chunker = DocumentChunker(max_tokens=4000)
        chunks = chunker.chunk(long_text)
    """
    
    # Characters per token estimate (conservative)
    # GPT/LLaMA average ~4 chars per token for English
    CHARS_PER_TOKEN = 4
    
    def __init__(
        self,
        max_tokens: int = 4000,
        overlap_tokens: int = 200
    ):
        """
        Initialize chunker.
        
        Args:
            max_tokens: Maximum tokens per chunk (default 4000)
            overlap_tokens: Token overlap between chunks (default 200)
        """
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        
        # Convert to character limits
        self.max_chars = max_tokens * self.CHARS_PER_TOKEN
        self.overlap_chars = overlap_tokens * self.CHARS_PER_TOKEN
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        return len(text) // self.CHARS_PER_TOKEN
    
    def needs_chunking(self, text: str) -> bool:
        """
        Check if text exceeds the token limit.
        
        Args:
            text: Input text
            
        Returns:
            True if chunking is needed
        """
        return self.estimate_tokens(text) > self.max_tokens
    
    def chunk(self, text: str) -> List[str]:
        """
        Split text into chunks.
        
        If text fits within limits, returns single-element list.
        Otherwise, splits on paragraph boundaries with overlap.
        
        Args:
            text: Input text
            
        Returns:
            List of text chunks
        """
        if not self.needs_chunking(text):
            return [text]
        
        # Split into paragraphs
        paragraphs = self._split_paragraphs(text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para)
            
            # If single paragraph exceeds limit, force-split it
            if para_length > self.max_chars:
                # Flush current chunk first
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = []
                    current_length = 0
                
                # Force-split the large paragraph
                sub_chunks = self._force_split(para)
                chunks.extend(sub_chunks)
                continue
            
            # Check if adding this paragraph exceeds limit
            if current_length + para_length + 2 > self.max_chars:  # +2 for "\n\n"
                # Save current chunk
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                
                # Start new chunk with overlap from previous
                overlap_paras = self._get_overlap(current_chunk)
                current_chunk = overlap_paras + [para]
                current_length = sum(len(p) for p in current_chunk) + 2 * len(current_chunk)
            else:
                current_chunk.append(para)
                current_length += para_length + 2
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
        
        logger.info(
            f"📄 Document chunked: {self.estimate_tokens(text)} tokens → "
            f"{len(chunks)} chunks"
        )
        
        return chunks
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs."""
        # Split on double newlines
        paragraphs = re.split(r"\n\s*\n", text)
        # Filter empty paragraphs
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _force_split(self, text: str) -> List[str]:
        """
        Force-split text that's too long for a single chunk.
        Splits on sentence boundaries when possible.
        """
        chunks = []
        
        # Try to split on sentences
        sentences = re.split(r"(?<=[.!?])\s+", text)
        
        current = []
        current_length = 0
        
        for sentence in sentences:
            sent_length = len(sentence)
            
            if current_length + sent_length > self.max_chars:
                if current:
                    chunks.append(" ".join(current))
                current = [sentence]
                current_length = sent_length
            else:
                current.append(sentence)
                current_length += sent_length + 1
        
        if current:
            chunks.append(" ".join(current))
        
        return chunks
    
    def _get_overlap(self, paragraphs: List[str]) -> List[str]:
        """Get paragraphs for overlap from the end of previous chunk."""
        if not paragraphs:
            return []
        
        overlap_paras = []
        overlap_length = 0
        
        # Take paragraphs from the end until we hit overlap limit
        for para in reversed(paragraphs):
            if overlap_length + len(para) > self.overlap_chars:
                break
            overlap_paras.insert(0, para)
            overlap_length += len(para)
        
        return overlap_paras
    
    def chunk_with_metadata(self, text: str) -> List[Tuple[str, dict]]:
        """
        Chunk text and return with metadata.
        
        Returns:
            List of (chunk_text, metadata) tuples
        """
        chunks = self.chunk(text)
        total_chunks = len(chunks)
        
        result = []
        for i, chunk in enumerate(chunks):
            metadata = {
                "chunk_index": i,
                "total_chunks": total_chunks,
                "estimated_tokens": self.estimate_tokens(chunk),
                "char_count": len(chunk),
            }
            result.append((chunk, metadata))
        
        return result
