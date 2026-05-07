# 📊 ConcallIQ — Earnings Call Intelligence Platform

> **RAG-powered Q&A on concall PDFs + Live News & Reddit Sentiment Analysis**

Built with: `Streamlit` · `LangChain` · `ChromaDB` · `OpenAI GPT-4o` · `NewsAPI` · `PRAW (Reddit)`

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Clone the project
```bash
git clone <your-repo-url>
cd ConcallIQ
```

### Step 2: Create a virtual environment
```bash
python -m venv venv

# Activate it:
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set up API keys
Copy the `.env` file and fill in your keys:
```bash
cp .env .env.local   # or just edit .env directly
```

Edit `.env`:
```
OPENAI_API_KEY=sk-...           # Required — get at platform.openai.com
NEWS_API_KEY=your_key_here      # Free — get at newsapi.org/register
REDDIT_CLIENT_ID=...            # Optional — for Reddit sentiment
REDDIT_CLIENT_SECRET=...        # Optional
```

**Getting your free API keys:**
| API | Cost | Link |
|-----|------|------|
| OpenAI | ~$2-5 for demo | [platform.openai.com](https://platform.openai.com/api-keys) |
| NewsAPI | 100 req/day FREE | [newsapi.org/register](https://newsapi.org/register) |
| Reddit (PRAW) | 100% FREE | [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) |
| ChromaDB | 100% FREE local | No key needed |

### Step 5: Run the app
```bash
streamlit run app.py
```
Open http://localhost:8501 in your browser 🎉

---

## 📁 Project Structure
```
ConcallIQ/
│
├── src/
│   ├── ingestion/
│   │   ├── pdf_loader.py      # Load & parse concall PDFs
│   │   └── chunker.py         # Smart text chunking
│   │
│   ├── rag/
│   │   ├── embeddings.py      # OpenAI embeddings
│   │   ├── vector_store.py    # ChromaDB setup
│   │   └── retriever.py       # RAG pipeline (GPT-4o)
│   │
│   ├── sentiment/
│   │   ├── news_sentiment.py  # NewsAPI + OpenAI
│   │   └── reddit_sentiment.py # PRAW Reddit scraper
│   │
│   └── utils/
│       ├── logger.py
│       └── exception.py
│
├── data/
│   └── concalls/              # Store uploaded PDFs
│
├── app.py                     # Streamlit app
├── requirements.txt
├── .env                       # API keys (never commit this!)
├── .gitignore
└── README.md
```

---

## 🎯 Features

### Tab 1: Upload & Index
- Upload any earnings call PDF/transcript
- Automatic text extraction (pdfplumber + PyPDF2 fallback)
- Smart chunking with overlap for better retrieval
- Persistent ChromaDB storage (survives restarts)

### Tab 2: Q&A
- Ask natural language questions about concalls
- GPT-4o powered answers grounded in actual transcript
- Source citations with page numbers
- Pre-built question templates
- Auto-summary generation

### Tab 3: Sentiment
- Live news sentiment via NewsAPI + GPT scoring
- Reddit sentiment via PRAW (finance subreddits)
- Visual gauge charts
- Sentiment score: -1 (Bearish) to +1 (Bullish)

### Tab 4: Compare
- Multi-company Q&A comparison
- Cross-company sentiment charts

---

## 💰 Estimated Costs

| Operation | Model | Cost |
|-----------|-------|------|
| Index 50-page PDF | text-embedding-3-small | ~$0.002 |
| Ask a question | GPT-4o | ~$0.01 |
| Ask a question | GPT-4o-mini | ~$0.001 |
| Sentiment analysis | GPT-4o-mini | ~$0.002 |

**Total for demo: ~$2-5**

---

## 🐳 Docker (Optional)
```bash
docker build -t concalliq .
docker run -p 8501:8501 --env-file .env concalliq
```

---

## 📝 Usage Tips

1. **Best PDFs**: Official concall transcripts from company investor relations pages, BSE/NSE filings, or Seeking Alpha transcripts
2. **Company names**: Use consistent names (e.g., always "Infosys" not "Infosys Ltd" sometimes)
3. **Questions**: Be specific — "What was Q3 FY24 revenue?" works better than "How did they do?"
4. **Model**: Use `gpt-4o-mini` during testing to save costs, switch to `gpt-4o` for production quality

---

## ⚠️ Disclaimer
This tool is for educational and research purposes only. Not financial advice.
