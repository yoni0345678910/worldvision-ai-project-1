from pydantic import BaseModel, Field

# 정보 검색
class SearchRequest(BaseModel):   # 입력 규격
    query: str = Field(
        ...,
        min_length=1,   # 빈 질문을 Pydantic이 Workflow까지 보내지 않고 바로 거절 가능
        description="사용자가 입력한 지식 검색 질문",
    )
    # DA 요구사항: 임베딩 모델을 직접 선택/비교할 수 있도록 파라미터 추가
    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="테스트할 OpenAI 임베딩 모델 (예: text-embedding-3-small, text-embedding-3-large)",
    )

class SearchResponse(BaseModel):   # 출력 규격
    answer: str
    sources: list[str] = Field(
        default=[],
        description="검색된 참고 문서 출처 목록"
    )

# 회의록
class MinutesResponse(BaseModel):   # 회의록 기능 출력 규격
    filename: str                   # 업로드된 음성 파일명
    minutes: str                    # 생성된 회의록

# 보고서
class ReportRequest(BaseModel):   # 보고서 생성 기능 입력 규격
    topic: str = Field(
        ...,
        min_length=1,
        description="생성할 보고서의 주제",
    )

class ReportResponse(BaseModel):  # 보고서 생성 기능 출력 규격
    report: str