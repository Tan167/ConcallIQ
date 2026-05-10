from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.sentiment import analyze_news_sentiment, analyze_reddit_sentiment

router = APIRouter()

class SentimentRequest(BaseModel):
    company: str
    days_back: int = 7

@router.post("/news")
async def news_sentiment(req: SentimentRequest):
    try:
        result = analyze_news_sentiment(req.company, days_back=req.days_back)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reddit")
async def reddit_sentiment(req: SentimentRequest):
    try:
        result = analyze_reddit_sentiment(req.company)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare")
async def compare_sentiment(companies: list[str]):
    try:
        results = []
        for company in companies:
            news = analyze_news_sentiment(company, days_back=7)
            results.append({
                "company": company,
                "score": news["score"],
                "label": news["label"],
            })
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))