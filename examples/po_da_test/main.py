from typing import Optional
from fastapi import FastAPI, Query, UploadFile, File, Form, HTTPException, status
from examples.po_da_test.services.search import run_knowledge_search
from examples.po_da_test.services.minutes import process_audio_minutes

app = FastAPI(title="PO/DA Test & Validation API")

# 1. 지식 검색 엔드포인트
@app.get("/api/v1/search")
async def search_endpoint(
    query: str = Query(..., description="검색할 질문 (최소 2자 이상)"),
    session_id: Optional[str] = Query(None, description="세션 ID (연속 대화 시 기존 session_id 입력)"),
    top_k: int = Query(3, ge=1, le=10),
    threshold: float = Query(0.7, ge=0.0, le=1.0)
):
    return await run_knowledge_search(
        query=query, 
        session_id=session_id, 
        top_k=top_k, 
        threshold=threshold
    )

# 2. 회의록 업로드 엔드포인트 (실제 Whisper STT + GPT 요약 연동)
@app.post("/api/v1/minutes")
async def minutes_endpoint(file: UploadFile = File(...)):
    return await process_audio_minutes(file)

# 3. 보고서 생성 테스트 엔드포인트
@app.post("/api/v1/report")
async def report_endpoint(topic: str = Form(...)):
    clean_topic = topic.strip() if topic else ""
    if not clean_topic:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="보고서 주제는 공백일 수 없습니다."
        )
    return {"topic": clean_topic, "message": "보고서 생성 요청 검증 완료"}