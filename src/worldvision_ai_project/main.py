import os
import tempfile
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, File, UploadFile, status
from worldvision_ai_project.schemas import (
    SearchRequest, SearchResponse,
    MinutesResponse,
    ReportRequest, ReportResponse
)
from worldvision_ai_project.services.search import run_knowledge_search
from worldvision_ai_project.services.minutes import process_audio_minutes
from worldvision_ai_project.services.report import generate_ai_report

app = FastAPI(
    title="WorldVision AI Assistant API",
    description="월드비전 AI 업무지원 서비스 종합 API",
    version="0.1.0"
)

ALLOWED_EXTENSIONS = {".flac", ".m4a", ".mp3", ".mp4", ".mpeg", ".mpga", ".oga", ".ogg", ".wav", ".webm"}

# 1. 헬스체크 엔드포인트
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "worldvision-ai-project",
        "version": "0.1.0"
    }

# 2. 지식검색 엔드포인트 (공백 입력 방어 + session_id 세션 기반 기억 + 검색 옵션 반영)
@app.post("/api/v1/search", response_model=SearchResponse)
async def search_knowledge(request: SearchRequest):
    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="검색어를 공백으로만 입력할 수 없습니다."
        )

    try:
        result = run_knowledge_search(
            query=request.query,
            session_id=request.session_id,
            embedding_model=request.embedding_model,
            top_k=request.top_k,
            search_type=request.search_type,
            filters=request.filters
        )
        return SearchResponse(
            answer=result.get("answer", "답변을 생성할 수 없습니다."),
            sources=result.get("sources", [])
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"지식검색 처리 중 오류가 발생했습니다: {str(e)}"
        )

# 3. 회의록 생성 엔드포인트 (오디오 확장자 검사 반영)
@app.post("/api/v1/minutes", response_model=MinutesResponse)
async def generate_minutes(file: UploadFile = File(...)):
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"지원하지 않는 파일 형식입니다. (지원 형식: {', '.join(sorted(ALLOWED_EXTENSIONS))})"
        )

    try:
        content = await file.read()
        result = process_audio_minutes(audio_file_bytes=content, file_name=file.filename)

        return MinutesResponse(
            filename=file.filename,
            summary=result.get("minutes", "요약 결과를 생성할 수 없습니다."),
            key_issues=[],
            decisions=[]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회의록 생성 중 오류가 발생했습니다: {str(e)}"
        )

# 4. 보고서 생성 엔드포인트 (공백 입력 방어 + GPT 연동 반영)
@app.post("/api/v1/report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    if not request.topic or not request.topic.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="보고서 주제를 공백으로만 입력할 수 없습니다."
        )

    try:
        report_content = generate_ai_report(topic=request.topic)
        return ReportResponse(report=report_content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"보고서 생성 중 오류가 발생했습니다: {str(e)}"
        )