"""
ConcallIQ — Earnings Call Intelligence Platform
A RAG + Sentiment analysis tool for concall PDFs.

Run with:  streamlit run app.py
"""

import os
import sys
import time
from pathlib import Path

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from src.ingestion import load_pdf_from_bytes, chunk_pages
from src.rag import index_chunks, answer_question, summarize_concall, list_indexed_companies, delete_company
from src.sentiment import analyze_news_sentiment, analyze_reddit_sentiment
from src.utils import get_logger

logger = get_logger("app")

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ConcallIQ",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .main { background-color: #0f0f0f; }
    .stApp { background-color: #0f0f0f; }

    .brand-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border: 1px solid #e94560;
        border-radius: 12px;
        padding: 24px 32px;
        margin-bottom: 24px;
    }
    .brand-title {
        font-size: 2.4rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
    }
    .brand-sub {
        color: #a0a0b0;
        font-size: 1rem;
        margin-top: 4px;
    }
    .brand-accent { color: #e94560; }

    .metric-card {
        background: #1a1a2e;
        border: 1px solid #2a2a4e;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #e94560;
    }
    .metric-label {
        color: #a0a0b0;
        font-size: 0.85rem;
        margin-top: 4px;
    }

    .answer-box {
        background: #1a1a2e;
        border-left: 4px solid #e94560;
        border-radius: 8px;
        padding: 20px 24px;
        margin: 16px 0;
        color: #e0e0f0;
        line-height: 1.7;
    }

    .source-chip {
        display: inline-block;
        background: #0f3460;
        color: #7eb8f7;
        border: 1px solid #1a5296;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.78rem;
        margin: 3px;
    }

    .sentiment-gauge {
        text-align: center;
        padding: 20px;
    }

    .news-card {
        background: #1a1a2e;
        border: 1px solid #2a2a4e;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 8px 0;
    }
    .news-title { color: #e0e0f0; font-weight: 500; font-size: 0.92rem; }
    .news-meta { color: #6060a0; font-size: 0.78rem; margin-top: 4px; }

    .upload-area {
        background: #1a1a2e;
        border: 2px dashed #e94560;
        border-radius: 12px;
        padding: 32px;
        text-align: center;
        color: #a0a0b0;
    }

    div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #e94560, #c73652);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 24px;
        transition: all 0.2s;
    }
    div[data-testid="stButton"] > button:hover {
        background: linear-gradient(135deg, #ff5577, #e94560);
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(233, 69, 96, 0.4);
    }

    .stSelectbox > div, .stTextInput > div > div {
        background: #1a1a2e;
        border-color: #2a2a4e;
        color: #e0e0f0;
    }

    .sidebar .stSelectbox label, .sidebar label { color: #a0a0b0; }

    h1, h2, h3 { color: #ffffff; }
    p { color: #c0c0d0; }

    .stSuccess { background-color: #0d2d1e !important; }
    .stError { background-color: #2d0d0d !important; }
    .stInfo { background-color: #0d1a2d !important; }
    .stWarning { background-color: #2d1e0d !important; }
</style>
""", unsafe_allow_html=True)


# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="brand-header">
    <h1 class="brand-title">📊 Concall<span class="brand-accent">IQ</span></h1>
    <p class="brand-sub">Earnings Call Intelligence — RAG Q&A + Live Market Sentiment</p>
</div>
""", unsafe_allow_html=True)


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")

    # API key check
    openai_key = os.getenv("OPENAI_API_KEY", "")
    news_key = os.getenv("NEWS_API_KEY", "")

    if not openai_key:
        openai_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key

    if not news_key:
        news_key = st.text_input("NewsAPI Key", type="password", placeholder="Get free at newsapi.org")
        if news_key:
            os.environ["NEWS_API_KEY"] = news_key

    if openai_key:
        st.success("✅ OpenAI connected")
    else:
        st.error("❌ OpenAI key required")

    if news_key:
        st.success("✅ NewsAPI connected")
    else:
        st.warning("⚠️ NewsAPI key for live news")

    st.divider()

    # Indexed companies
    st.markdown("### 📁 Indexed Concalls")
    companies = list_indexed_companies()
    if companies:
        for c in companies:
            col1, col2 = st.columns([3, 1])
            col1.markdown(f"🏢 **{c}**")
            if col2.button("🗑️", key=f"del_{c}", help=f"Delete {c}"):
                delete_company(c)
                st.rerun()
    else:
        st.info("No concalls indexed yet.\nUpload a PDF to get started.")

    st.divider()

    st.markdown("### 🤖 Model")
    # NEW - working
model_choice = st.selectbox(
    "LLM",
    [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "moonshotai/kimi-k2-instruct",
    ],
    help="Free models via Groq"
)

# ─── Tabs ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload & Index", "💬 Q&A", "📰 Sentiment", "📊 Compare"])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1: Upload & Index
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("## Upload Concall PDF")
    st.markdown("Upload an earnings call transcript or concall PDF to index it for Q&A.")

    col1, col2 = st.columns([2, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=["pdf"],
            help="Upload earnings call transcript, concall PDF, or investor presentation",
        )

    with col2:
        company_name = st.text_input(
            "Company Name",
            placeholder="e.g. Infosys, TCS, Reliance...",
            help="Used to tag and filter chunks",
        )

    if uploaded_file and company_name:
        if st.button("🚀 Index Concall", use_container_width=True):
            with st.spinner("Loading and indexing PDF..."):
                try:
                    # Load
                    st.info("📖 Extracting text from PDF...")
                    pages = load_pdf_from_bytes(uploaded_file.read(), uploaded_file.name)
                    st.success(f"✅ Extracted {len(pages)} pages")

                    # Chunk
                    st.info("✂️ Chunking text...")
                    chunks = chunk_pages(pages)
                    st.success(f"✅ Created {len(chunks)} chunks")

                    # Index
                    st.info("🔢 Embedding and indexing into ChromaDB...")
                    n = index_chunks(chunks, company=company_name)
                    st.success(f"✅ Indexed {n} chunks for **{company_name}**")

                    st.balloons()
                    st.success(f"🎉 **{company_name}** concall is ready! Switch to Q&A tab.")
                    time.sleep(1)
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    elif uploaded_file and not company_name:
        st.warning("⚠️ Please enter a company name before indexing.")

    # Stats
    if companies:
        st.divider()
        st.markdown("### 📊 Indexed Documents")
        cols = st.columns(min(len(companies), 4))
        for i, c in enumerate(companies):
            cols[i % 4].markdown(f"""
<div class="metric-card">
    <div class="metric-value">✓</div>
    <div class="metric-label">{c}</div>
</div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 2: Q&A
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("## 💬 Ask Questions About Concalls")

    if not companies:
        st.info("📤 Please upload and index a concall PDF in the **Upload & Index** tab first.")
    else:
        col1, col2 = st.columns([2, 1])

        with col1:
            selected_company = st.selectbox("Select Company", ["All"] + companies)

        with col2:
            k_chunks = st.slider("Context chunks", 3, 15, 6, help="More chunks = more context but higher cost")

        # Preset questions
        st.markdown("**💡 Quick Questions:**")
        preset_cols = st.columns(3)
        preset_questions = [
            "What was the revenue growth this quarter?",
            "What did the CEO say about margins?",
            "What is the company's guidance for next quarter?",
            "What are the key risks mentioned?",
            "What were the analyst concerns?",
            "How is headcount changing?",
        ]
        # NEW - fixed
        if "qa_question" not in st.session_state:
            st.session_state.qa_question = ""

        for i, q in enumerate(preset_questions):
            if preset_cols[i % 3].button(q, key=f"preset_{i}", use_container_width=True):
                st.session_state.qa_question = q

        question = st.text_input(
            "Your Question",
            value=st.session_state.qa_question,
            placeholder="What did management say about AI investments?",
            key="qa_input",
        )
        st.session_state.qa_question = question

        st.divider()

       
        if st.button("🔍 Ask ConcallIQ", use_container_width=True) and question:
            if not openai_key:
                st.error("❌ OpenAI API key required.")
            else:
                with st.spinner("Searching concall and generating answer..."):
                    try:
                        company_filter = "" if selected_company == "All" else selected_company
                        result = answer_question(
                            question=question,
                            company=company_filter,
                            k=k_chunks,
                            model=model_choice,
                        )
                        st.session_state["last_answer"] = result["answer"]       # ✅ just save
                        st.session_state["last_sources"] = result.get("sources", [])  # ✅ just save
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

        # ✅ This is OUTSIDE the button block — paste this right after the block above
        if "last_answer" in st.session_state:
            st.markdown("### 🤖 Answer")
            st.markdown(f'<div class="answer-box">{st.session_state["last_answer"]}</div>', unsafe_allow_html=True)

            if st.session_state["last_sources"]:
                st.markdown("**📎 Sources:**")
                source_html = " ".join(
                    f'<span class="source-chip">📄 {s["source"]} (p.{s["page"]})</span>'
                    for s in st.session_state["last_sources"]
                )
                st.markdown(source_html, unsafe_allow_html=True)


        st.divider()

        # Summarize
        st.markdown("### 📋 Auto-Summary")
        sum_company = st.selectbox("Company to Summarize", companies, key="sum_co")
        if st.button("📝 Generate Summary", use_container_width=True):
            if not openai_key:
                st.error("❌ OpenAI key required.")
            else:
                with st.spinner(f"Generating summary for {sum_company}..."):
                    try:
                        summary = summarize_concall(sum_company)
                        st.markdown(f'<div class="answer-box">{summary}</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"❌ {str(e)}")


# ════════════════════════════════════════════════════════════════════════════
# TAB 3: Sentiment
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("## 📰 Market Sentiment Analysis")

    sentiment_company = st.text_input(
        "Company / Stock Name",
        placeholder="e.g. Infosys, TCS, Wipro, HDFC Bank...",
        key="sent_co"
    )

    col1, col2 = st.columns(2)
    days_back = col1.slider("News lookback (days)", 1, 30, 7)

    if st.button("🔍 Analyze Sentiment", use_container_width=True) and sentiment_company:
        if not openai_key:
            st.error("❌ OpenAI key required for GPT sentiment scoring.")
        else:
            col_news, col_reddit = st.columns(2)

            # News Sentiment
            with col_news:
                st.markdown("### 📰 News Sentiment")
                with st.spinner("Fetching and analyzing news..."):
                    try:
                        news_result = analyze_news_sentiment(sentiment_company, days_back=days_back)

                        score = news_result["score"]
                        label = news_result["label"]
                        color = "#00d26a" if score > 0 else "#ff4757" if score < 0 else "#ffa502"

                        # Gauge chart
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=score,
                            number={"font": {"color": color, "size": 36}},
                            gauge={
                                "axis": {"range": [-1, 1]},
                                "bar": {"color": color},
                                "steps": [
                                    {"range": [-1, -0.3], "color": "#2d0d0d"},
                                    {"range": [-0.3, 0.3], "color": "#1a1a2e"},
                                    {"range": [0.3, 1], "color": "#0d2d1e"},
                                ],
                                "threshold": {"line": {"color": color, "width": 4}, "value": score},
                            },
                            title={"text": label, "font": {"color": "#ffffff"}},
                        ))
                        fig.update_layout(
                            paper_bgcolor="#0f0f0f",
                            font={"color": "#ffffff"},
                            height=250,
                            margin=dict(t=40, b=10, l=20, r=20),
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        st.info(news_result["summary"])

                        if news_result["articles"]:
                            st.markdown("**Recent Headlines:**")
                            for art in news_result["articles"][:5]:
                                st.markdown(f"""
<div class="news-card">
    <div class="news-title">📰 {art['title']}</div>
    <div class="news-meta">🔗 {art['source']} · {art['published_at'][:10] if art['published_at'] else ''}</div>
</div>""", unsafe_allow_html=True)

                    except Exception as e:
                        st.error(f"News error: {e}")

            # Reddit Sentiment
            with col_reddit:
                st.markdown("### 🟠 StockTwits Sentiment")
                with st.spinner("Analyzing Reddit..."):
                    try:
                        reddit_result = analyze_reddit_sentiment(sentiment_company)

                        r_score = reddit_result["score"]
                        r_label = reddit_result["label"]
                        r_color = "#00d26a" if r_score > 0 else "#ff4757" if r_score < 0 else "#ffa502"

                        fig2 = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=r_score,
                            number={"font": {"color": r_color, "size": 36}},
                            gauge={
                                "axis": {"range": [-1, 1]},
                                "bar": {"color": r_color},
                                "steps": [
                                    {"range": [-1, -0.3], "color": "#2d0d0d"},
                                    {"range": [-0.3, 0.3], "color": "#1a1a2e"},
                                    {"range": [0.3, 1], "color": "#0d2d1e"},
                                ],
                            },
                            title={"text": r_label, "font": {"color": "#ffffff"}},
                        ))
                        fig2.update_layout(
                            paper_bgcolor="#0f0f0f",
                            font={"color": "#ffffff"},
                            height=250,
                            margin=dict(t=40, b=10, l=20, r=20),
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                        st.info(reddit_result["summary"])

                        if reddit_result["posts"]:
                            st.markdown("**Top Posts:**")
                            for post in reddit_result["posts"][:3]:
                                st.markdown(f"""
<div class="news-card">
    <div class="news-title">🟠 r/{post['subreddit']}: {post['title'][:80]}...</div>
    <div class="news-meta">⬆️ {post['score']} · 💬 {post['num_comments']} comments</div>
</div>""", unsafe_allow_html=True)

                    except Exception as e:
                        st.error(f"Reddit error: {e}")


# ════════════════════════════════════════════════════════════════════════════
# TAB 4: Multi-Company Compare
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("## 📊 Multi-Company Comparison")

    if len(companies) < 2:
        st.info("📤 Index at least **2 companies** to compare them.")
    else:
        compare_question = st.text_input(
            "Comparison Question",
            value="What is the revenue growth rate?",
            placeholder="Ask a question to compare across companies..."
        )

        selected_companies = st.multiselect(
            "Select Companies to Compare",
            companies,
            default=companies[:min(3, len(companies))],
        )

        if st.button("⚡ Compare", use_container_width=True) and selected_companies and compare_question:
            if not openai_key:
                st.error("❌ OpenAI key required.")
            else:
                results = {}
                with st.spinner("Querying all companies..."):
                    for comp in selected_companies:
                        try:
                            r = answer_question(compare_question, company=comp, k=5, model=model_choice)
                            results[comp] = r["answer"]
                        except Exception as e:
                            results[comp] = f"Error: {str(e)}"

                st.markdown("### 🏆 Comparison Results")
                for comp, answer in results.items():
                    with st.expander(f"🏢 {comp}", expanded=True):
                        st.markdown(f'<div class="answer-box">{answer}</div>', unsafe_allow_html=True)

        st.divider()

        # Sentiment comparison chart
        # Sentiment comparison chart
        st.markdown("### 📈 Sentiment Comparison")
        sentiment_selected = st.multiselect(
            "Select Companies for Sentiment Comparison",
            companies,
            default=companies[:min(3, len(companies))],
            key="sentiment_compare_select"
        )
        if st.button("📊 Compare News Sentiment", use_container_width=True) and sentiment_selected:
            if not openai_key:
                st.error("❌ OpenAI key required.")
            else:
                sentiment_data = []
                progress = st.progress(0)
                for i, comp in enumerate(sentiment_selected):
                    with st.spinner(f"Analyzing {comp}..."):
                        try:
                            result = analyze_news_sentiment(comp, days_back=20)
                            sentiment_data.append({
                                "Company": comp,
                                "Score": result["score"],
                                "Label": result["label"],
                            })
                        except Exception:
                            pass
                    progress.progress((i + 1) / len(companies))

                if sentiment_data:
                    df = pd.DataFrame(sentiment_data)
                    colors = ["#00d26a" if s > 0 else "#ff4757" for s in df["Score"]]

                    fig = px.bar(
                        df, x="Company", y="Score", color="Score",
                        color_continuous_scale=["#ff4757", "#ffa502", "#00d26a"],
                        range_color=[-1, 1],
                        title="News Sentiment Score by Company",
                        text="Label",
                    )
                    fig.update_layout(
                        paper_bgcolor="#0f0f0f",
                        plot_bgcolor="#1a1a2e",
                        font={"color": "#ffffff"},
                        title_font_color="#ffffff",
                        height=400,
                    )
                    st.plotly_chart(fig, use_container_width=True)

# ─── Footer ──────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="text-align:center; color:#404060; font-size:0.8rem; padding:16px 0;">
    ConcallIQ • Built with Streamlit + LangChain + ChromaDB + OpenAI<br>
    <span style="color:#e94560;">For educational and research purposes only. Not financial advice.</span>
</div>
""", unsafe_allow_html=True)
