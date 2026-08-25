import os
from typing import List
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
    embedding_model: str = "text-embedding-3-small"
) -> List[Document]:
    embeddings = OpenAIEmbeddings(model=embedding_model)
    
    try:
        vector_store = PGVector(
            connection=DATABASE_URL,
            embeddings=embeddings,
            collection_name="worldvision_docs"
        )
        
        results_with_score = vector_store.similarity_search_with_score(query, k=k)
        
        filtered_docs = []
        for doc, score in results_with_score:
            if score <= score_threshold or score_threshold == 0.0:
                filtered_docs.append(doc)
                
        return filtered_docs if filtered_docs else [doc for doc, _ in results_with_score]
        
    except Exception as e:
        print(f"[RAG Warning] Vector Store 연결 실패 (Mock 데이터 Fallback 반환): {e}")
        return [
            Document(
                page_content="월드비전 AI 지식검색 시스템 참고 문서입니다. 사업 규정 및 가이드라인을 확인하세요.",
                metadata={"source": "사내_규정_가이드.pdf"}
            )
        ]