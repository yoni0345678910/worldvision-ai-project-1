from fastapi import FastAPI, UploadFile, File

from worldvision_ai_project.schemas import (
    SearchRequest,   #정보 검색
    SearchResponse,
    MinutesResponse,   #회의록
    ReportRequest,   #보고서
    ReportResponse,
)

app = FastAPI(
    title="World Vision AI",
    version="0.1.0",
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

#정보 검색
@app.post("/search", response_model=SearchResponse)
def search(request: SearchRequest):
    return SearchResponse(
        answer=f"검색 요청이 정상적으로 전달되었습니다: {request.query}"
    )

#회의록
@app.post("/minutes", response_model=MinutesResponse)
async def create_minutes(file: UploadFile = File(...)):
    return MinutesResponse(
        filename=file.filename or "unknown",
        minutes="회의록 생성 요청이 정상적으로 전달되었습니다.",
    )

#보고서
@app.post("/report", response_model=ReportResponse)
def create_report(request: ReportRequest):
    return ReportResponse(
        report=f"보고서 생성 요청이 정상적으로 전달되었습니다: {request.topic}"
    )