import re

from langfuse import get_client, observe
from dotenv import load_dotenv

from typing import Optional, Dict, Any, List

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chat_history import (
    InMemoryChatMessageHistory,
)
from langchain_core.documents import Document

from worldvision_ai_project.services.rag import (
    search_similar_docs,
    search_keyword_docs,
    get_page_chunks,
)

from worldvision_ai_project.services.memory import (
    add_memory,
    search_relevant_memories,
    trim_memory,
)


load_dotenv()

langfuse = get_client()

store = {}


def get_session_history(
    session_id: str,
) -> InMemoryChatMessageHistory:

    if session_id not in store:
        store[session_id] = (
            InMemoryChatMessageHistory()
        )

    return store[session_id]


def rerank_documents(
    query: str,
    docs: List[Document],
    final_k: int = 20,
) -> List[Document]:

    query_terms = set(
        re.findall(
            r"[가-힣A-Za-z0-9%]+",
            query,
        )
    )

    ranked = []

    for index, doc in enumerate(docs):

        content = doc.page_content or ""

        score = 0

        # 일반적인 직접 단어 일치
        for term in query_terms:
            if (
                len(term) >= 2
                and term in content
            ):
                score += 1

        # 국제/국내 비교 질문
        if "국제사업" in query:
            if "국제" in content:
                score += 5

        if "국내사업" in query:
            if "국내" in content:
                score += 5

        if "수혜자" in query:
            if (
                "수혜자" in content
                or "도운 사람" in content
            ):
                score += 5

        # 한 문서에서 국제 + 국내가 함께 나오면
        # 비교 질문에서 매우 강하게 우선
        if (
            "국제사업" in query
            and "국내사업" in query
            and "국제" in content
            and "국내" in content
        ):
            score += 15

        # 재무 질문
        if (
            "사업수익" in query
            and "사업수익" in content
        ):
            score += 10

        if (
            "사업비용" in query
            and "사업비용" in content
        ):
            score += 10

        # 식수 정의 질문
        if (
            "보편적 식수" in query
            and "보편적 식수" in content
        ):
            score += 10

        if (
            "안전한 식수" in content
            and (
                "식수" in query
                or "보편적" in query
            )
        ):
            score += 5

        if (
            "90%" in content
            and "30분" in content
        ):
            score += 10

        # 같은 점수라면 기존 retrieval 순위를 유지
        ranked.append(
            (
                score,
                -index,
                doc,
            )
        )

    ranked.sort(
        key=lambda item: (
            item[0],
            item[1],
        ),
        reverse=True,
    )

    return [
        item[2]
        for item in ranked[:final_k]
    ]


RAG_PROMPT_TEMPLATE = """
당신은 월드비전 사내 지식검색 AI 도우미입니다.

[이전 대화 기록]:
{chat_history}

[답변 지침]:
1. 이전 대화 기록은 대화 맥락을 이해하는 용도로만 사용하세요.

2. 사내 업무/지식 질문에는 반드시 아래 [참고 문서]에
   명시된 정보만 사용해 답변하세요.

3. 참고 문서에서 확인할 수 있는 정보는 최대한 활용하여 답변하세요.

4. 질문에 대한 정보가 일부만 확인되는 경우,
   확인 가능한 내용은 먼저 답변하고
   확인되지 않는 부분만
   "제시된 사내 문서에서 확인할 수 없습니다."
   라고 안내하세요.
   일부 정보가 부족하다는 이유로 전체 답변을 거부하지 마세요.

5. 참고 문서에서 질문과 관련된 정보를 전혀 찾을 수 없는 경우에만
   "제시된 사내 문서에서 해당 정보를 찾을 수 없습니다."
   라고 답변하세요.

6. 여러 수치나 정보를 비교해야 하는 질문은
   확인 가능한 값과 확인할 수 없는 값을 구분하여 설명하세요.
   확인되지 않은 값은 추측하지 마세요.

7. 질문이 "주요 사업", "주요 성과", "주요 분야"처럼
   범위가 넓은 경우에는 참고 문서에서 확인되는
   대표적인 항목들을 요약하여 답변하세요.

8. 친근한 인사나 일반 대화에는 자연스럽게 응답할 수 있습니다.

9. 질문에 여러 수치나 지표가 관련될 경우,
   질문의 표현과 가장 직접적으로 대응하는 항목의 수치를 사용하세요.
   비교 질문에서는 비교 대상 각각의 값을 문서에서
   명시적으로 확인한 뒤 답변하세요.
   비슷한 의미의 다른 지표, 합계, 소계 값을
   임의로 대신 사용하지 마세요.

10. "국제", "국내", "아동", "성인"처럼 서로 다른 범주의
    수치가 함께 제시되어 있는 경우에는
    각 수치 바로 옆에 표시된 범주명을 확인하여 답변하세요.
    다른 범주의 수치를 대신 사용하지 마세요.

11. 문서에 정확한 수치가 명시되어 있는 경우,
    "약", "여", "만여" 등으로 반올림하거나 축약하지 말고
    문서에 기재된 정확한 숫자를 그대로 사용하세요.

[참고 문서]:
{context}

[현재 질문]:
{question}

[답변]:

[관련 과거 대화 메모리]:
{memory_context}
"""


