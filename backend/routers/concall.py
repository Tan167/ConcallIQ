from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ingestion import load_pdf_from_bytes, chunk_pages
from src.rag import index_chunks, answer_question, summarize_concall, list_indexed_companies, delete_company

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str
    company: str = ""
    k: int = 6
    model: str = "llama3-8b-8192"

@router.post("/upload")
async def upload_concall(
    file: UploadFile = File(...),
    company: str = Form(...),
):
    try:
        contents = await file.read()
        pages = load_pdf_from_bytes(contents, file.filename)
        chunks = chunk_pages(pages)
        n = index_chunks(chunks, company=company)
        return {"success": True, "pages": len(pages), "chunks": n, "company": company}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask")
async def ask_question(req: QuestionRequest):
    try:
        result = answer_question(
            question=req.question,
            company=req.company,
            k=req.k,
            model=req.model,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize/{company}")
async def summarize(company: str):
    try:
        summary = summarize_concall(company)
        return {"summary": summary, "company": company}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/companies")
async def get_companies():
    try:
        companies = list_indexed_companies()
        return {"companies": companies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/companies/{company}")
async def remove_company(company: str):
    try:
        delete_company(company)
        return {"success": True, "deleted": company}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))