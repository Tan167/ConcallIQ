"""
Vector Store — ChromaDB local persistence for concall embeddings.
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.rag.embeddings import get_embeddings
from src.utils import get_logger

logger = get_logger(__name__)

CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chromadb")
COLLECTION_NAME = "concalls"

_vector_store: Optional[Chroma] = None


def get_vector_store() -> Chroma:
    """Return (or create) the ChromaDB vector store."""
    global _vector_store

    if _vector_store is None:
        Path(CHROMA_DIR).mkdir(parents=True, exist_ok=True)
        _vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=get_embeddings(),
            persist_directory=CHROMA_DIR,
        )
        logger.info(f"ChromaDB loaded from {CHROMA_DIR}")

    return _vector_store


def reset_vector_store():
    """Clear the in-memory reference (forces reload)."""
    global _vector_store
    _vector_store = None


def index_chunks(chunks: List[Dict[str, Any]], company: str = "") -> int:
    """
    Embed and index a list of text chunks into ChromaDB.

    Args:
        chunks: List of chunk dicts from chunker.
        company: Company name tag for filtering.

    Returns:
        Number of chunks indexed.
    """
    if not chunks:
        logger.warning("No chunks to index.")
        return 0

    docs = []
    ids = []

    for chunk in chunks:
        doc = Document(
            page_content=chunk["text"],
            metadata={
                "chunk_id": chunk["chunk_id"],
                "source": chunk["source"],
                "page_num": chunk["page_num"],
                "company": company,
            }
        )
        docs.append(doc)
        ids.append(chunk["chunk_id"])

    vs = get_vector_store()
    vs.add_documents(docs, ids=ids)
    logger.info(f"Indexed {len(docs)} chunks for '{company}'")
    return len(docs)


def similarity_search(query: str, k: int = 5, company_filter: str = "") -> List[Document]:
    """
    Retrieve the top-k most relevant chunks for a query.

    Args:
        query: User question.
        k: Number of results.
        company_filter: If set, filter by company name.

    Returns:
        List of LangChain Documents.
    """
    vs = get_vector_store()

    where = {"company": company_filter} if company_filter else None

    results = vs.similarity_search(
        query,
        k=k,
        filter=where,
    )
    logger.info(f"Retrieved {len(results)} chunks for query: '{query[:60]}'")
    return results


def list_indexed_companies() -> List[str]:
    """Return list of unique companies indexed in ChromaDB."""
    try:
        vs = get_vector_store()
        collection = vs._collection
        all_meta = collection.get(include=["metadatas"])["metadatas"]
        companies = list({m.get("company", "") for m in all_meta if m.get("company")})
        return sorted(companies)
    except Exception:
        return []


def delete_company(company: str):
    """Delete all chunks for a specific company."""
    vs = get_vector_store()
    vs._collection.delete(where={"company": company})
    logger.info(f"Deleted all chunks for company: {company}")
