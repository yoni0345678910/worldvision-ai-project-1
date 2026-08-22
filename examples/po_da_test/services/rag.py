import os
from langchain_community.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 1. 문서 잘라내기 (Chunking) - DA 테스트용 파라미터 유연화
def split_documents(documents, chunk_size: int = 1000, chunk_overlap: int = 100):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return text_splitter.split_documents(documents)

# 2. Vector DB (PostgreSQL + pgvector) 연동 및 유사도 검색 - DA 요구사항 반영
def get_vectorstore(embedding_model: str = "text-embedding-3-small"):
    # DB 접속 정보 (환경변수 또는 설정값 사용)
    connection_string = os.getenv(
        "DATABASE_URL", 
        "postgresql+psycopg2://postgres:postgres@localhost:5432/worldvision_db"
    )
    # DA분이 전달한 임베딩 모델 적용
    embeddings = OpenAIEmbeddings(model=embedding_model)
    
    vectorstore = PGVector(
        connection_string=connection_string,
        embedding_function=embeddings,
        collection_name="knowledge_base"
    )
    return vectorstore

# 3. 질문과 유사한 문서 및 출처 가져오기
def search_similar_docs(query: str, k: int = 3, embedding_model: str = "text-embedding-3-small"):
    vectorstore = get_vectorstore(embedding_model=embedding_model)
    # 유사도 높은 문서 k개 검색
    docs = vectorstore.similarity_search(query, k=k)
    return docs