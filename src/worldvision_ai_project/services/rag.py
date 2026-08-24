import os
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector

# DB 연결 정보 (환경변수 기본값 설정)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg2://postgres:postgres@localhost:5432/worldvision"
)

def split_documents(docs: List[Document], chunk_size: int = 500, chunk_overlap: int = 50) -> List[Document]:
    """
    멘토 피드백 반영: 선언만 되어 있던 split_documents 실체화
    긴 문서를 랭체인 TextSplitter로 잘라 청크 목록 생성
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    return splitter.split_documents(docs)

def search_similar_docs(
    query: str, 
    k: int = 3, 
    score_threshold: float = 0.3,
    embedding_model: str = "text-embedding-3-small"
) -> List[Document]:
    """
    멘토 피드백 반영: similarity_search_with_score 적용
    유사도 점수를 기준으로 Threshold 이하의 관련 없는 문서 제거
    """
    embeddings = OpenAIEmbeddings(model=embedding_model)
    
    try:
        vector_store = PGVector(
            connection=DATABASE_URL,
            embeddings=embeddings,
            collection_name="worldvision_docs"
        )
        
        # 유사도 점수와 함께 문서 검색 (점수가 낮을수록 유사함 / L2 또는 Cosine 거리 기준)
        results_with_score = vector_store.similarity_search_with_score(query, k=k)
        
        # 설정한 임계값(score_threshold)을 통과한 유효 문서만 필터링
        filtered_docs = []
        for doc, score in results_with_score:
            # 거리 점수 기준 필터링 (필요시 커스텀 로직 적용)
            if score <= score_threshold or score_threshold == 0.0:
                filtered_docs.append(doc)
                
        # 필터링 결과가 없으면 상위 k개 fallback 반환
        return filtered_docs if filtered_docs else [doc for doc, _ in results_with_score]
        
    except Exception as e:
        # DB 미연결 환경 대비 Fallback Mock 데이터
        print(f"[RAG Warning] Vector Store 연결 실패 (Mock 데이터 반환): {e}")
        return [
            Document(
                page_content="월드비전 AI 지식검색 시스템 모의 참고 문서입니다. 사업 규정 및 가이드라인을 확인하세요.",
                metadata={"source": "사내_규정_가이드.pdf"}
            )
        ]