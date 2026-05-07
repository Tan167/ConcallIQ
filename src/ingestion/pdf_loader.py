"""
PDF Loader — loads and extracts text from concall PDFs/transcripts.
Supports both pdfplumber (preferred) and PyPDF2 as fallback.
"""

import os
from pathlib import Path
from typing import List, Dict, Any

import pdfplumber
import PyPDF2

from src.utils import get_logger, PDFLoadError

logger = get_logger(__name__)


def load_pdf(file_path: str) -> List[Dict[str, Any]]:
    """
    Load a PDF and extract text page by page.

    Args:
        file_path: Path to the PDF file.

    Returns:
        List of dicts: [{page_num, text, source}]
    """
    path = Path(file_path)
    if not path.exists():
        raise PDFLoadError(f"File not found: {file_path}")

    logger.info(f"Loading PDF: {path.name}")
    pages = []

    try:
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                if text.strip():
                    pages.append({
                        "page_num": i + 1,
                        "text": text.strip(),
                        "source": path.name,
                        "file_path": str(path)
                    })
        logger.info(f"Extracted {len(pages)} pages via pdfplumber")

    except Exception as e:
        logger.warning(f"pdfplumber failed ({e}), falling back to PyPDF2")
        try:
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for i, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    if text.strip():
                        pages.append({
                            "page_num": i + 1,
                            "text": text.strip(),
                            "source": path.name,
                            "file_path": str(path)
                        })
            logger.info(f"Extracted {len(pages)} pages via PyPDF2")
        except Exception as e2:
            raise PDFLoadError(f"Could not read PDF: {e2}") from e2

    if not pages:
        raise PDFLoadError(f"No text found in PDF: {file_path}")

    return pages


def load_pdf_from_bytes(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    """Load PDF from bytes (for Streamlit file uploads)."""
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        pages = load_pdf(tmp_path)
        # Override source with original filename
        for p in pages:
            p["source"] = filename
    finally:
        os.unlink(tmp_path)

    return pages
