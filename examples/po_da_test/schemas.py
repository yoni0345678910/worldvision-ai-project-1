from pydantic import BaseModel, Field

# 1. 지식검색 요청/응답 스키마
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="사용자가 입력한 지식 검색 질문")
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="테스트할 OpenAI 임베딩 모델 (예: text-embedding-3-small, text-embedding-3-large)"
    )
    chunk_size: int = Field(default=1000, description="RAG 품질 검증용 Chunk Size")
    chunk_overlap: int = Field(default=100, description="RAG 품질 검증용 Chunk Overlap")
    top_k: int = Field(default=3, description="RAG 품질 검증용 Retriever Top-K 값")

class SearchResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default=[], description="검색된 참고 문서 출처 목록 (PO/README 요구사항 반영)")

# 2. 회의록 응답 스키마 (README 명세에 따라 구조화된 JSON 형태로 분리)
class MinutesResponse(BaseModel):
    filename: str = Field(..., description="업로드된 음성 파일명")
    summary: str = Field(..., description="회의 전체 요약")
    key_issues: list[str] = Field(default=[], description="주요 논의사항 목록")
    decisions: list[str] = Field(default=[], description="결정사항 목록")

# 3. 보고서 요청/응답 스키마
class ReportRequest(BaseModel):
    topic: str = Field(..., min_length=1, description="생성할 보고서의 주제")

class ReportResponse(BaseModel):
    report: str