"""
News Sentiment — fetches recent news articles via NewsAPI and scores them with GPT.
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

import requests
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.utils import get_logger, SentimentError

logger = get_logger(__name__)


def fetch_news(company: str, days_back: int = 7, max_articles: int = 10) -> List[Dict]:
    """
    Fetch recent news articles about a company from NewsAPI.

    Args:
        company: Company name to search for.
        days_back: How many days back to search.
        max_articles: Max articles to return.

    Returns:
        List of article dicts.
    """
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        logger.warning("NEWS_API_KEY not set — returning empty news.")
        return []

    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": f"{company} stock earnings",
        "from": from_date,
        "sortBy": "relevancy",
        "language": "en",
        "pageSize": max_articles,
        "apiKey": api_key,
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        articles = []
        for art in data.get("articles", []):
            if not art.get("title") or "[Removed]" in art.get("title", ""):
                continue
            articles.append({
                "title": art["title"],
                "description": art.get("description", ""),
                "url": art.get("url", ""),
                "published_at": art.get("publishedAt", ""),
                "source": art.get("source", {}).get("name", "Unknown"),
            })

        logger.info(f"Fetched {len(articles)} articles for '{company}'")
        return articles

    except Exception as e:
        logger.error(f"NewsAPI error: {e}")
        return []


def analyze_news_sentiment(company: str, days_back: int = 7) -> Dict[str, Any]:
    """
    Fetch news and score overall sentiment using GPT.

    Returns:
        Dict with score (-1 to 1), label, summary, and articles.
    """
    articles = fetch_news(company, days_back=days_back)

    if not articles:
        return {
            "score": 0.0,
            "label": "Neutral",
            "summary": "No recent news found.",
            "articles": [],
            "article_count": 0,
        }

    # Prepare headlines for GPT
    headlines = "\n".join(
        f"- [{a['source']}] {a['title']}: {a['description'][:100]}"
        for a in articles
    )

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SentimentError("OPENAI_API_KEY not set.")

    llm = ChatOpenAI(
    model="llama3-8b-8192",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    openai_api_base=os.getenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1"),
)

    prompt = f"""Analyze the following news headlines about {company} and provide:
1. Overall sentiment score from -1.0 (very negative) to 1.0 (very positive)
2. Sentiment label: Strongly Bullish / Bullish / Neutral / Bearish / Strongly Bearish
3. 2-3 sentence summary of key themes

Headlines:
{headlines}

Respond in this exact format:
SCORE: [number]
LABEL: [label]
SUMMARY: [summary]"""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        text = response.content

        score = 0.0
        label = "Neutral"
        summary = ""

        for line in text.strip().split("\n"):
            if line.startswith("SCORE:"):
                try:
                    score = float(line.replace("SCORE:", "").strip())
                    score = max(-1.0, min(1.0, score))
                except ValueError:
                    pass
            elif line.startswith("LABEL:"):
                label = line.replace("LABEL:", "").strip()
            elif line.startswith("SUMMARY:"):
                summary = line.replace("SUMMARY:", "").strip()

        return {
            "score": score,
            "label": label,
            "summary": summary,
            "articles": articles,
            "article_count": len(articles),
        }

    except Exception as e:
        raise SentimentError(f"Sentiment analysis failed: {e}") from e
