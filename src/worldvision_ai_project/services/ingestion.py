import os
from typing import List

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector

from worldvision_ai_project.services.rag import split_documents


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