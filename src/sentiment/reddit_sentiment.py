"""
Reddit Sentiment — scrapes relevant subreddits via PRAW (100% Free).
"""

import os
from typing import List, Dict, Any

from src.utils import get_logger, SentimentError

logger = get_logger(__name__)

FINANCE_SUBS = ["investing", "stocks", "IndianStockMarket", "SecurityAnalysis", "ValueInvesting"]


def fetch_reddit_posts(company: str, limit: int = 20) -> List[Dict]:
    """
    Fetch recent Reddit posts mentioning the company.
    Returns empty list if PRAW credentials not configured.
    """
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "ConcallIQ/1.0")

    if not client_id or not client_secret:
        logger.warning("Reddit credentials not set — skipping social sentiment.")
        return []

    try:
        import praw
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )

        posts = []
        for sub_name in FINANCE_SUBS:
            subreddit = reddit.subreddit(sub_name)
            for post in subreddit.search(company, limit=limit // len(FINANCE_SUBS), sort="new"):
                posts.append({
                    "subreddit": sub_name,
                    "title": post.title,
                    "score": post.score,
                    "upvote_ratio": post.upvote_ratio,
                    "num_comments": post.num_comments,
                    "url": f"https://reddit.com{post.permalink}",
                    "selftext": post.selftext[:300],
                })

        logger.info(f"Fetched {len(posts)} Reddit posts for '{company}'")
        return posts

    except Exception as e:
        logger.error(f"Reddit fetch error: {e}")
        return []


def analyze_reddit_sentiment(company: str) -> Dict[str, Any]:
    """
    Analyze Reddit sentiment for a company.

    Returns:
        Dict with score, label, summary, and posts.
    """
    posts = fetch_reddit_posts(company)

    if not posts:
        return {
            "score": 0.0,
            "label": "No Data",
            "summary": "Reddit credentials not configured or no posts found.",
            "posts": [],
            "post_count": 0,
        }

    # Simple heuristic: weighted by upvote ratio
    total_weight = 0.0
    weighted_score = 0.0

    for post in posts:
        weight = max(1, post.get("score", 1))
        ratio = post.get("upvote_ratio", 0.5)
        # Map upvote_ratio [0,1] to sentiment [-1, 1]
        sentiment = (ratio - 0.5) * 2
        weighted_score += sentiment * weight
        total_weight += weight

    if total_weight > 0:
        score = round(weighted_score / total_weight, 3)
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

    summary = (
        f"Analyzed {len(posts)} Reddit posts across finance subreddits. "
        f"Community sentiment appears {label.lower()} with a score of {score:.2f}."
    )

    return {
        "score": score,
        "label": label,
        "summary": summary,
        "posts": posts[:10],  # Return top 10
        "post_count": len(posts),
    }
