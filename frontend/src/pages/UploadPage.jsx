import { useState } from "react"
import { UploadCloud, CheckCircle, AlertCircle, FileText } from "lucide-react"
import axios from "axios"

export default function UploadPage({ companies, setCompanies }) {
  const [file, setFile] = useState(null)
  const [company, setCompany] = useState("")
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)
  const [progress, setProgress] = useState("")

  const handleUpload = async () => {
    if (!file || !company) return
    setLoading(true)
    setStatus(null)

    const formData = new FormData()
    formData.append("file", file)
    formData.append("company", company)

    try {
      setProgress("Extracting text from PDF...")
      const res = await axios.post("http://localhost:8000/api/concall/upload", formData)
      setProgress("Chunking and indexing...")
      setStatus({ type: "success", data: res.data })
      if (!companies.includes(company)) {
        setCompanies([...companies, company])
      }
      setFile(null)
      setCompany("")
    } catch (e) {
      setStatus({ type: "error", message: e.response?.data?.detail || e.message })
    } finally {
      setLoading(false)
      setProgress("")
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">

      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-[#f5a623] tracking-wide">
          Upload & Index
        </h1>
        <p className="text-[#4a5568] text-sm mt-1">
          Upload a concall PDF to index it for Q&A
        </p>
      </div>

      {/* Upload Card */}
      <div className="bg-[#0d1117] border border-[#1a2332] rounded-lg p-6 space-y-5">

        {/* Drop Zone */}
        <label className={`flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-10 cursor-pointer transition-all duration-200
          ${file ? "border-[#f5a623] bg-[#f5a62308]" : "border-[#1a2332] hover:border-[#f5a623] hover:bg-[#f5a62305]"}`}>
          <input
            type="file"
            accept=".pdf"
            className="hidden"
            onChange={(e) => setFile(e.target.files[0])}
          />
          <UploadCloud size={36} className={file ? "text-[#f5a623]" : "text-[#4a5568]"} />
          <p className="mt-3 text-sm text-[#8a9ab0]">
            {file ? file.name : "Click to upload concall PDF"}
          </p>
          <p className="text-xs text-[#4a5568] mt-1">
            BSE / NSE filings, investor transcripts
          </p>
        </label>

        {/* Company Input */}
        <div>
          <label className="text-xs text-[#4a5568] uppercase tracking-widest mb-2 block">
            Company Name
          </label>
          <input
            type="text"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            placeholder="e.g. Infosys, TCS, Reliance..."
            className="w-full bg-[#080c0f] border border-[#1a2332] rounded px-4 py-3 text-sm text-[#e2e8f0] placeholder-[#4a5568] focus:outline-none focus:border-[#f5a623] transition-colors"
          />
        </div>

        {/* Button */}
        <button
          onClick={handleUpload}
          disabled={!file || !company || loading}
          className="w-full py-3 rounded font-semibold text-sm tracking-widest uppercase transition-all duration-200
            bg-[#f5a623] text-[#080c0f] hover:bg-[#e09415] disabled:opacity-30 disabled:cursor-not-allowed"
        >
          {loading ? progress || "Indexing..." : "Index Concall"}
        </button>

        {/* Status */}
        {status?.type === "success" && (
          <div className="flex items-start gap-3 bg-[#00c97a12] border border-[#00c97a30] rounded p-4">
            <CheckCircle size={18} className="text-[#00c97a] mt-0.5 shrink-0" />
            <div className="text-sm">
              <p className="text-[#00c97a] font-semibold">Indexed successfully</p>
              <p className="text-[#8a9ab0] mt-1">
                {status.data.pages} pages · {status.data.chunks} chunks · {status.data.company}
              </p>
            </div>
          </div>
        )}

        {status?.type === "error" && (
          <div className="flex items-start gap-3 bg-[#ff4c4c12] border border-[#ff4c4c30] rounded p-4">
            <AlertCircle size={18} className="text-[#ff4c4c] mt-0.5 shrink-0" />
            <p className="text-sm text-[#ff4c4c]">{status.message}</p>
          </div>
        )}
      </div>

      {/* Indexed Companies */}
      {companies.length > 0 && (
        <div className="bg-[#0d1117] border border-[#1a2332] rounded-lg p-6">
          <h2 className="text-sm text-[#4a5568] uppercase tracking-widest mb-4">
            Indexed Concalls
          </h2>
          <div className="grid grid-cols-2 gap-3">
            {companies.map((c) => (
              <div key={c} className="flex items-center gap-3 bg-[#080c0f] border border-[#1a2332] rounded p-3">
                <FileText size={14} className="text-[#f5a623]" />
                <span className="text-sm text-[#e2e8f0]">{c}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}