# 📊 ConcallIQ — Earnings Call Intelligence Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red?style=for-the-badge&logo=streamlit)
![LangChain](https://img.shields.io/badge/LangChain-0.2-green?style=for-the-badge)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Local-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Ask questions about any earnings call transcript using RAG + LLM. Get live news and Reddit sentiment. Built for analysts, by a developer.**

[Features](#-features) • [Demo](#-demo) • [Tech Stack](#-tech-stack) • [Setup](#-quick-start) • [Usage](#-usage)

</div>

---

## 🚀 What is ConcallIQ?

ConcallIQ is an AI-powered earnings call analysis tool that lets you:

- 📄 **Upload any concall PDF** and instantly ask questions about it
- 🤖 **Get precise, cited answers** grounded in the actual transcript — no hallucinations
- 📰 **Fetch live news sentiment** about any stock using NewsAPI + LLM scoring
- 🟠 **Analyze Reddit sentiment** from finance communities
- 📊 **Compare multiple companies** side by side

> This is the kind of tool used by hedge funds and trading firms — built from scratch with open-source tools and free APIs.

---

## ✨ Features

| Feature | Description | Tech |
|--------|-------------|------|
| 📤 PDF Upload & Index | Upload concall transcripts, auto-chunked and embedded | PyPDF2 + pdfplumber |
| 💬 RAG Q&A | Ask natural language questions, get cited answers | LangChain + ChromaDB + Groq |
| 📋 Auto Summary | One-click comprehensive concall summary | LLaMA3 70B |
| 📰 News Sentiment | Live news fetched and scored -1 to +1 | NewsAPI + LLM |
| 🟠 Reddit Sentiment | Finance subreddit sentiment analysis | PRAW (Free) |
| 📊 Multi-Company Compare | Ask same question across multiple concalls | Multi-doc RAG |
| 📈 Sentiment Charts | Visual gauge charts for sentiment scores | Plotly |

---

## 🏗️ How It Works

```
User uploads Concall PDF/Transcript
            ↓
RAG chunks + indexes it (ChromaDB + Local Embeddings)
            ↓
User asks → "What did CEO say about margins?"
            ↓
RAG retrieves relevant chunks → LLM answers with citations
            +
OpenAI fetches latest news sentiment
            +
Reddit community sentiment (PRAW)
            ↓
Final Answer = Concall Insight + Market Sentiment
```

---

## 🛠️ Tech Stack

```
Frontend          →  Streamlit
RAG Framework     →  LangChain
Vector Store      →  ChromaDB (local, free)
LLM               →  Groq (LLaMA3 70B / Mixtral) — Free tier
Embeddings        →  all-MiniLM-L6-v2 (local, free)
PDF Parser        →  pdfplumber / PyPDF2
News Sentiment    →  NewsAPI + Groq LLM
Social Sentiment  →  PRAW Reddit — Free
Visualization     →  Plotly
```

---

## 📁 Project Structure

```
ConcallIQ/
│
├── src/
│   ├── ingestion/
│   │   ├── pdf_loader.py       # Load & parse concall PDFs
│   │   └── chunker.py          # Smart text chunking with overlap
│   │
│   ├── rag/
│   │   ├── embeddings.py       # Local HuggingFace embeddings
│   │   ├── vector_store.py     # ChromaDB setup & retrieval
│   │   └── retriever.py        # Full RAG pipeline
│   │
│   ├── sentiment/
│   │   ├── news_sentiment.py   # NewsAPI + LLM scoring
│   │   └── reddit_sentiment.py # PRAW Reddit scraper
│   │
│   └── utils/
│       ├── logger.py
│       └── exception.py
│
├── data/concalls/              # Store uploaded PDFs
├── app.py                      # Streamlit UI (4 tabs)
├── requirements.txt
├── .env                        # API keys (never commit!)
└── README.md
```

---

## ⚡ Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/ConcallIQ.git
cd ConcallIQ
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up API keys
Create a `.env` file:
```env
OPENAI_API_KEY=your_groq_key_here        # Get free at console.groq.com
NEWS_API_KEY=your_newsapi_key_here       # Get free at newsapi.org
OPENAI_BASE_URL=https://api.groq.com/openai/v1

# Optional — Reddit sentiment
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret
REDDIT_USER_AGENT=ConcallIQ/1.0 by u/yourusername
```

### 5. Run the app
```bash
streamlit run app.py
```
Open **http://localhost:8501** 🎉

---

## 🔑 API Keys (All Free!)

| Service | Cost | Link | Used For |
|---------|------|------|----------|
| Groq | ✅ Free | [console.groq.com](https://console.groq.com) | LLM inference |
| NewsAPI | ✅ Free (100 req/day) | [newsapi.org](https://newsapi.org/register) | Live news |
| Reddit PRAW | ✅ Free | [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) | Social sentiment |
| ChromaDB | ✅ Free (local) | Built-in | Vector storage |
| HuggingFace Embeddings | ✅ Free (local) | Built-in | Text embeddings |

**Total cost to run: $0** 🎉

---

## 📖 Usage Guide

### Upload & Index a Concall
1. Go to **Upload & Index** tab
2. Upload a concall PDF (BSE/NSE filings, investor relations pages)
3. Enter the company name (e.g. `Infosys`)
4. Click **🚀 Index Concall** — done in ~30 seconds

### Ask Questions
1. Go to **Q&A** tab
2. Select company or ask across all
3. Use preset questions or type your own:
   - *"What was Q3 revenue growth?"*
   - *"What did the CEO say about AI investments?"*
   - *"What are the key risks for next quarter?"*

### Get Sentiment
1. Go to **Sentiment** tab
2. Type any company/stock name
3. Get live news + Reddit sentiment scores with visual gauges

### Where to find Concall PDFs
- **BSE India** → [bseindia.com](https://bseindia.com) → Search company → Announcements
- **NSE** → [nseindia.com](https://nseindia.com) → Company page → Transcripts  
- Company investor relations pages

---

## 🤖 Supported LLM Models (via Groq — Free)

| Model | Speed | Best For |
|-------|-------|----------|
| `llama3-8b-8192` | ⚡ Fastest | Quick Q&A |
| `llama3-70b-8192` | 🎯 Best quality | Detailed analysis |
| `mixtral-8x7b-32768` | ⚡ Fast | Long transcripts (32K context) |
| `gemma2-9b-it` | ⚡ Fast | Balanced performance |

---

## 🙋 FAQ

**Q: Does it work with Hindi/regional language concalls?**  
A: It works best with English transcripts. Mixed language may reduce accuracy.

**Q: How many PDFs can I index?**  
A: Unlimited — ChromaDB is local and only limited by your disk space.

**Q: Is my data sent to any server?**  
A: PDF text is sent to Groq for LLM inference. ChromaDB and embeddings run 100% locally.

**Q: Can I use OpenAI instead of Groq?**  
A: Yes — set `OPENAI_BASE_URL` to `https://api.openai.com/v1` and use `gpt-4o` as the model.

---

## ⚠️ Disclaimer

This tool is for **educational and research purposes only**.  
It is **not financial advice**. Always do your own research before making investment decisions.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

<div align="center">
Built with ❤️ using Streamlit, LangChain, and Groq
</div>
