from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, File, UploadFile, status
from examples.po_da_test.schemas import (
    SearchRequest, SearchResponse,
    MinutesResponse,
    ReportRequest, ReportResponse
)
from examples.po_da_test.search import run_knowledge_search

app = FastAPI(
    title="WorldVision AI Assistant API (PO/DA Test)",
    description="월드비전 AI 업무지원 서비스 종합 API - PO/DA 요구사항 반영 테스트용",
    version="0.2.0"
)

@app.post("/api/v1/search", response_model=SearchResponse)
async def search_knowledge(request: SearchRequest):
    try:
        result = run_knowledge_search(
            query=request.query, 
            embedding_model=request.embedding_model,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            top_k=request.top_k
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
    try:
        return MinutesResponse(
            filename=file.filename,
            summary="2026년도 월드비전 AI 지식검색 시스템 고도화 및 테스트 방안 논의 회의입니다.",
            key_issues=[
                "PO/DA 테스트용 예시 모듈(examples) 구현 및 검증",
                "RAG 품질 검증을 위한 Chunk Size, Top-K 파라미터 조정 기능 추가",
                "MinutesResponse의 구조화된 JSON 반환 형식 표준화"
            ],
            decisions=[
                "운영 코드(src/)는 원복 상태로 유지하고 examples에서 1차 테스트 진행",
                "테스트 완료 후 피드백 반영하여 src/ 정식 이식 진행"
            ]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회의록 생성 중 오류가 발생했습니다: {str(e)}"
        )

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