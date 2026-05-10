import { useState, useEffect } from "react"
import { Wifi, Clock } from "lucide-react"

const models = [
  "llama3-8b-8192",
  "llama3-70b-8192",
  "mixtral-8x7b-32768",
  "gemma2-9b-it",
]

export default function TopBar({ model, setModel }) {
  const [time, setTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  return (
    <div className="h-14 bg-[#0d1117] border-b border-[#1a2332] flex items-center justify-between px-6">
      
      {/* Left — status */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[#00c97a] animate-pulse" />
          <span className="text-[#00c97a] text-xs tracking-widest uppercase">
            API Live
          </span>
        </div>
        <div className="w-px h-4 bg-[#1a2332]" />
        <span className="text-[#4a5568] text-xs tracking-widest uppercase">
          NSE · BSE · Earnings Terminal
        </span>
      </div>

      {/* Right — model + clock */}
      <div className="flex items-center gap-4">
        <select
          value={model}
          onChange={(e) => setModel(e.target.value)}
          className="bg-[#111820] border border-[#1a2332] text-[#f5a623] text-xs px-3 py-1.5 rounded focus:outline-none focus:border-[#f5a623]"
        >
          {models.map((m) => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>

        <div className="flex items-center gap-2 text-[#4a5568] text-xs">
          <Clock size={12} />
          <span className="font-mono">
            {time.toLocaleTimeString("en-IN", { hour12: false })}
          </span>
        </div>

        <Wifi size={14} className="text-[#4a5568]" />
      </div>
    </div>
  )
}