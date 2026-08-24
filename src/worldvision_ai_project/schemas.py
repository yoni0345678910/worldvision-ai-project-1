from pydantic import BaseModel, Field

# 1. 지식검색 요청/응답 스키마 (min_length 및 sources 필드 추가)
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="사용자가 입력한 지식 검색 질문 (빈 값 방지)")
    embedding_model: str = Field(
        default="text-embedding-3-small", 
        description="사용할 임베딩 모델"
    )

class SearchResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default=[], description="검색된 참고 문서 출처 목록")

# 2. 회의록 응답 스키마
class MinutesResponse(BaseModel):
    filename: str = Field(..., description="업로드된 파일명")
    summary: str = Field(..., description="회의 전체 요약")
    key_issues: list[str] = Field(default=[], description="주요 논의사항")
    decisions: list[str] = Field(default=[], description="결정사항")

# 3. 보고서 요청/응답 스키마
class ReportRequest(BaseModel):
    topic: str = Field(..., min_length=1, description="보고서 주제")

class ReportResponse(BaseModel):
    report: str