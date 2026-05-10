from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import concall, sentiment

app = FastAPI(title="ConcallIQ API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(concall.router, prefix="/api/concall", tags=["concall"])
app.include_router(sentiment.router, prefix="/api/sentiment", tags=["sentiment"])

@app.get("/")
def root():
    return {"status": "ConcallIQ API running"}