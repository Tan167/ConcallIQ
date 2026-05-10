import { useState } from "react"
import { TrendingUp, TrendingDown, Minus, Loader, Newspaper, MessageCircle } from "lucide-react"
import axios from "axios"
import { RadialBarChart, RadialBar, ResponsiveContainer, PolarAngleAxis } from "recharts"

function ScoreGauge({ score, label }) {
  const color = score > 0.2 ? "#00c97a" : score < -0.2 ? "#ff4c4c" : "#f5a623"
  const data = [{ value: Math.abs(score) * 100, fill: color }]

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-36 h-36">
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart
            innerRadius="70%"
            outerRadius="100%"
            data={data}
            startAngle={90}
            endAngle={-270}
          >
            <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
            <RadialBar dataKey="value" cornerRadius={4} background={{ fill: "#1a2332" }} />
          </RadialBarChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold" style={{ color }}>
            {score > 0 ? "+" : ""}{score.toFixed(2)}
          </span>
          <span className="text-xs text-[#4a5568] mt-1">{label}</span>
        </div>
      </div>
      <div className="flex items-center gap-1 mt-2">
        {score > 0.2 ? <TrendingUp size={14} color="#00c97a" /> :
         score < -0.2 ? <TrendingDown size={14} color="#ff4c4c" /> :
         <Minus size={14} color="#f5a623" />}
        <span className="text-xs" style={{ color: score > 0.2 ? "#00c97a" : score < -0.2 ? "#ff4c4c" : "#f5a623" }}>
          {score > 0.2 ? "Bullish" : score < -0.2 ? "Bearish" : "Neutral"}
        </span>
      </div>
    </div>
  )
}

export default function SentimentPage() {
  const [company, setCompany] = useState("")
  const [loading, setLoading] = useState(false)
  const [news, setNews] = useState(null)
  const [reddit, setReddit] = useState(null)
  const [error, setError] = useState(null)

  const analyze = async () => {
    if (!company) return
    setLoading(true)
    setError(null)
    setNews(null)
    setReddit(null)
    try {
      const [newsRes, redditRes] = await Promise.all([
        axios.post("http://localhost:8000/api/sentiment/news", { company, days_back: 7 }),
        axios.post("http://localhost:8000/api/sentiment/reddit", { company }),
      ])
      setNews(newsRes.data)
      setReddit(redditRes.data)
    } catch (e) {
      setError(e.response?.data?.detail || e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">

      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-[#f5a623] tracking-wide">Sentiment Terminal</h1>
        <p className="text-[#4a5568] text-sm mt-1">Live news and Reddit sentiment analysis</p>
      </div>

      {/* Search */}
      <div className="bg-[#0d1117] border border-[#1a2332] rounded-lg p-5">
        <div className="flex gap-3">
          <input
            type="text"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && analyze()}
            placeholder="Enter company or stock name..."
            className="flex-1 bg-[#080c0f] border border-[#1a2332] rounded px-4 py-3 text-sm text-[#e2e8f0] placeholder-[#4a5568] focus:outline-none focus:border-[#f5a623] transition-colors"
          />
          <button
            onClick={analyze}
            disabled={!company || loading}
            className="px-6 py-3 bg-[#f5a623] text-[#080c0f] rounded font-semibold text-sm disabled:opacity-30 hover:bg-[#e09415] transition-all"
          >
            {loading ? <Loader size={16} className="animate-spin" /> : "Analyze"}
          </button>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="bg-[#0d1117] border border-[#1a2332] rounded-lg p-6 flex items-center gap-3">
          <Loader size={16} className="text-[#f5a623] animate-spin" />
          <span className="text-sm text-[#8a9ab0]">Fetching live sentiment data...</span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-[#ff4c4c12] border border-[#ff4c4c30] rounded-lg p-4 text-sm text-[#ff4c4c]">
          {error}
        </div>
      )}

      {/* Results */}
      {(news || reddit) && !loading && (
        <>
          {/* Gauges */}
          <div className="grid grid-cols-2 gap-4">
            {news && (
              <div className="bg-[#0d1117] border border-[#1a2332] rounded-lg p-6 flex flex-col items-center">
                <div className="flex items-center gap-2 mb-4 self-start">
                  <Newspaper size={14} className="text-[#f5a623]" />
                  <span className="text-xs text-[#f5a623] uppercase tracking-widest">News Sentiment</span>
                </div>
                <ScoreGauge score={news.score} label={news.label} />
                <p className="text-xs text-[#4a5568] text-center mt-4">{news.summary}</p>
              </div>
            )}
            {reddit && (
              <div className="bg-[#0d1117] border border-[#1a2332] rounded-lg p-6 flex flex-col items-center">
                <div className="flex items-center gap-2 mb-4 self-start">
                  <MessageCircle size={14} className="text-[#f5a623]" />
                  <span className="text-xs text-[#f5a623] uppercase tracking-widest">Reddit Sentiment</span>
                </div>
                <ScoreGauge score={reddit.score} label={reddit.label} />
                <p className="text-xs text-[#4a5568] text-center mt-4">{reddit.summary}</p>
              </div>
            )}
          </div>

          {/* News Articles */}
          {news?.articles?.length > 0 && (
            <div className="bg-[#0d1117] border border-[#1a2332] rounded-lg p-5 space-y-3">
              <p className="text-xs text-[#4a5568] uppercase tracking-widest">Recent Headlines</p>
              {news.articles.slice(0, 5).map((a, i) => (
                <div key={i} className="border-b border-[#1a2332] pb-3 last:border-0 last:pb-0">
                  <p className="text-sm text-[#c8d6e5]">{a.title}</p>
                  <p className="text-xs text-[#4a5568] mt-1">{a.source} · {a.published_at?.slice(0, 10)}</p>
                </div>
              ))}
            </div>
          )}

          {/* Reddit Posts */}
          {reddit?.posts?.length > 0 && (
            <div className="bg-[#0d1117] border border-[#1a2332] rounded-lg p-5 space-y-3">
              <p className="text-xs text-[#4a5568] uppercase tracking-widest">Top Reddit Posts</p>
              {reddit.posts.slice(0, 3).map((p, i) => (
                <div key={i} className="border-b border-[#1a2332] pb-3 last:border-0 last:pb-0">
                  <p className="text-sm text-[#c8d6e5]">{p.title}</p>
                  <p className="text-xs text-[#4a5568] mt-1">r/{p.subreddit} · ⬆ {p.score} · 💬 {p.num_comments}</p>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}