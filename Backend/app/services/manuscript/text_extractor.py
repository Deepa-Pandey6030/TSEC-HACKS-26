"""
Text Extractor

Extracts clean text from various file formats:
- PDF (using pypdf)
- DOCX (using python-docx)
- TXT (plain text)

Design Decision:
- Each format has a dedicated handler method for clarity.
- All methods return plain text, normalized (no excessive whitespace).
- Errors are logged and re-raised with context for upstream handling.
"""

from pathlib import Path
from typing import Union, BinaryIO
import logging
import io

logger = logging.getLogger(__name__)


class TextExtractor:
    """
    Unified text extraction from multiple file formats.
    
    Usage:
        extractor = TextExtractor()
        text = extractor.extract_from_bytes(file_bytes, "pdf")
        # or
        text = extractor.extract_from_path("/path/to/file.docx")
    """
    
    # Supported file extensions
    SUPPORTED_FORMATS = {"pdf", "docx", "txt"}
    
    def extract_from_bytes(self, content: bytes, file_type: str) -> str:
        """
        Extract text from raw bytes.
        
        Args:
            content: Raw file bytes
            file_type: File extension without dot (pdf, docx, txt)
            
        Returns:
            Extracted and cleaned text
            
        Raises:
            ValueError: If file type is unsupported
            Exception: If extraction fails
        """
        file_type = file_type.lower().strip(".")
        
        if file_type not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported file type: {file_type}. "
                f"Supported: {', '.join(self.SUPPORTED_FORMATS)}"
            )
        
        try:
            if file_type == "pdf":
                return self._extract_pdf(io.BytesIO(content))
            elif file_type == "docx":
                return self._extract_docx(io.BytesIO(content))
            elif file_type == "txt":
                return self._extract_txt(content)
            
        except Exception as e:
            logger.error(f"Text extraction failed for {file_type}: {e}")
            raise
    
    def extract_from_path(self, file_path: Union[str, Path]) -> str:
        """
        Extract text from a file path.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted and cleaned text
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_type = path.suffix.lower().strip(".")
        
        with open(path, "rb") as f:
            content = f.read()
        
        return self.extract_from_bytes(content, file_type)
    
    def _extract_pdf(self, file_obj: BinaryIO) -> str:
        """
        Extract text from PDF using pypdf.
        
        Handles multi-page documents, concatenating all pages.
        """
        try:
            from pypdf import PdfReader
        except ImportError:
            raise ImportError(
                "pypdf is required for PDF extraction. "
                "Install with: pip install pypdf"
            )
        
        reader = PdfReader(file_obj)
        text_parts = []
        
        for page_num, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            except Exception as e:
                logger.warning(f"Failed to extract page {page_num}: {e}")
                continue
        
        if not text_parts:
            raise ValueError("No text could be extracted from PDF")
        
        full_text = "\n\n".join(text_parts)
        return self._normalize_text(full_text)
    
    def _extract_docx(self, file_obj: BinaryIO) -> str:
        """
        Extract text from DOCX using python-docx.
        
        Extracts all paragraphs, preserving paragraph structure.
        """
        try:
            from docx import Document
        except ImportError:
            raise ImportError(
                "python-docx is required for DOCX extraction. "
                "Install with: pip install python-docx"
            )
        
        doc = Document(file_obj)
        text_parts = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        
        if not text_parts:
            raise ValueError("No text could be extracted from DOCX")
        
        full_text = "\n\n".join(text_parts)
        return self._normalize_text(full_text)
    
    def _extract_txt(self, content: bytes) -> str:
        """
        Extract text from plain text file.
        
        Handles common encodings: UTF-8, Latin-1.
        """
        # Try UTF-8 first (most common)
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            # Fallback to Latin-1 (handles all byte values)
            text = content.decode("latin-1")
        
        return self._normalize_text(text)
    
    def _normalize_text(self, text: str) -> str:
        """
        Normalize extracted text.
        
        - Remove excessive whitespace
        - Normalize line endings
        - Strip leading/trailing whitespace
        """
        import re
        
        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        
        # Collapse multiple blank lines to double newline
        text = re.sub(r"\n{3,}", "\n\n", text)
        
        # Collapse multiple spaces to single space
        text = re.sub(r"[ \t]+", " ", text)
        
        # Strip each line
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)
        
        return text.strip()


# Convenience function for simple usage
def extract_text_from_file(
    content: bytes,
    file_type: str
) -> str:
    """
    Extract text from file bytes.
    
    Args:
        content: Raw file bytes
        file_type: File extension (pdf, docx, txt)
        
    Returns:
        Extracted text
    """
    extractor = TextExtractor()
    return extractor.extract_from_bytes(content, file_type)
