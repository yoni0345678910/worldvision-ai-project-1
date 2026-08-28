from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chat_history import InMemoryChatMessageHistory
from worldvision_ai_project.services.rag import search_similar_docs

# 세션별 대화 기록 메모리 저장소
store = {}


def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


RAG_PROMPT_TEMPLATE = """
당신은 월드비전 사내 지식검색 AI 도우미입니다.

[이전 대화 기록]:
{chat_history}

[답변 지침]:
1. 이전 대화 기록은 대화 맥락을 이해하는 용도로만 사용하세요.
2. 사내 업무/지식 질문에는 반드시 아래 [참고 문서]에 명시된 정보만 사용해 답변하세요.
3. 참고 문서에서 확인할 수 있는 정보는 최대한 활용하여 답변하세요.

4. 질문에 대한 정보가 일부만 확인되는 경우,
   확인 가능한 내용은 먼저 답변하고
   확인되지 않는 부분만 "제시된 사내 문서에서 확인할 수 없습니다."라고 안내하세요.
   일부 정보가 부족하다는 이유로 전체 답변을 거부하지 마세요.

5. 참고 문서에서 질문과 관련된 정보를 전혀 찾을 수 없는 경우에만
   "제시된 사내 문서에서 해당 정보를 찾을 수 없습니다."
   라고 답변하세요.

6. 여러 수치나 정보를 비교해야 하는 질문은
   확인 가능한 값과 확인할 수 없는 값을 구분하여 설명하세요.
   확인되지 않은 값은 추측하지 마세요.

7. 질문이 "주요 사업", "주요 성과", "주요 분야"처럼 범위가 넓은 경우에는
   참고 문서에서 확인되는 대표적인 항목들을 요약하여 답변하세요.

8. 친근한 인사나 일반 대화에는 자연스럽게 응답할 수 있습니다.
[참고 문서]:
{context}

[현재 질문]:
{question}

[답변]:
"""

def run_knowledge_search(
    query: str,
    session_id: str = "default_session",
    embedding_model: str = "text-embedding-3-large",
    top_k: int = 10,
    search_type: str = "similarity",
    filters: Optional[Dict[str, Any]] = None
):
    docs = search_similar_docs(
        query=query,
        k=top_k,
        embedding_model=embedding_model,
        search_type=search_type,
        filters=filters,
    )

    print("\n===== RAG DEBUG =====")
    print("QUERY:", query)
    print("DOC COUNT:", len(docs))

    for i, doc in enumerate(docs):
        print(f"\n--- DOC {i + 1} ---")
        print("SOURCE:", doc.metadata.get("source"))
        print("PAGE:", doc.metadata.get("page"))
        print("CONTENT:", doc.page_content[:500])

    print("=====================\n")

    if docs:
        context_text = "\n\n".join(
            f"[출처: {doc.metadata.get('source', '알 수 없는 출처')}, "
            f"페이지: {doc.metadata.get('page', '알 수 없음')}]\n"
            f"{doc.page_content}"
            for doc in docs
        )
    else:
        context_text = "참고할 문서가 없습니다."

    # 동일 문서의 여러 chunk가 검색되어도 출처는 한 번만 반환
    sources = list(
        dict.fromkeys(
            doc.metadata.get("source", "알 수 없는 출처")
            for doc in docs
        )
    ) if docs else []

    history_obj = get_session_history(session_id)
    chat_history_messages = history_obj.messages

    formatted_history = ""
    for msg in chat_history_messages:
        role = "사용자" if msg.type == "human" else "AI"
        formatted_history += f"{role}: {msg.content}\n"

    if not formatted_history:
        formatted_history = "이전 대화 없음"

    prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    chain = prompt | llm
    response = chain.invoke({
        "context": context_text,
        "chat_history": formatted_history,
        "question": query,
    })

    history_obj.add_user_message(query)
    history_obj.add_ai_message(response.content)

    return {
        "answer": response.content,
        "sources": sources,
    }