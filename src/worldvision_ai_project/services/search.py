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
1. [이전 대화 기록]을 참조하여 사용자의 이름이나 이전 대화 맥락을 기억하고 친절하게 답변해 주세요.
2. 친근한 대화나 인사말에는 친절하게 대답해 주세요.
3. 사내 업무/지식 질문인 경우 아래 [참고 문서] 내용에 기반하여 답변해 주세요.
4. [참고 문서]에 없는 사내 업무 정보라면 "제시된 사내 문서에서 해당 정보를 찾을 수 없습니다."라고 안내해 주세요.

[참고 문서]:
{context}

[현재 질문]:
{question}

[답변]:
"""

def run_knowledge_search(
    query: str,
    session_id: str = "default_session",
    embedding_model: str = "text-embedding-3-large",  # 👈 text-embedding-3-large로 변경!
    top_k: int = 3,
    search_type: str = "hybrid",
    filters: Optional[Dict[str, Any]] = None
):
    docs = search_similar_docs(query, k=top_k, embedding_model=embedding_model)
    context_text = "\n\n".join([doc.page_content for doc in docs]) if docs else "참고할 문서가 없습니다."
    sources = [doc.metadata.get("source", "알 수 없는 출처") for doc in docs] if docs else []
    
    # 1) 세션 메모리 가져오기
    history_obj = get_session_history(session_id)
    chat_history_messages = history_obj.messages
    
    # 2) 이전 대화 내역 텍스트 변환
    formatted_history = ""
    for msg in chat_history_messages:
        role = "사용자" if msg.type == "human" else "AI"
        formatted_history += f"{role}: {msg.content}\n"
        
    if not formatted_history:
        formatted_history = "이전 대화 없음"

    # 3) LLM 실행
    prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    chain = prompt | llm
    response = chain.invoke({
        "context": context_text,
        "chat_history": formatted_history,
        "question": query
    })
    
    # 4) 대화 내용 메모리 저장
    history_obj.add_user_message(query)
    history_obj.add_ai_message(response.content)
    
    return {
        "answer": response.content,
        "sources": sources
    }