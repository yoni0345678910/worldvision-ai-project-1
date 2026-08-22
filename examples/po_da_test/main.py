from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException, File, UploadFile, status

# 1. 원본 src가 아닌 'examples.po_da_test.schemas'에서 가져오도록 수정
from examples.po_da_test.schemas import (
    SearchRequest, SearchResponse,
    MinutesResponse,
    ReportRequest, ReportResponse
)

# 2. search 서비스도 examples 쪽 함수를 바라보도록 수정
from examples.po_da_test.search import run_knowledge_search
from worldvision_ai_project.services.minutes import process_audio_minutes

app = FastAPI(
    title="WorldVision AI Assistant API (PO/DA Test)",
    description="월드비전 AI 업무지원 서비스 종합 API - PO/DA 테스트용",
    version="0.1.0"
)

# 1. 사내 지식검색 엔드포인트
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

# 2. AI 회의록 생성 엔드포인트
@app.post("/api/v1/minutes", response_model=MinutesResponse)
async def generate_minutes(file: UploadFile = File(...)):
    try:
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

# 3. PO 테스트용 보고서 생성 엔드포인트
@app.post("/api/v1/report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    try:
        mock_report = (
            f"# {request.topic} 관련 AI 자동 보고서 초안\n\n"
            f"## 1. 개요\n본 보고서는 {request.topic} 주제에 대한 AI 분석 및 요약 내용입니다.\n\n"
            f"## 2. 주요 현황 및 분석\n- 사내 문서 및 데이터 기반 분석 수행 완료\n- 관련 세부 지표 검토 필요\n\n"
            f"## 3. 결론 및 제언\n수집된 결과를 바탕으로 추가 실행 계획을 수립할 것을 권장합니다."
        )
        return ReportResponse(report=mock_report)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"보고서 생성 중 오류가 발생했습니다: {str(e)}"
        )