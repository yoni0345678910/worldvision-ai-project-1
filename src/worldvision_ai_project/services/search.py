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
3. 참고 문서에서 질문의 근거를 확인할 수 없다면 추측하거나 일반 지식으로 보완하지 마세요.
4. 필요한 정보가 없거나 일부만 확인되는 경우
   "제시된 사내 문서에서 해당 정보를 찾을 수 없습니다."
   라고 명확하게 안내하세요.
5. 여러 수치나 정보를 비교해야 하는 질문은 참고 문서에서 각각의 값을 모두 확인한 경우에만 결론을 내리세요.
6. 친근한 인사나 일반 대화에는 자연스럽게 응답할 수 있습니다.

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

    context_text = (
        "\n\n".join(doc.page_content for doc in docs)
        if docs
        else "참고할 문서가 없습니다."
    )

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