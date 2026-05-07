from langchain_community.embeddings import HuggingFaceEmbeddings
from src.utils import get_logger

logger = get_logger(__name__)

_embeddings_instance = None

def get_embeddings():
    global _embeddings_instance
    if _embeddings_instance is None:
        logger.info("Loading local HuggingFace embeddings (all-MiniLM-L6-v2)...")
        _embeddings_instance = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        logger.info("Embeddings model loaded!")
    return _embeddings_instance

def embed_texts(texts):
    emb = get_embeddings()
    return emb.embed_documents(texts)