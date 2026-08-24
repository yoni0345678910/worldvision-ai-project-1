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

from worldvision_ai_project.agent import invoke_agent

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
        agent_result = invoke_agent({
            "request_type": "search",
            "query": request.query,
            "embedding_model": request.embedding_model
        })

        if agent_result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=agent_result["error"]
            )

        result = agent_result["result"]

        return SearchResponse(
            answer=result.get("answer", "답변을 생성할 수 없습니다."),
            sources=result.get("sources", [])
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"지식검색 처리 중 오류가 발생했습니다: {str(e)}"
        )

@app.post("/api/v1/minutes", response_model=MinutesResponse)
async def generate_minutes(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()

        agent_result = invoke_agent({
            "request_type": "minutes",
            "file_name": file.filename,
            "file_bytes": file_bytes
        })

        if agent_result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=agent_result["error"]
            )

        result = agent_result["result"]

        return MinutesResponse(
            filename=file.filename,
            summary=result.get(
                "minutes",
                "회의록을 생성할 수 없습니다."
            ),
            key_issues=[],
            decisions=[]
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회의록 생성 중 오류가 발생했습니다: {str(e)}"
        )

@app.post("/api/v1/report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    try:
        agent_result = invoke_agent({
            "request_type": "report",
            "topic": request.topic
        })

        if agent_result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=agent_result["error"]
            )

        result = agent_result["result"]

        return ReportResponse(
            report=result.get(
                "report",
                "보고서를 생성할 수 없습니다."
            )
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"보고서 생성 중 오류가 발생했습니다: {str(e)}"
        )