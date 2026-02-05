"""
Manuscript Processor

Orchestrates the full manuscript processing pipeline:
1. Extract text from uploaded file
2. Chunk if necessary for LLM processing
3. Generate AI summary
4. Store in MongoDB

This is the single entry point for the API layer.
"""

from typing import Dict, Any, Optional
import logging

from .text_extractor import TextExtractor
from .document_chunker import DocumentChunker
from .summarizer import get_summarizer, BaseSummarizer
from app.db.manuscript_repository import get_manuscript_repository

logger = logging.getLogger(__name__)


class ManuscriptProcessor:
    """
    Full pipeline orchestrator for manuscript processing.
    
    Usage:
        processor = ManuscriptProcessor()
        result = await processor.process(
            file_content=raw_bytes,
            file_type="pdf",
            title="My Novel"
        )
    """
    
    # Default chunking settings
    DEFAULT_MAX_TOKENS = 4000  # Conservative for LLM context
    DEFAULT_OVERLAP = 200
    
    def __init__(
        self,
        summarizer: Optional[BaseSummarizer] = None,
        max_tokens: int = DEFAULT_MAX_TOKENS,
        overlap_tokens: int = DEFAULT_OVERLAP,
    ):
        """
        Initialize the processor.
        
        Args:
            summarizer: Custom summarizer (defaults to Groq)
            max_tokens: Max tokens per chunk
            overlap_tokens: Overlap between chunks
        """
        self.extractor = TextExtractor()
        self.chunker = DocumentChunker(
            max_tokens=max_tokens,
            overlap_tokens=overlap_tokens
        )
        self.summarizer = summarizer or get_summarizer("groq")
        self.repository = get_manuscript_repository()
    
    async def process(
        self,
        file_content: bytes,
        file_type: str,
        title: str,
        file_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process a manuscript through the full pipeline.
        
        Args:
            file_content: Raw file bytes
            file_type: File extension (pdf, docx, txt)
            title: Title for the manuscript
            file_name: Optional original filename
            
        Returns:
            Complete manuscript document with summary
            
        Raises:
            ValueError: If file type is unsupported or extraction fails
            Exception: If summarization or storage fails
        """
        logger.info(f"📖 Processing manuscript: {title} ({file_type})")
        
        # Step 1: Extract text
        logger.info("  Step 1: Extracting text...")
        text = self.extractor.extract_from_bytes(file_content, file_type)
        word_count = len(text.split())
        
        logger.info(f"  Extracted {word_count} words")
        
        if word_count == 0:
            raise ValueError("No text could be extracted from the file")
        
        # Step 2: Chunk if necessary
        logger.info("  Step 2: Checking chunking requirements...")
        chunks = self.chunker.chunk(text)
        
        # Step 3: Summarize
        logger.info(f"  Step 3: Generating summary ({len(chunks)} chunk(s))...")
        
        if len(chunks) == 1:
            summary = await self.summarizer.summarize(
                text,
                context=f"This is a manuscript titled '{title}'"
            )
        else:
            summary = await self.summarizer.summarize_chunks(
                chunks,
                context=f"This is a manuscript titled '{title}'"
            )
        
        # Step 4: Store in MongoDB
        logger.info("  Step 4: Storing in database...")
        document = self.repository.create(
            title=title,
            original_text=text,
            summary=summary,
            word_count=word_count,
            model_used=self.summarizer.model_name,
            file_type=file_type,
            file_name=file_name,
        )
        
        logger.info(f"✅ Manuscript processed successfully: {document['id']}")
        
        return document
    
    async def process_text(
        self,
        text: str,
        title: str,
    ) -> Dict[str, Any]:
        """
        Process raw text (no file extraction needed).
        
        Args:
            text: Raw text content
            title: Title for the manuscript
            
        Returns:
            Complete manuscript document
        """
        logger.info(f"📝 Processing text: {title}")
        
        word_count = len(text.split())
        
        if word_count == 0:
            raise ValueError("Text is empty")
        
        # Chunk if necessary
        chunks = self.chunker.chunk(text)
        
        # Summarize
        if len(chunks) == 1:
            summary = await self.summarizer.summarize(text, context=f"Title: {title}")
        else:
            summary = await self.summarizer.summarize_chunks(chunks, context=f"Title: {title}")
        
        # Store
        document = self.repository.create(
            title=title,
            original_text=text,
            summary=summary,
            word_count=word_count,
            model_used=self.summarizer.model_name,
            file_type="text",
            file_name=None,
        )
        
        return document


# Convenient function for simple usage
async def process_manuscript(
    file_content: bytes,
    file_type: str,
    title: str,
    file_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Process a manuscript file.
    
    Args:
        file_content: Raw file bytes
        file_type: File extension (pdf, docx, txt)
        title: Title for the manuscript
        file_name: Original filename (optional)
        
    Returns:
        Manuscript document with summary
    """
    processor = ManuscriptProcessor()
    return await processor.process(
        file_content=file_content,
        file_type=file_type,
        title=title,
        file_name=file_name,
    )
