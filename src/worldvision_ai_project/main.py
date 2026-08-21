from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException, File, UploadFile, status
from worldvision_ai_project.schemas import (
    SearchRequest, SearchResponse,
    MinutesResponse,
    ReportRequest, ReportResponse
)
from src.worldvision_ai_project.services.search import run_knowledge_search
from src.worldvision_ai_project.services.minutes import process_audio_minutes

app = FastAPI(
    title="WorldVision AI Assistant API",
    description="월드비전 AI 업무지원 서비스 종합 API",
    version="0.1.0"
)

# 1. 사내 지식검색 엔드포인트
@app.post("/api/v1/search", response_model=SearchResponse)
async def search_knowledge(request: SearchRequest):
    try:
        result = run_knowledge_search(request.query)
        return SearchResponse(
            answer=result["answer"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"지식검색 처리 중 오류가 발생했습니다: {str(e)}"
        )

# 2. AI 회의록 생성 엔드포인트
@app.post("/api/v1/minutes", response_model=MinutesResponse)
async def generate_minutes(file: UploadFile = File(...)):
    try:
        # 파일 내용을 bytes 형태로 읽어온 뒤 전달
        file_bytes = await file.read()
        result = process_audio_minutes(file_bytes, file_name=file.filename)
        return MinutesResponse(
            filename=file.filename,
            minutes=result["minutes"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회의록 생성 중 오류가 발생했습니다: {str(e)}"
        )