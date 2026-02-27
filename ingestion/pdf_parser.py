"""PDF parsing and text extraction."""
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import pdfplumber
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)


class PDFParser:
    """Extract text and metadata from PDF documents."""

    def __init__(self):
        """Initialize PDF parser."""
        self.supported_formats = [".pdf"]

    def parse(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a PDF file and extract text and metadata.

        Args:
            file_path: Path to the PDF file

        Returns:
            Dictionary containing extracted text and metadata
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        try:
            # Extract text using pdfplumber (better formatting)
            text = self._extract_text_pdfplumber(file_path)

            # Extract metadata using PyPDF2
            metadata = self._extract_metadata(file_path)

            return {
                "text": text,
                "metadata": metadata,
                "page_count": metadata.get("page_count", 0),
                "success": True,
            }

        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {e}")
            return {
                "text": "",
                "metadata": {},
                "page_count": 0,
                "success": False,
                "error": str(e),
            }

    def _extract_text_pdfplumber(self, file_path: Path) -> str:
        """Extract text using pdfplumber for better formatting."""
        text_parts = []

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

        return "\n\n".join(text_parts)

    def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract PDF metadata."""
        try:
            reader = PdfReader(str(file_path))
            metadata = reader.metadata

            return {
                "page_count": len(reader.pages),
                "title": metadata.get("/Title", ""),
                "author": metadata.get("/Author", ""),
                "subject": metadata.get("/Subject", ""),
                "creator": metadata.get("/Creator", ""),
                "producer": metadata.get("/Producer", ""),
                "creation_date": metadata.get("/CreationDate", ""),
            }

        except Exception as e:
            logger.warning(f"Error extracting metadata: {e}")
            return {"page_count": 0}


def parse_pdf(file_path: Path) -> Dict[str, Any]:
    """Convenience function to parse a PDF file."""
    parser = PDFParser()
    return parser.parse(file_path)
