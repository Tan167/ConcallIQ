import { UploadCloud, MessageSquare, TrendingUp, BarChart2, Activity, Circle } from "lucide-react"

const nav = [
  { id: "upload", label: "Upload & Index", icon: UploadCloud, shortcut: "F1" },
  { id: "qa", label: "Q&A Terminal", icon: MessageSquare, shortcut: "F2" },
  { id: "sentiment", label: "Sentiment", icon: TrendingUp, shortcut: "F3" },
  { id: "compare", label: "Compare", icon: BarChart2, shortcut: "F4" },
]

export default function Sidebar({ activePage, setActivePage, companies }) {
  return (
    <div className="w-56 bg-[#0a0e13] border-r border-[#1e2d3d] flex flex-col shrink-0">

      {/* Logo */}
      <div className="px-5 py-5 border-b border-[#1e2d3d]">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 bg-[#f5a623] rounded flex items-center justify-center">
            <Activity size={14} className="text-[#080c0f]" />
          </div>
          <div>
            <div className="text-[15px] font-bold tracking-wider text-white">
              Concall<span className="text-[#f5a623]">IQ</span>
            </div>
            <div className="text-[9px] text-[#3d5166] tracking-[0.2em] uppercase mt-0.5">
              Earnings Intelligence
            </div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <div className="p-3 space-y-0.5 flex-1">
        <div className="text-[9px] text-[#3d5166] tracking-[0.2em] uppercase px-3 py-2">
          Navigation
        </div>
        {nav.map(({ id, label, icon: Icon, shortcut }) => (
          <button
            key={id}
            onClick={() => setActivePage(id)}
            className={`w-full flex items-center justify-between px-3 py-2.5 rounded text-left transition-all duration-150 group
              ${activePage === id
                ? "bg-[#f5a623] text-[#080c0f]"
                : "text-[#5a7a94] hover:bg-[#0d1520] hover:text-[#e2e8f0]"
              }`}
          >
            <div className="flex items-center gap-2.5">
              <Icon size={14} />
              <span className="text-[12px] font-semibold tracking-wide">{label}</span>
            </div>
            <span className={`text-[9px] tracking-wider font-mono
              ${activePage === id ? "text-[#80530a]" : "text-[#2a3d4d] group-hover:text-[#3d5166]"}`}>
              {shortcut}
            </span>
          </button>
        ))}
      </div>

      {/* Indexed Companies */}
      <div className="p-3 border-t border-[#1e2d3d]">
        <div className="text-[9px] text-[#3d5166] tracking-[0.2em] uppercase px-3 py-2 flex items-center justify-between">
          <span>Indexed</span>
          <span className="bg-[#0d1520] border border-[#1e2d3d] text-[#f5a623] px-1.5 py-0.5 rounded text-[9px]">
            {companies.length}
          </span>
        </div>
        <div className="space-y-0.5 max-h-36 overflow-y-auto">
          {companies.length === 0 ? (
            <p className="text-[#2a3d4d] text-[11px] px-3 py-1">No concalls yet</p>
          ) : (
            companies.map((c) => (
              <div key={c} className="flex items-center gap-2 px-3 py-1.5 rounded hover:bg-[#0d1520] transition-all">
                <div className="w-1.5 h-1.5 rounded-full bg-[#00c97a] shrink-0" />
                <span className="text-[11px] text-[#5a7a94] truncate">{c}</span>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="px-5 py-3 border-t border-[#1e2d3d]">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded bg-[#0d1520] border border-[#1e2d3d] flex items-center justify-center">
            <span className="text-[9px] text-[#f5a623] font-bold">v2</span>
          </div>
          <div>
            <div className="text-[10px] text-[#3d5166]">UI Redesign</div>
            <div className="text-[9px] text-[#2a3d4d]">feature/ui-redesign</div>
          </div>
        </div>
      </div>

    </div>
  )
}