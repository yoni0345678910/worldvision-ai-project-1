import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from fastapi import HTTPException, status
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

# RAG 품질 검증용 더미 가상 지식 기반(Knowledge Base) 데이터셋
MOCK_KNOWLEDGE_BASE = [
    {
        "id": "doc_01",
        "title": "월드비전 사업 안내",
        "content": "월드비전은 전 세계 취약계층 아동과 주민들을 지원하는 국제구호개발 NGO입니다.",
        "score": 0.88
    },
    {
        "id": "doc_02",
        "title": "월드비전 연차 보고서",
        "content": "2023년 월드비전은 글로벌 아동 후원 사업 및 국내 위기아동 지원 사업에 주력하였습니다.",
        "score": 0.75
    },
    {
        "id": "doc_03",
        "title": "프로젝트 배포 가이드",
        "content": "FastAPI 애플리케이션은 Docker 및 AWS ECS 환경에 최적화되어 배포됩니다.",
        "score": 0.35
    }
]

async def process_rag_search(query: str, top_k: int = 3, threshold: float = 0.7) -> Dict[str, Any]:
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OpenAI API 키가 설정되지 않았증니다."
        )

    # 1. 문서 검색 및 threshold 필터링 (품질 검증 핵심 로직)
    retrieved_docs = [
        doc for doc in MOCK_KNOWLEDGE_BASE 
        if doc["score"] >= threshold
    ][:top_k]

    # 2. RAG 품질 검증: Threshold 만족 문서가 없는 경우 (검색 품질 저하 판정)
    if not retrieved_docs:
        return {
            "query": query,
            "threshold": threshold,
            "retrieved_count": 0,
            "quality_status": "LOW_RELEVANCE",
            "message": f"설정된 유사도 기준({threshold})을 충족하는 관련 지식 문서를 찾지 못했습니다.",
            "answer": "죄송합니다. 제공된 지식 정보 내에서는 해당 질문에 답변할 적절한 내용을 찾을 수 없습니다."
        }

    # 3. 검색된 문서 맥락(Context) 구성
    context_text = "\n".join([f"- [{doc['title']}]: {doc['content']}" for doc in retrieved_docs])

    # 4. GPT RAG 답변 생성
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"너는 월드비전 지식 검색 도우미야. 오직 제공된 [참고 문서] 정보만을 바탕으로 답변해줘.\n\n[참고 문서]:\n{context_text}"},
            {"role": "user", "content": query}
        ],
        timeout=30.0
    )

    return {
        "query": query,
        "threshold": threshold,
        "retrieved_count": len(retrieved_docs),
        "retrieved_docs": retrieved_docs,
        "quality_status": "PASS",
        "answer": response.choices[0].message.content
    }