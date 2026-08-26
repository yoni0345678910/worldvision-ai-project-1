from typing import Dict, List
import math

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings


load_dotenv()

# 메모리 임베딩 모델
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

# 세션별 대화 Document 저장
memory_store: Dict[str, List[Document]] = {}

# 세션별 대화 임베딩 벡터 저장
memory_vectors: Dict[str, List[List[float]]] = {}


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """
    두 임베딩 벡터의 코사인 유사도를 계산합니다.
    """
    dot_product = sum(x * y for x, y in zip(a, b))

    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def add_memory(
    session_id: str,
    user_message: str,
    ai_message: str
) -> None:
    """
    한 번의 사용자 질문 + AI 답변을
    세션 메모리와 벡터 인덱스에 저장합니다.
    """
    if session_id not in memory_store:
        memory_store[session_id] = []
        memory_vectors[session_id] = []

    memory_text = (
        f"사용자: {user_message}\n"
        f"AI: {ai_message}"
    )

    memory_doc = Document(
        page_content=memory_text,
        metadata={
            "session_id": session_id
        }
    )

    # 대화 내용을 임베딩
    memory_vector = embeddings.embed_query(memory_text)

    # Document와 벡터를 같은 순서로 저장
    memory_store[session_id].append(memory_doc)
    memory_vectors[session_id].append(memory_vector)


def get_memories(session_id: str) -> List[Document]:
    """
    특정 세션의 모든 메모리를 반환합니다.
    """
    return memory_store.get(session_id, [])


def search_relevant_memories(
    session_id: str,
    query: str,
    top_k: int = 3,
    score_threshold: float = 0.3
) -> List[Document]:
    """
    현재 질문과 의미적으로 관련 있는
    과거 세션 메모리를 검색합니다.
    """
    docs = memory_store.get(session_id, [])
    vectors = memory_vectors.get(session_id, [])

    if not docs or not vectors:
        return []

    query_vector = embeddings.embed_query(query)

    scored_memories = []

    for doc, memory_vector in zip(docs, vectors):
        score = cosine_similarity(
            query_vector,
            memory_vector
        )

        if score >= score_threshold:
            scored_memories.append((score, doc))

    scored_memories.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        doc
        for _, doc in scored_memories[:top_k]
    ]

def clear_memory(session_id: str) -> None:
    """
    특정 세션의 메모리와 벡터 인덱스를 초기화합니다.
    """
    memory_store.pop(session_id, None)
    memory_vectors.pop(session_id, None)

def get_memory_count(session_id: str) -> int:
    """
    특정 세션에 저장된 메모리 개수를 반환합니다.
    """
    return len(memory_store.get(session_id, []))


def trim_memory(session_id: str, max_memories: int = 20) -> None:
    """
    세션별 메모리 개수를 제한합니다.
    오래된 메모리부터 제거합니다.
    """
    docs = memory_store.get(session_id, [])
    vectors = memory_vectors.get(session_id, [])

    if len(docs) <= max_memories:
        return

    memory_store[session_id] = docs[-max_memories:]
    memory_vectors[session_id] = vectors[-max_memories:]

    trim_memory(session_id)