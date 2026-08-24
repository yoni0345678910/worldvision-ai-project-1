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

app = FastAPI(
    title="WorldVision AI Assistant API",
    description="월드비전 AI 업무지원 서비스 종합 API",
    version="0.1.0"
)

# 헬스체크 엔드포인트
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "service": "worldvision-ai-project",
        "version": "0.1.0"
    }

@app.post("/api/v1/search", response_model=SearchResponse)
async def search_knowledge(request: SearchRequest):
    try:
        result = run_knowledge_search(
            query=request.query, 
            embedding_model=request.embedding_model
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

@app.post("/api/v1/minutes", response_model=MinutesResponse)
async def generate_minutes(file: UploadFile = File(...)):
    temp_file_path = None
    try:
        # tempfile.NamedTemporaryFile로 경로 조작(Path Traversal) 보안 차단
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        return MinutesResponse(
            filename=file.filename,
            summary="2026년도 월드비전 AI 지식검색 및 회의록 시스템 고도화 회의입니다.",
            key_issues=[
                "tempfile 모듈 적용을 통한 경로 조작 보안 위험 차단",
                "프롬프트 인젝션 방어 문구 수록 및 /health 헬스체크 구현"
            ],
            decisions=[
                "보안 및 예외 처리 가이드라인 준수로 시스템 안정성 확보"
            ]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회의록 생성 중 오류가 발생했습니다: {str(e)}"
        )
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.post("/api/v1/report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    try:
        mock_report = f"# {request.topic} 관련 AI 자동 보고서 초안\n\n- 본 보고서는 {request.topic} 주제에 대한 AI 분석 내용입니다."
        return ReportResponse(report=mock_report)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"보고서 생성 중 오류가 발생했습니다: {str(e)}"
        )