@observe(name="knowledge-search")
def run_knowledge_search(
    query: str,
    session_id: str = "default_session",
    embedding_model: str = "text-embedding-3-large",
    top_k: int = 20,
    search_type: str = "similarity",
    filters: Optional[Dict[str, Any]] = None,
):

    # =====================================================
    # 1. Vector retrieval
    # =====================================================

    vector_docs = search_similar_docs(
        query=query,
        k=top_k,
        score_threshold=0.0,
        embedding_model=embedding_model,
        search_type=search_type,
        filters=filters,
    )

    # =====================================================
    # 2. Keyword retrieval
    #
    # Vector가 놓치는 정확한 용어/표/수치 페이지 보완
    # OpenAI API 호출 없음
    # =====================================================

    keyword_docs = search_keyword_docs(
        query=query,
        k=15,
    )

    # =====================================================
    # 3. Vector + keyword seed 합치기
    # =====================================================

    seed_docs = []
    seen_seed = set()

    for doc in vector_docs + keyword_docs:

        key = (
            doc.metadata.get("source"),
            doc.metadata.get("page"),
            doc.page_content,
        )

        if key in seen_seed:
            continue

        seen_seed.add(key)
        seed_docs.append(doc)

    # =====================================================
    # 4. 관련 페이지 목록 확보
    # =====================================================

    page_keys = []
    seen_pages = set()

    for doc in seed_docs:

        source = doc.metadata.get("source")
        page = doc.metadata.get("page")

        key = (
            source,
            page,
        )

        if (
            source
            and page is not None
            and key not in seen_pages
        ):
            page_keys.append(key)
            seen_pages.add(key)

    # =====================================================
    # 5. 같은 페이지 chunk 전체를 DB에서 직접 조회
    #
    # 벡터 검색 재호출 X
    # OpenAI 호출 X
    # =====================================================

    sibling_docs = get_page_chunks(
        page_keys
    )

    # =====================================================
    # 6. seed + sibling 합치기
    # =====================================================

    combined_docs = []
    seen_docs = set()

    for doc in seed_docs + sibling_docs:

        key = (
            doc.metadata.get("source"),
            doc.metadata.get("page"),
            doc.page_content,
        )

        if key in seen_docs:
            continue

        seen_docs.add(key)
        combined_docs.append(doc)

    # =====================================================
    # 7. 최종 rerank
    # =====================================================

    docs = rerank_documents(
        query=query,
        docs=combined_docs,
        final_k=top_k,
    )

    # =====================================================
    # DEBUG
    # =====================================================

    print("\n===== RAG DEBUG =====")
    print("QUERY:", query)

    print(
        "VECTOR COUNT:",
        len(vector_docs),
    )

    print(
        "KEYWORD COUNT:",
        len(keyword_docs),
    )

    print(
        "PAGE KEYS:",
        page_keys,
    )

    print(
        "SIBLING COUNT:",
        len(sibling_docs),
    )

    print(
        "FINAL DOC COUNT:",
        len(docs),
    )

    for i, doc in enumerate(docs):

        print(
            f"\n--- DOC {i + 1} ---"
        )

        print(
            "SOURCE:",
            doc.metadata.get("source"),
        )

        print(
            "PAGE:",
            doc.metadata.get("page"),
        )

        print(
            "CONTENT:",
            doc.page_content[:500],
        )

    print("=====================\n")

    # =====================================================
    # Context
    # =====================================================

    if docs:

        context_text = "\n\n".join(
            f"[출처: "
            f"{doc.metadata.get('source', '알 수 없는 출처')}, "
            f"페이지: "
            f"{doc.metadata.get('page', '알 수 없음')}]\n"
            f"{doc.page_content}"
            for doc in docs
        )

    else:
        context_text = (
            "참고할 문서가 없습니다."
        )

    # =====================================================
    # Sources
    # =====================================================

    sources = (
        list(
            dict.fromkeys(
                doc.metadata.get(
                    "source",
                    "알 수 없는 출처",
                )
                for doc in docs
            )
        )
        if docs
        else []
    )

    # =====================================================
    # Semantic memory
    # =====================================================

    relevant_memories = (
        search_relevant_memories(
            session_id=session_id,
            query=query,
            top_k=3,
        )
    )

    print("\n===== MEMORY DEBUG =====")
    print(
        "QUERY:",
        query,
    )

    print(
        "MEMORY COUNT:",
        len(relevant_memories),
    )

    for i, memory in enumerate(
        relevant_memories
    ):
        print(
            f"\n--- MEMORY {i + 1} ---"
        )
        print(memory.page_content)

    print("========================\n")

    if relevant_memories:

        memory_context = "\n\n".join(
            doc.page_content
            for doc in relevant_memories
        )

    else:
        memory_context = (
            "관련 과거 대화 없음"
        )

    # =====================================================
    # Chat history
    # =====================================================

    history_obj = get_session_history(
        session_id
    )

    formatted_history = ""

    for msg in history_obj.messages:

        role = (
            "사용자"
            if msg.type == "human"
            else "AI"
        )

        formatted_history += (
            f"{role}: {msg.content}\n"
        )

    if not formatted_history:
        formatted_history = (
            "이전 대화 없음"
        )

    # =====================================================
    # LLM
    # =====================================================

    prompt = (
        ChatPromptTemplate.from_template(
            RAG_PROMPT_TEMPLATE
        )
    )

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
    )

    chain = prompt | llm

    response = chain.invoke(
        {
            "context": context_text,
            "chat_history": formatted_history,
            "memory_context": memory_context,
            "question": query,
        }
    )

    # =====================================================
    # Memory 저장
    # =====================================================

    history_obj.add_user_message(
        query
    )

    history_obj.add_ai_message(
        response.content
    )

    add_memory(
        session_id=session_id,
        user_message=query,
        ai_message=response.content,
    )

    trim_memory(
        session_id=session_id,
        max_memories=20,
    )

    return {
        "answer": response.content,
        "sources": sources,
    }