from pydantic import BaseModel, Field

#정보 검색
class SearchRequest(BaseModel):   #입력 규격 ex) 월드비전의주요 사업은?
    query: str = Field(
        ...,
        min_length=1,   #빈 질문을 Pydantic이 Workflow까지 보내지 않고 바로 거절 가능
        description="사용자가 입력한 지식 검색 질문",
    )

#회의록
class SearchResponse(BaseModel):   #출력 규격
    answer: str

class MinutesResponse(BaseModel):   # 회의록 기능 출력 규격
    filename: str                   # 업로드된 음성 파일명
    minutes: str                    # 생성된 회의록

#보고서
class ReportRequest(BaseModel):   # 보고서 생성 기능 입력 규격
    topic: str = Field(
        ...,
        min_length=1,
        description="생성할 보고서의 주제",
    )


class ReportResponse(BaseModel):  # 보고서 생성 기능 출력 규격
    report: str