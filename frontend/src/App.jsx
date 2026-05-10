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
      <div className="flex h-screen overflow-hidden terminal-grid">
        <Sidebar activePage={activePage} setActivePage={setActivePage} companies={companies} />
        <div className="flex flex-col flex-1 overflow-hidden">
          <TopBar model={model} setModel={setModel} />
          <main className="flex-1 overflow-y-auto p-6">
            {pages[activePage]}
          </main>
        </div>
      </div>
    </QueryClientProvider>
  )
}