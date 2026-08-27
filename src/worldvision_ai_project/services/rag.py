import os
from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/worldvision"
)

def split_documents(docs: List[Document], chunk_size: int = 500, chunk_overlap: int = 50) -> List[Document]:
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
    embedding_model: str = "text-embedding-3-large",  # 1. text-embedding-3-large로 통일
    search_type: str = "similarity",                  # 2. 미사용 파라미터 옵션화
    filters: Optional[Dict[str, Any]] = None           # 3. 메타데이터 필터 옵션 추가
) -> List[Document]:
    embeddings = OpenAIEmbeddings(model=embedding_model)
    
    try:
        vector_store = PGVector(
            connection=DATABASE_URL,
            embeddings=embeddings,
            collection_name="worldvision_docs"
        )
        
        # filters 조건 적용 가능하도록 kwargs 구성
        search_kwargs = {}
        if filters:
            search_kwargs["filter"] = filters

        results_with_score = vector_store.similarity_search_with_score(
            query, 
            k=k,
            **search_kwargs
        )
        
        filtered_docs = []
        for doc, score in results_with_score:
            if score <= score_threshold or score_threshold == 0.0:
                filtered_docs.append(doc)
                
        return filtered_docs if filtered_docs else [doc for doc, _ in results_with_score]
        
    except Exception as e:
        # DB 오류 발생 시 모의(Mock) 문서로 감추지 않고, 
        # 상위 서비스(Service Layer)에서 DB 에러(500/504 등)임을 알 수 있도록 명확히 로깅 및 예외 처리
        print(f"[RAG Error] Vector Store 연결 또는 검색 실패: {e}")
        raise RuntimeError(f"PostgreSQL/PGVector DB 연결 및 검색 오류: {str(e)}")