"""
Smart text chunker — splits concall text into semantically meaningful chunks
with overlap for better RAG retrieval.
"""

from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.utils import get_logger

logger = get_logger(__name__)

# Optimal settings for earnings call transcripts
CHUNK_SIZE = 1000       # characters per chunk
CHUNK_OVERLAP = 200     # overlap between chunks
MIN_CHUNK_LENGTH = 100  # discard tiny chunks


def chunk_pages(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Split pages into overlapping chunks suitable for RAG.

    Args:
        pages: Output from pdf_loader.load_pdf()

    Returns:
        List of chunk dicts with metadata.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    chunks = []
    chunk_id = 0

    for page in pages:
        raw_chunks = splitter.split_text(page["text"])

        for raw in raw_chunks:
            if len(raw.strip()) < MIN_CHUNK_LENGTH:
                continue

            chunks.append({
                "chunk_id": f"{page['source']}_p{page['page_num']}_c{chunk_id}",
                "text": raw.strip(),
                "page_num": page["page_num"],
                "source": page["source"],
                "file_path": page.get("file_path", ""),
            })
            chunk_id += 1

    logger.info(f"Created {len(chunks)} chunks from {len(pages)} pages")
    return chunks


def chunk_text(text: str, source: str = "unknown") -> List[Dict[str, Any]]:
    """Convenience function to chunk a raw string."""
    pages = [{"page_num": 1, "text": text, "source": source, "file_path": ""}]
    return chunk_pages(pages)
