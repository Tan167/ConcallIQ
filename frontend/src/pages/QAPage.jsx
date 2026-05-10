import { useState } from "react"
import { Search, MessageSquare, FileText, Loader } from "lucide-react"
import axios from "axios"

const presets = [
  "What was the revenue growth this quarter?",
  "What did the CEO say about margins?",
  "What is the guidance for next quarter?",
  "What are the key risks mentioned?",
  "What were the analyst concerns?",
  "How is headcount changing?",
]

export default function QAPage({ companies, model }) {
  const [question, setQuestion] = useState("")
  const [company, setCompany] = useState("All")
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState([])

  const ask = async (q) => {
    if (!q) return
    setLoading(true)
    setResult(null)
    try {
      const res = await axios.post("http://localhost:8000/api/concall/ask", {
        question: q,
        company: company === "All" ? "" : company,
        k: 6,
        model,
      })
      setResult(res.data)
      setHistory((prev) => [{ question: q, answer: res.data.answer }, ...prev.slice(0, 4)])
    } catch (e) {
      setResult({ error: e.response?.data?.detail || e.message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">

      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-[#f5a623] tracking-wide">Q&A Terminal</h1>
        <p className="text-[#4a5568] text-sm mt-1">Ask anything about indexed concalls</p>
      </div>

      {/* Controls */}
      <div className="bg-[#0d1117] border border-[#1a2332] rounded-lg p-5 space-y-4">
        
        {/* Company selector */}
        <div className="flex gap-3">
          {["All", ...companies].map((c) => (
            <button
              key={c}
              onClick={() => setCompany(c)}
              className={`px-4 py-1.5 rounded text-xs font-semibold uppercase tracking-widest transition-all
                ${company === c
                  ? "bg-[#f5a623] text-[#080c0f]"
                  : "border border-[#1a2332] text-[#4a5568] hover:border-[#f5a623] hover:text-[#f5a623]"
                }`}
            >
              {c}
            </button>
          ))}
        </div>

        {/* Preset questions */}
        <div>
          <p className="text-xs text-[#4a5568] uppercase tracking-widest mb-2">Quick Questions</p>
          <div className="grid grid-cols-2 gap-2">
            {presets.map((q) => (
              <button
                key={q}
                onClick={() => { setQuestion(q); ask(q) }}
                className="text-left text-xs text-[#8a9ab0] border border-[#1a2332] rounded px-3 py-2 hover:border-[#f5a623] hover:text-[#f5a623] transition-all"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        {/* Input */}
        <div className="flex gap-3">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && ask(question)}
            placeholder="Type your question and press Enter..."
            className="flex-1 bg-[#080c0f] border border-[#1a2332] rounded px-4 py-3 text-sm text-[#e2e8f0] placeholder-[#4a5568] focus:outline-none focus:border-[#f5a623] transition-colors"
          />
          <button
            onClick={() => ask(question)}
            disabled={!question || loading}
            className="px-5 py-3 bg-[#f5a623] text-[#080c0f] rounded font-semibold text-sm disabled:opacity-30 hover:bg-[#e09415] transition-all"
          >
            {loading ? <Loader size={16} className="animate-spin" /> : <Search size={16} />}
          </button>
        </div>
      </div>

      {/* Answer */}
      {loading && (
        <div className="bg-[#0d1117] border border-[#1a2332] rounded-lg p-6 flex items-center gap-3">
          <Loader size={16} className="text-[#f5a623] animate-spin" />
          <span className="text-sm text-[#8a9ab0]">Searching concall and generating answer...</span>
        </div>
      )}

      {result && !loading && (
        <div className="bg-[#0d1117] border border-[#1a2332] rounded-lg p-6 space-y-4">
          {result.error ? (
            <p className="text-[#ff4c4c] text-sm">{result.error}</p>
          ) : (
            <>
              <div className="flex items-center gap-2 mb-3">
                <MessageSquare size={14} className="text-[#f5a623]" />
                <span className="text-xs text-[#f5a623] uppercase tracking-widest">Answer</span>
              </div>
              <div className="border-l-2 border-[#f5a623] pl-4 text-sm text-[#c8d6e5] leading-7">
                {result.answer}
              </div>
              {result.sources?.length > 0 && (
                <div className="pt-3 border-t border-[#1a2332]">
                  <p className="text-xs text-[#4a5568] uppercase tracking-widest mb-2">Sources</p>
                  <div className="flex flex-wrap gap-2">
                    {result.sources.map((s, i) => (
                      <span key={i} className="flex items-center gap-1.5 text-xs bg-[#080c0f] border border-[#1a2332] text-[#8a9ab0] px-3 py-1 rounded-full">
                        <FileText size={10} className="text-[#f5a623]" />
                        {s.source} · p.{s.page}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* History */}
      {history.length > 0 && (
        <div className="bg-[#0d1117] border border-[#1a2332] rounded-lg p-5 space-y-3">
          <p className="text-xs text-[#4a5568] uppercase tracking-widest">Recent Questions</p>
          {history.map((h, i) => (
            <div key={i} className="border-b border-[#1a2332] pb-3 last:border-0 last:pb-0">
              <p className="text-xs text-[#f5a623] mb-1">{h.question}</p>
              <p className="text-xs text-[#4a5568] line-clamp-2">{h.answer}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}