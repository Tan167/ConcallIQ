import { UploadCloud, MessageSquare, TrendingUp, BarChart2, Activity } from "lucide-react"

const nav = [
  { id: "upload", label: "Upload & Index", icon: UploadCloud },
  { id: "qa", label: "Q&A Terminal", icon: MessageSquare },
  { id: "sentiment", label: "Sentiment", icon: TrendingUp },
  { id: "compare", label: "Compare", icon: BarChart2 },
]

export default function Sidebar({ activePage, setActivePage, companies }) {
  return (
    <div className="w-64 bg-[#0d1117] border-r border-[#1a2332] flex flex-col">
      
      {/* Logo */}
      <div className="p-6 border-b border-[#1a2332]">
        <div className="flex items-center gap-2">
          <Activity className="text-[#f5a623]" size={22} />
          <span className="text-xl font-semibold tracking-wider">
            Concall<span className="text-[#f5a623]">IQ</span>
          </span>
        </div>
        <p className="text-[#4a5568] text-xs mt-1 tracking-widest uppercase">
          Earnings Intelligence
        </p>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-4 space-y-1">
        {nav.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActivePage(id)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded text-sm transition-all duration-200 text-left
              ${activePage === id
                ? "bg-[#f5a623] text-[#080c0f] font-semibold"
                : "text-[#8a9ab0] hover:bg-[#111820] hover:text-[#f5a623]"
              }`}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </nav>

      {/* Indexed Companies */}
      <div className="p-4 border-t border-[#1a2332]">
        <p className="text-[#4a5568] text-xs uppercase tracking-widest mb-3">
          Indexed — {companies.length}
        </p>
        <div className="space-y-1 max-h-40 overflow-y-auto">
          {companies.length === 0 ? (
            <p className="text-[#4a5568] text-xs">No concalls yet</p>
          ) : (
            companies.map((c) => (
              <div key={c} className="flex items-center gap-2 text-xs text-[#8a9ab0] py-1">
                <div className="w-1.5 h-1.5 rounded-full bg-[#f5a623]" />
                {c}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}