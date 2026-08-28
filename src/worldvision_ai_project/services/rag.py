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
    k: int = 10,
    score_threshold: float = 0.55,
    embedding_model: str = "text-embedding-3-large",
    search_type: str = "similarity",
    filters: Optional[Dict[str, Any]] = None
) -> List[Document]:
    print("[RAG] search_similar_docs 실행됨")

    embeddings = OpenAIEmbeddings(model=embedding_model)
    
    try:
        vector_store = PGVector(
            connection=DATABASE_URL,
            embeddings=embeddings,
            collection_name="worldvision_docs"
        )
        
        search_kwargs = {}
        if filters:
            search_kwargs["filter"] = filters

        # search_type 조건 처리
        if search_type == "mmr":
            docs = vector_store.max_marginal_relevance_search(
                query, k=k, **search_kwargs
            )
            return docs

        results_with_score = vector_store.similarity_search_with_score(
            query, 
            k=k,
            **search_kwargs
        )

        print("\n===== VECTOR SCORE DEBUG =====")
        for i, (doc, score) in enumerate(results_with_score):
            print(
                f"{i + 1}. SCORE={score:.4f} | "
                f"SOURCE={doc.metadata.get('source', '알 수 없는 출처')}"
            )
        print("==============================\n")
        
        filtered_docs = []
        for doc, score in results_with_score:
            if score <= score_threshold or score_threshold == 0.0:
                filtered_docs.append(doc)
                
        return filtered_docs
        
    except Exception as e:
        print(f"[RAG Error] Vector Store 연결 또는 검색 실패: {e}")
        raise RuntimeError(f"PostgreSQL/PGVector DB 연결 및 검색 오류: {str(e)}")