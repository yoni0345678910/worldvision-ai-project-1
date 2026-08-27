import os
from typing import List

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector

from worldvision_ai_project.services.rag import split_documents
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader


load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/worldvision"
)

COLLECTION_NAME = "worldvision_docs"
EMBEDDING_MODEL = "text-embedding-3-large"


def ingest_documents(docs: List[Document]) -> int:
    """
    문서를 chunking 후 PGVector에 저장합니다.
    반환값은 저장된 chunk 개수입니다.
    """
    if not docs:
        return 0

    chunks = split_documents(docs)

    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL
    )

    vector_store = PGVector(
        connection=DATABASE_URL,
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        use_jsonb=True,
    )

    vector_store.add_documents(chunks)

    return len(chunks)

def ingest_pdf_directory(directory_path: str) -> int:
    """
    지정한 폴더의 모든 PDF를 읽어 PGVector에 저장합니다.
    각 페이지의 metadata에 원본 파일명과 페이지 번호를 유지합니다.
    """
    pdf_dir = Path(directory_path)

    if not pdf_dir.exists():
        raise FileNotFoundError(
            f"PDF 디렉터리를 찾을 수 없습니다: {directory_path}"
        )

    all_docs: List[Document] = []

    for pdf_path in pdf_dir.glob("*.pdf"):
        loader = PyPDFLoader(str(pdf_path))
        pages = loader.load()

        for page_doc in pages:
            page_number = page_doc.metadata.get("page", 0)

            page_doc.metadata["source"] = pdf_path.name
            page_doc.metadata["page"] = page_number + 1

        all_docs.extend(pages)

        print(
            f"[Ingestion] {pdf_path.name} "
            f"- {len(pages)}페이지 로드 완료"
        )

    if not all_docs:
        print("[Ingestion] 적재할 PDF가 없습니다.")
        return 0

    chunk_count = ingest_documents(all_docs)

    print(
        f"[Ingestion] 전체 {len(all_docs)}페이지 → "
        f"{chunk_count}개 chunk 저장 완료"
    )

    return chunk_count