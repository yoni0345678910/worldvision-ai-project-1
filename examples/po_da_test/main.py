from typing import Optional
from fastapi import FastAPI, Query, UploadFile, File, Form
from examples.po_da_test.services.rag import process_rag_search
from examples.po_da_test.services.minutes import process_audio_minutes
from examples.po_da_test.services.report import generate_business_report

app = FastAPI(title="PO/DA Test & Validation API")

# 1. 지식 검색 및 RAG 품질 검증 엔드포인트
@app.get("/api/v1/search")
async def search_endpoint(
    query: str = Query(..., description="검색할 질문 (최소 2자 이상)"),
    top_k: int = Query(3, ge=1, le=10),
    threshold: float = Query(0.7, ge=0.0, le=1.0)
):
    return await process_rag_search(
        query=query, 
        top_k=top_k, 
        threshold=threshold
    )

# 2. 회의록 업로드 엔드포인트
@app.post("/api/v1/minutes")
async def minutes_endpoint(file: UploadFile = File(...)):
    return await process_audio_minutes(file)

# 3. 보고서 생성 엔드포인트
@app.post("/api/v1/report")
async def report_endpoint(topic: str = Form(...)):
    return await generate_business_report(topic)