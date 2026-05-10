import { useState } from "react"
import { BarChart2, Loader, CheckSquare, Square } from "lucide-react"
import axios from "axios"
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts"

export default function ComparePage({ companies, model }) {
  const [question, setQuestion] = useState("What was the revenue growth this quarter?")
  const [selected, setSelected] = useState([])
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)

  const toggleCompany = (c) => {
    setSelected((prev) =>
      prev.includes(c) ? prev.filter((x) => x !== c) : [...prev, c]
    )
  }

  const compare = async () => {
    if (!selected.length || !question) return
    setLoading(true)
    setResults(null)
    try {
      const answers = await Promise.all(
        selected.map((c) =>
          axios.post("http://localhost:8000/api/concall/ask", {
            question,
            company: c,
            k: 5,
            model,
          }).then((r) => ({ company: c, answer: r.data.answer }))
        )
      )
      setResults(answers)
    } catch (e) {
      setResults([{ company: "Error", answer: e.message }])
    } finally {
      setLoading(false)
    }
  }

  const colors = ["#f5a623", "#00c97a", "#4a9eff", "#ff4c4c", "#b388ff"]

  return (
    <div className="max-w-4xl mx-auto space-y-6">

      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-[#f5a623] tracking-wide">Compare Terminal</h1>
        <p className="text-[#4a5568] text-sm mt-1">Compare answers across multiple concalls</p>
      </div>

      {companies.length < 2 ? (
        <div className="bg-[#0d1117] border border-[#1a2332] rounded-lg p-10 text-center">
          <BarChart2 size={36} className="text-[#1a2332] mx-auto mb-3" />
          <p className="text-[#4a5568] text-sm">Index at least 2 companies to compare</p>
        </div>
      ) : (
        <>
          {/* Setup */}
          <div className="bg-[#0d1117] border border-[#1a2332] rounded-lg p-5 space-y-4">

            {/* Company selector */}
            <div>
              <p className="text-xs text-[#4a5568] uppercase tracking-widest mb-3">Select Companies</p>
              <div className="flex flex-wrap gap-2">
                {companies.map((c, i) => (
                  <button
                    key={c}
                    onClick={() => toggleCompany(c)}
                    className={`flex items-center gap-2 px-4 py-2 rounded text-xs font-semibold transition-all border
                      ${selected.includes(c)
                        ? "border-[#f5a623] text-[#f5a623] bg-[#f5a62310]"
                        : "border-[#1a2332] text-[#4a5568] hover:border-[#f5a623] hover:text-[#f5a623]"
                      }`}
                  >
                    {selected.includes(c)
                      ? <CheckSquare size={12} style={{ color: colors[i % colors.length] }} />
                      : <Square size={12} />
                    }
                    {c}
                  </button>
                ))}
              </div>
            </div>

            {/* Question */}
            <div>
              <p className="text-xs text-[#4a5568] uppercase tracking-widest mb-2">Question</p>
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                className="w-full bg-[#080c0f] border border-[#1a2332] rounded px-4 py-3 text-sm text-[#e2e8f0] placeholder-[#4a5568] focus:outline-none focus:border-[#f5a623] transition-colors"
              />
            </div>

            <button
              onClick={compare}
              disabled={selected.length < 2 || !question || loading}
              className="w-full py-3 bg-[#f5a623] text-[#080c0f] rounded font-semibold text-sm uppercase tracking-widest disabled:opacity-30 hover:bg-[#e09415] transition-all"
            >
              {loading
                ? <span className="flex items-center justify-center gap-2"><Loader size={14} className="animate-spin" /> Comparing...</span>
                : "Compare Companies"
              }
            </button>
          </div>

          {/* Results */}
          {results && !loading && (
            <div className="space-y-4">
              {results.map((r, i) => (
                <div key={r.company} className="bg-[#0d1117] border border-[#1a2332] rounded-lg p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-2 h-2 rounded-full" style={{ background: colors[i % colors.length] }} />
                    <span className="text-sm font-semibold" style={{ color: colors[i % colors.length] }}>
                      {r.company}
                    </span>
                  </div>
                  <div className="border-l-2 pl-4 text-sm text-[#c8d6e5] leading-7"
                    style={{ borderColor: colors[i % colors.length] }}>
                    {r.answer}
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}