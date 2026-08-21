from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.worldvision_ai_project.services.rag import search_similar_docs

# 1. RAG 프롬프트 템플릿 설정
RAG_PROMPT_TEMPLATE = """
당신은 월드비전 사내 지식검색 AI 도우미입니다.
아래 제공된 [참고 문서]만을 바탕으로 사용자의 질문에 친절하고 정확하게 답변해 주세요.
만약 참고 문서에서 답을 찾을 수 없다면 "제시된 문서에서 해당 정보를 찾을 수 없습니다."라고 답변하세요.

[참고 문서]:
{context}

[질문]:
{question}

[답변]:
"""

# 2. 사내 지식검색 핵심 실행 함수
def run_knowledge_search(query: str):
    # 1) RAG: 관련 문서 및 출처 검색
    docs = search_similar_docs(query, k=3)
    
    # 검색 결과에서 문서 내용과 출처 정보 분리
    context_text = "\n\n".join([doc.page_content for doc in docs])
    sources = [doc.metadata.get("source", "알 수 없는 출처") for doc in docs]
    
    # 2) LLM 호출 준비
    prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    chain = prompt | llm
    
    # 3) 답변 생성
    response = chain.invoke({
        "context": context_text,
        "question": query
    })
    
    # 4) 답변 + 출처 형태 반환
    return {
        "answer": response.content,
        "sources": sources
    }