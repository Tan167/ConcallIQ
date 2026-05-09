"""
StockTwits Sentiment — fetches retail investor sentiment (100% Free, no API key needed).
"""

from typing import List, Dict, Any
import requests

from src.utils import get_logger

logger = get_logger(__name__)


def company_to_symbol(company: str) -> str:
    """
    Clean and convert company name/input to StockTwits symbol.
    No yfinance — just clean the input directly.
    """
    clean = company.upper().strip()
    clean = clean.replace(".NSE", "").replace(".BSE", "").replace(".NS", "").replace(" ", "")
    return clean


def fetch_stocktwits_posts(company: str, limit: int = 30) -> List[Dict]:
    """
    Fetch recent StockTwits messages for a company.
    No API key required.
    Tries SYMBOL.NSE first (Indian stocks), then plain SYMBOL (US stocks).
    """
    symbol = company_to_symbol(company)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    for ticker in [f"{symbol}.NSE", symbol]:
        url = f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json"
        try:
            resp = requests.get(url, headers=headers, timeout=10)

            if resp.status_code in [403, 404]:
                logger.warning(f"StockTwits: {resp.status_code} for '{ticker}', trying next format...")
                continue

            resp.raise_for_status()
            data = resp.json()

            posts = []
            for msg in data.get("messages", [])[:limit]:
                sentiment = None
                if msg.get("entities", {}).get("sentiment"):
                    sentiment = msg["entities"]["sentiment"].get("basic")

                posts.append({
                    "id": msg.get("id"),
                    "body": msg.get("body", "")[:200],
                    "sentiment": sentiment,
                    "likes": msg.get("likes", {}).get("total", 0),
                    "created_at": msg.get("created_at", ""),
                    "username": msg.get("user", {}).get("username", "unknown"),
                    "subreddit": "StockTwits",
                    "title": msg.get("body", "")[:100],
                    "score": msg.get("likes", {}).get("total", 0),
                    "num_comments": 0,
                })

            if posts:
                logger.info(f"Fetched {len(posts)} StockTwits messages for '{ticker}'")
                return posts

        except Exception as e:
            logger.error(f"StockTwits fetch error for {ticker}: {e}")
            continue

    return []


def analyze_reddit_sentiment(company: str) -> Dict[str, Any]:
    """
    Analyze StockTwits sentiment for a company.
    Function name kept as analyze_reddit_sentiment for app.py compatibility.
    """
    posts = fetch_stocktwits_posts(company)

    if not posts:
        return {
            "score": 0.0,
            "label": "No Data",
            "summary": f"No StockTwits data found for '{company}'. Try using the exact NSE ticker e.g. NETWEB, INFY, TCS.",
            "posts": [],
            "post_count": 0,
        }

    # Use StockTwits built-in bullish/bearish tags for scoring
    bullish = sum(1 for p in posts if p["sentiment"] == "Bullish")
    bearish = sum(1 for p in posts if p["sentiment"] == "Bearish")
    total_tagged = bullish + bearish

    if total_tagged > 0:
        score = round((bullish - bearish) / total_tagged, 3)
    else:
        score = 0.0

    score = max(-1.0, min(1.0, score))

    if score > 0.3:
        label = "Bullish"
    elif score > 0.1:
        label = "Slightly Bullish"
    elif score < -0.3:
        label = "Bearish"
    elif score < -0.1:
        label = "Slightly Bearish"
    else:
        label = "Neutral"

    symbol = company_to_symbol(company)
    summary = (
        f"Analyzed {len(posts)} StockTwits messages for ${symbol}. "
        f"{bullish} bullish 📈 vs {bearish} bearish 📉 tagged posts. "
        f"Retail sentiment is {label.lower()} (score: {score:.2f})."
    )

    return {
        "score": score,
        "label": label,
        "summary": summary,
        "posts": posts[:10],
        "post_count": len(posts),
    }