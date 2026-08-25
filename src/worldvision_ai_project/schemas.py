from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

# 1. 지식검색 요청/응답 스키마
class SearchRequest(BaseModel):
    query: str = Field(
        ..., 
        min_length=1, 
        strip_whitespace=True, 
        description="사용자가 입력한 질문"
    )
    session_id: Optional[str] = Field(
        default="default_session", 
        description="대화 맥락 유지를 위한 고유 세션 ID (예: a1b2c3d4-e5f6-7890-abcd-123456789abc)"
    )
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="사용할 임베딩 모델"
    )
    top_k: int = Field(default=3, ge=1, le=10, description="반환할 상위 문서 개수")
    search_type: str = Field(default="hybrid", description="검색 방식")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="메타데이터 필터 조건")

class SearchResponse(BaseModel):
    answer: str
    sources: List[str] = Field(default=[], description="참고 문서 출처 목록")

# 2. 회의록 응답 스키마
class MinutesResponse(BaseModel):
    filename: str = Field(..., description="업로드된 파일명")
    summary: str = Field(..., description="회의 전체 요약")
    key_issues: List[str] = Field(default=[], description="주요 논의사항")
    decisions: List[str] = Field(default=[], description="결정사항")

# 3. 보고서 요청/응답 스키마
class ReportRequest(BaseModel):
    topic: str = Field(
        ..., 
        min_length=1, 
        strip_whitespace=True, 
        description="보고서 주제"
    )

class ReportResponse(BaseModel):
    report: str