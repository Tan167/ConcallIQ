import { useState } from "react"
import { BarChart2, Loader, CheckSquare, Square, TrendingUp, TrendingDown, Minus } from "lucide-react"
import axios from "axios"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts"

const COLORS = ["#f5a623", "#00c97a", "#4a9eff", "#ff4c4c", "#b388ff"]

function CompanySelector({ companies, selected, onToggle }) {
  return (
    <div className="flex flex-wrap gap-2">
      {companies.map((c, i) => (
        <button
          key={c}
          onClick={() => onToggle(c)}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold tracking-wider uppercase transition-all border
            ${selected.includes(c)
              ? "text-[#080c0f] border-transparent"
              : "border-[#1e2d3d] text-[#5a7a94] hover:border-[#f5a623] hover:text-[#f5a623]"
            }`}
          style={selected.includes(c) ? { backgroundColor: COLORS[i % COLORS.length], borderColor: COLORS[i % COLORS.length] } : {}}
        >
          {selected.includes(c) ? <CheckSquare size={12} /> : <Square size={12} />}
          {c}
        </button>
      ))}
    </div>
  )
}

export default function ComparePage({ companies, model }) {
  const [question, setQuestion] = useState("What was the revenue growth this quarter?")
  const [selectedQA, setSelectedQA] = useState([])
  const [selectedSentiment, setSelectedSentiment] = useState([])
  const [qaResults, setQaResults] = useState(null)
  const [sentimentResults, setSentimentResults] = useState(null)
  const [loadingQA, setLoadingQA] = useState(false)
  const [loadingSentiment, setLoadingSentiment] = useState(false)

  const toggleQA = (c) => setSelectedQA((prev) => prev.includes(c) ? prev.filter((x) => x !== c) : [...prev, c])
  const toggleSentiment = (c) => setSelectedSentiment((prev) => prev.includes(c) ? prev.filter((x) => x !== c) : [...prev, c])

  const compareQA = async () => {
    if (!selectedQA.length || !question) return
    setLoadingQA(true)
    setQaResults(null)
    try {
      const answers = await Promise.all(
        selectedQA.map((c) =>
          axios.post("http://localhost:8000/api/concall/ask", {
            question, company: c, k: 5, model,
          }).then((r) => ({ company: c, answer: r.data.answer }))
        )
      )
      setQaResults(answers)
    } catch (e) {
      setQaResults([{ company: "Error", answer: e.message }])
    } finally {
      setLoadingQA(false)
    }
  }

  const compareSentiment = async () => {
    if (!selectedSentiment.length) return
    setLoadingSentiment(true)
    setSentimentResults(null)
    try {
      const results = await Promise.all(
        selectedSentiment.map((c) =>
          axios.post("http://localhost:8000/api/sentiment/news", { company: c, days_back: 7 })
            .then((r) => ({ company: c, score: r.data.score, label: r.data.label }))
        )
      )
      setSentimentResults(results)
    } catch (e) {
      setSentimentResults([])
    } finally {
      setLoadingSentiment(false)
    }
  }

  if (companies.length < 2) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-[#0a0e13] border border-[#1e2d3d] rounded-xl p-16 text-center">
          <BarChart2 size={48} className="text-[#1e2d3d] mx-auto mb-4" />
          <p className="text-[#3d5166] text-sm tracking-wide">Index at least 2 companies to compare</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">

      {/* ── Section 1: Q&A Comparison ── */}
      <div className="bg-[#0a0e13] border border-[#1e2d3d] rounded-xl p-7 space-y-5">
        <div className="flex items-center gap-3 pb-4 border-b border-[#1e2d3d]">
          <div className="w-1 h-5 bg-[#f5a623] rounded-full" />
          <div>
            <h2 className="text-[13px] font-bold text-white tracking-widest uppercase">Q&A Comparison</h2>
            <p className="text-[11px] text-[#3d5166] mt-0.5">Ask the same question across multiple concalls</p>
          </div>
        </div>

        {/* Company selector */}
        <div className="space-y-2">
          <p className="text-[11px] text-[#3d5166] tracking-widest uppercase">Select Companies</p>
          <CompanySelector companies={companies} selected={selectedQA} onToggle={toggleQA} />
        </div>

        {/* Question */}
        <div className="space-y-2">
          <p className="text-[11px] text-[#3d5166] tracking-widest uppercase">Question</p>
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className="w-full bg-[#080c0f] border border-[#1e2d3d] rounded-lg px-5 py-4 text-sm text-[#e2e8f0] placeholder-[#2a3d4d] focus:outline-none focus:border-[#f5a623] transition-colors"
          />
        </div>

        <button
          onClick={compareQA}
          disabled={selectedQA.length < 2 || !question || loadingQA}
          className="w-full py-4 bg-[#f5a623] text-[#080c0f] rounded-lg font-bold text-sm uppercase tracking-widest disabled:opacity-20 hover:bg-[#e09415] transition-all"
        >
          {loadingQA
            ? <span className="flex items-center justify-center gap-2"><Loader size={14} className="animate-spin" /> Comparing...</span>
            : "⚡ Compare Companies →"
          }
        </button>

        {/* Q&A Results */}
        {qaResults && !loadingQA && (
          <div className="space-y-3 pt-2">
            {qaResults.map((r, i) => (
              <div key={r.company} className="bg-[#080c0f] border border-[#1e2d3d] rounded-lg p-5 hover:border-[#f5a62340] transition-all">
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: COLORS[i % COLORS.length] }} />
                  <span className="text-sm font-bold tracking-wider" style={{ color: COLORS[i % COLORS.length] }}>
                    {r.company}
                  </span>
                </div>
                <div className="border-l-2 pl-4 text-sm text-[#8a9ab0] leading-7"
                  style={{ borderColor: COLORS[i % COLORS.length] }}>
                  {r.answer}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ── Section 2: Sentiment Comparison ── */}
      <div className="bg-[#0a0e13] border border-[#1e2d3d] rounded-xl p-7 space-y-5">
        <div className="flex items-center gap-3 pb-4 border-b border-[#1e2d3d]">
          <div className="w-1 h-5 bg-[#00c97a] rounded-full" />
          <div>
            <h2 className="text-[13px] font-bold text-white tracking-widest uppercase">Sentiment Comparison</h2>
            <p className="text-[11px] text-[#3d5166] mt-0.5">Compare live news sentiment across companies</p>
          </div>
        </div>

        <div className="space-y-2">
          <p className="text-[11px] text-[#3d5166] tracking-widest uppercase">Select Companies</p>
          <CompanySelector companies={companies} selected={selectedSentiment} onToggle={toggleSentiment} />
        </div>

        <button
          onClick={compareSentiment}
          disabled={selectedSentiment.length < 2 || loadingSentiment}
          className="w-full py-4 bg-[#00c97a] text-[#080c0f] rounded-lg font-bold text-sm uppercase tracking-widest disabled:opacity-20 hover:bg-[#00b06a] transition-all"
        >
          {loadingSentiment
            ? <span className="flex items-center justify-center gap-2"><Loader size={14} className="animate-spin" /> Fetching Sentiment...</span>
            : "📊 Compare News Sentiment →"
          }
        </button>

        {/* Sentiment Results */}
        {sentimentResults && !loadingSentiment && (
          <div className="space-y-4">
            {/* Bar Chart */}
            <div className="bg-[#080c0f] border border-[#1e2d3d] rounded-lg p-5">
              <p className="text-[11px] text-[#3d5166] tracking-widest uppercase mb-4">Sentiment Score Chart</p>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={sentimentResults} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                  <XAxis dataKey="company" tick={{ fill: "#5a7a94", fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis domain={[-1, 1]} tick={{ fill: "#5a7a94", fontSize: 11 }} axisLine={false} tickLine={false} />
                  <Tooltip
                    contentStyle={{ background: "#0d1520", border: "1px solid #1e2d3d", borderRadius: 8, fontSize: 12 }}
                    labelStyle={{ color: "#f5a623" }}
                    itemStyle={{ color: "#e2e8f0" }}
                  />
                  <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                    {sentimentResults.map((r, i) => (
                      <Cell key={i} fill={r.score > 0.2 ? "#00c97a" : r.score < -0.2 ? "#ff4c4c" : "#f5a623"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Score Cards */}
            <div className="grid grid-cols-3 gap-3">
              {sentimentResults.map((r, i) => {
                const color = r.score > 0.2 ? "#00c97a" : r.score < -0.2 ? "#ff4c4c" : "#f5a623"
                const Icon = r.score > 0.2 ? TrendingUp : r.score < -0.2 ? TrendingDown : Minus
                return (
                  <div key={r.company} className="bg-[#080c0f] border border-[#1e2d3d] rounded-lg p-4 text-center">
                    <p className="text-[11px] text-[#3d5166] tracking-wider uppercase mb-2">{r.company}</p>
                    <Icon size={20} className="mx-auto mb-2" style={{ color }} />
                    <p className="text-2xl font-bold" style={{ color }}>
                      {r.score > 0 ? "+" : ""}{r.score.toFixed(2)}
                    </p>
                    <p className="text-[10px] text-[#3d5166] mt-1">{r.label}</p>
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}