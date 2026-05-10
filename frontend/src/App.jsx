import { useState } from "react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import Sidebar from "./components/Sidebar"
import TopBar from "./components/TopBar"
import UploadPage from "./pages/UploadPage"
import QAPage from "./pages/QAPage"
import SentimentPage from "./pages/SentimentPage"
import ComparePage from "./pages/ComparePage"

const queryClient = new QueryClient()

export default function App() {
  const [activePage, setActivePage] = useState("upload")
  const [companies, setCompanies] = useState([])
  const [model, setModel] = useState("llama3-8b-8192")

  const pages = {
    upload: <UploadPage companies={companies} setCompanies={setCompanies} />,
    qa: <QAPage companies={companies} model={model} />,
    sentiment: <SentimentPage />,
    compare: <ComparePage companies={companies} model={model} />,
  }

  return (
    <QueryClientProvider client={queryClient}>
      <div className="flex h-screen overflow-hidden bg-[#080c0f]">
        <Sidebar activePage={activePage} setActivePage={setActivePage} companies={companies} />
        <div className="flex flex-col flex-1 overflow-hidden">
          <TopBar model={model} setModel={setModel} />
          {/* Page header strip */}
          <div className="bg-[#0a0e13] border-b border-[#1e2d3d] px-6 py-3 flex items-center gap-3 shrink-0">
            <div className="w-1 h-4 bg-[#f5a623] rounded-full" />
            <h1 className="text-[13px] font-bold text-white tracking-widest uppercase">
              {activePage === "upload" && "Upload & Index"}
              {activePage === "qa" && "Q&A Terminal"}
              {activePage === "sentiment" && "Sentiment Analysis"}
              {activePage === "compare" && "Compare Terminal"}
            </h1>
            <div className="ml-auto flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-[#f5a623] animate-pulse" />
              <span className="text-[10px] text-[#3d5166] tracking-widest uppercase">Ready</span>
            </div>
          </div>
          <main className="flex-1 overflow-y-auto p-6 bg-[#080c0f]">
            {pages[activePage]}
          </main>
        </div>
      </div>
    </QueryClientProvider>
  )
}