"""
Manuscript Processing Service Package

Provides a complete pipeline for:
- Extracting text from various file formats (PDF, DOCX, TXT)
- Chunking long documents for LLM processing
- AI-powered summarization with provider abstraction
- Orchestrating the full ingestion workflow
"""

from .text_extractor import TextExtractor, extract_text_from_file
from .document_chunker import DocumentChunker
from .summarizer import BaseSummarizer, GroqSummarizer, get_summarizer
from .manuscript_processor import ManuscriptProcessor, process_manuscript

__all__ = [
    "TextExtractor",
    "extract_text_from_file",
    "DocumentChunker",
    "BaseSummarizer",
    "GroqSummarizer",
    "get_summarizer",
    "ManuscriptProcessor",
    "process_manuscript",
]
