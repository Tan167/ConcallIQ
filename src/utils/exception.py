class ConcallIQError(Exception):
    """Base exception for ConcallIQ."""
    pass

class PDFLoadError(ConcallIQError):
    """Raised when a PDF cannot be loaded or parsed."""
    pass

class EmbeddingError(ConcallIQError):
    """Raised when embeddings fail."""
    pass

class RAGError(ConcallIQError):
    """Raised when RAG retrieval/generation fails."""
    pass

class SentimentError(ConcallIQError):
    """Raised when sentiment analysis fails."""
    pass
