"""
RAG Retriever — retrieves relevant concall chunks and generates answers via GPT-4o.
"""

import os
from typing import List, Dict, Any, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.rag.vector_store import similarity_search
from src.utils import get_logger, RAGError

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are ConcallIQ, an expert financial analyst assistant specializing in earnings call analysis.

You have access to concall transcripts and must answer questions based strictly on the provided context.

Guidelines:
- Quote specific numbers, percentages, and statements when available
- Mention which page or section the info comes from when possible
- If the context doesn't contain the answer, say so clearly — don't hallucinate
- Be concise but thorough; use bullet points for multi-part answers
- Use financial terminology appropriately
- Always cite the source document when referencing specific facts
"""


def get_llm(model: str = "llama3-8b-8192") -> ChatOpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
    return ChatOpenAI(
        model=model,
        temperature=0.1,
        openai_api_key=api_key,
        openai_api_base=base_url,
    )


def build_context(docs) -> str:
    """Format retrieved documents into a context string."""
    parts = []
    for i, doc in enumerate(docs, 1):
        meta = doc.metadata
        parts.append(
            f"[Source {i}: {meta.get('source', 'unknown')} | Page {meta.get('page_num', '?')}]\n"
            f"{doc.page_content}"
        )
    return "\n\n---\n\n".join(parts)


def answer_question(
    question: str,
    company: str = "",
    k: int = 6,
    model: str = "llama3-8b-8192",
) -> Dict[str, Any]:
    """
    Full RAG pipeline: retrieve → augment → generate.

    Args:
        question: User's question about the concall.
        company: Filter results to a specific company.
        k: Number of chunks to retrieve.
        model: OpenAI model to use.

    Returns:
        Dict with 'answer', 'sources', 'context'
    """
    logger.info(f"RAG query: '{question}' | company: '{company}'")

    # 1. Retrieve
    docs = similarity_search(question, k=k, company_filter=company)
    if not docs:
        return {
            "answer": "No relevant concall data found. Please upload a PDF first.",
            "sources": [],
            "context": "",
        }

    # 2. Build context
    context = build_context(docs)

    # 3. Generate
    llm = get_llm(model)
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""Context from concall transcripts:

{context}

---

Question: {question}

Please answer based only on the context above.""")
    ]

    try:
        response = llm.invoke(messages)
        answer = response.content
    except Exception as e:
        raise RAGError(f"LLM generation failed: {e}") from e

    # 4. Collect sources
    sources = []
    seen = set()
    for doc in docs:
        src = doc.metadata.get("source", "unknown")
        pg = doc.metadata.get("page_num", "?")
        key = f"{src}:{pg}"
        if key not in seen:
            sources.append({"source": src, "page": pg})
            seen.add(key)

    logger.info(f"Generated answer ({len(answer)} chars) from {len(sources)} sources")

    return {
        "answer": answer,
        "sources": sources,
        "context": context,
    }


def summarize_concall(company: str, k: int = 15) -> str:
    """Generate a high-level summary of an indexed concall."""
    result = answer_question(
        question=(
            "Provide a comprehensive summary of this earnings call covering: "
            "1) Key financial metrics (revenue, profit, margins, EPS), "
            "2) Management guidance and outlook, "
            "3) Major business updates, "
            "4) Analyst concerns raised, "
            "5) Key risks mentioned."
        ),
        company=company,
        k=k,
    )
    return result["answer"]
