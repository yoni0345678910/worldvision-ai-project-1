import os
import re
from typing import List, Optional, Dict, Any, Tuple

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector


load_dotenv()


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/worldvision"
)

COLLECTION_NAME = "worldvision_docs"

engine = create_engine(DATABASE_URL)


def split_documents(
    docs: List[Document],
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[Document]:

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )

    return splitter.split_documents(docs)


def search_similar_docs(
    query: str,
    k: int = 10,
    score_threshold: float = 0.55,
    embedding_model: str = "text-embedding-3-large",
    search_type: str = "similarity",
    filters: Optional[Dict[str, Any]] = None,
) -> List[Document]:

    print("[RAG] search_similar_docs 실행됨")

    embeddings = OpenAIEmbeddings(
        model=embedding_model
    )

    try:
        vector_store = PGVector(
            connection=DATABASE_URL,
            embeddings=embeddings,
            collection_name=COLLECTION_NAME,
        )

        search_kwargs = {}

        if filters:
            search_kwargs["filter"] = filters

        if search_type == "mmr":
            return vector_store.max_marginal_relevance_search(
                query,
                k=k,
                **search_kwargs,
            )

        results_with_score = (
            vector_store.similarity_search_with_score(
                query,
                k=k,
                **search_kwargs,
            )
        )

        print("\n===== VECTOR SCORES =====")

        filtered_docs = []

        for i, (doc, score) in enumerate(
            results_with_score
        ):
            print(
                i + 1,
                score,
                doc.metadata.get("source"),
                doc.metadata.get("page"),
            )

            # 0.0이면 threshold 필터 비활성화
            if (
                score_threshold == 0.0
                or score <= score_threshold
            ):
                filtered_docs.append(doc)

        print("=========================\n")

        return filtered_docs

    except Exception as e:
        print("[RAG ERROR]", e)
        return []


def build_keyword_terms(
    query: str,
) -> List[str]:
    """
    질문에서 DB 텍스트 검색용 핵심어를 만든다.
    한국어 조사 및 표현 차이를 일부 보완한다.
    """

    raw_terms = re.findall(
        r"[가-힣A-Za-z0-9%]+",
        query,
    )

    suffixes = (
        "에서",
        "에게",
        "으로",
        "까지",
        "부터",
        "보다",
        "이며",
        "이고",
        "인가요",
        "나요",
        "과",
        "와",
        "은",
        "는",
        "이",
        "가",
        "을",
        "를",
        "의",
        "에",
        "도",
    )

    terms = []

    for raw in raw_terms:
        cleaned = raw

        for suffix in suffixes:
            if (
                cleaned.endswith(suffix)
                and len(cleaned) > len(suffix) + 1
            ):
                cleaned = cleaned[:-len(suffix)]
                break

        if len(cleaned) >= 2:
            terms.append(cleaned)

    # 표현이 달라도 같은 의미를 찾을 수 있도록
    # 일반적인 용어 alias 추가
    alias_groups = {
        "국제사업": [
            "국제사업",
            "국제",
            "해외사업",
            "해외",
        ],
        "국내사업": [
            "국내사업",
            "국내",
        ],
        "수혜자": [
            "수혜자",
            "수혜자수",
            "도운 사람",
            "도운 사람들",
        ],
        "사업수익": [
            "사업수익",
            "수익",
        ],
        "사업비용": [
            "사업비용",
            "비용",
        ],
        "보편적 식수": [
            "보편적 식수",
            "식수 공급",
        ],
        "안전한 식수": [
            "안전한 식수",
            "식수",
        ],
    }

    for concept, aliases in alias_groups.items():
        if concept in query:
            terms.extend(aliases)

    # 중복 제거
    return list(dict.fromkeys(terms))


def search_keyword_docs(
    query: str,
    k: int = 15,
) -> List[Document]:
    """
    임베딩 없이 PostgreSQL document 텍스트를 직접 검사하여
    질문 핵심어가 많이 포함된 chunk를 반환한다.

    OpenAI API 호출 없음.
    """

    query_terms = build_keyword_terms(query)

    if not query_terms:
        return []

    sql = text("""
        SELECT
            e.document,
            e.cmetadata
        FROM langchain_pg_embedding AS e
        JOIN langchain_pg_collection AS c
            ON e.collection_id = c.uuid
        WHERE c.name = :collection_name
    """)

    ranked = []

    try:
        with engine.connect() as conn:
            rows = conn.execute(
                sql,
                {
                    "collection_name": COLLECTION_NAME,
                },
            )

            for row in rows:
                content = row.document or ""
                metadata = row.cmetadata or {}

                matched_terms = [
                    term
                    for term in query_terms
                    if term in content
                ]

                if not matched_terms:
                    continue

                score = len(matched_terms)

                # 여러 핵심 개념이 한 chunk에 같이 있으면
                # 단일 단어만 맞는 chunk보다 강하게 우선
                if "국제사업" in query:
                    if (
                        "국제" in content
                        or "해외" in content
                    ):
                        score += 3

                if "국내사업" in query:
                    if "국내" in content:
                        score += 3

                if "수혜자" in query:
                    if (
                        "수혜자" in content
                        or "도운 사람" in content
                    ):
                        score += 3

                if "사업수익" in query:
                    if "사업수익" in content:
                        score += 5

                if "사업비용" in query:
                    if "사업비용" in content:
                        score += 5

                if "보편적 식수" in query:
                    if "보편적 식수" in content:
                        score += 5

                ranked.append(
                    (
                        score,
                        Document(
                            page_content=content,
                            metadata=metadata,
                        ),
                    )
                )

    except Exception as e:
        print("[KEYWORD SEARCH ERROR]", e)
        return []

    ranked.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    docs = [
        doc
        for _, doc in ranked[:k]
    ]

    print("\n===== KEYWORD SEARCH =====")
    print("TERMS:", query_terms)
    print("DOC COUNT:", len(docs))

    for i, doc in enumerate(docs):
        print(
            i + 1,
            doc.metadata.get("source"),
            doc.metadata.get("page"),
        )

    print("==========================\n")

    return docs


def get_page_chunks(
    page_keys: List[Tuple[str, int]],
) -> List[Document]:
    """
    벡터검색 없이 source + page가 같은 모든 chunk를
    PostgreSQL에서 직접 가져온다.
    """

    if not page_keys:
        return []

    sql = text("""
        SELECT
            e.document,
            e.cmetadata
        FROM langchain_pg_embedding AS e
        JOIN langchain_pg_collection AS c
            ON e.collection_id = c.uuid
        WHERE
            c.name = :collection_name
            AND e.cmetadata ->> 'source' = :source
            AND CAST(
                e.cmetadata ->> 'page'
                AS INTEGER
            ) = :page
    """)

    docs = []
    seen = set()

    try:
        with engine.connect() as conn:

            for source, page in page_keys:

                if (
                    not source
                    or page is None
                ):
                    continue

                rows = conn.execute(
                    sql,
                    {
                        "collection_name": COLLECTION_NAME,
                        "source": source,
                        "page": int(page),
                    },
                )

                for row in rows:

                    content = row.document or ""
                    metadata = row.cmetadata or {}

                    key = (
                        metadata.get("source"),
                        metadata.get("page"),
                        content,
                    )

                    if key in seen:
                        continue

                    seen.add(key)

                    docs.append(
                        Document(
                            page_content=content,
                            metadata=metadata,
                        )
                    )

    except Exception as e:
        print("[PAGE RETRIEVAL ERROR]", e)

    return docs