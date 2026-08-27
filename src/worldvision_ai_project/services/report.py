# src/worldvision_ai_project/services/report.py

from worldvision_ai_project.services.rag import search_similar_docs
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

REPORT_PROMPT_TEMPLATE = """
당신은 월드비전 보고서 작성 전문가입니다. 
아래 검색된 사내 문서를 바탕으로 요청된 주제에 대한 전문적인 보고서를 작성해 주세요.

[참고 사내 문서]:
{context}

[보고서 주제]:
{topic}

[작성 지침]:
1. 참고 문서의 내용을 적극 활용하여 논리적이고 체계적인 보고서를 작성하세요.
2. 개요, 현황/주요내용, 결론 및 제언의 구조로 가독성 있게 작성하세요.

[작성된 보고서]:
"""

def generate_ai_report(topic: str):
    try:
        docs = search_similar_docs(query=topic, k=3)
        context_text = "\n\n".join([doc.page_content for doc in docs]) if docs else "관련 사내 문서를 찾을 수 없습니다."
    except Exception as e:
        context_text = "사내 DB 연동 전 기본 참고 정보"

    prompt = ChatPromptTemplate.from_template(REPORT_PROMPT_TEMPLATE)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    chain = prompt | llm
    response = chain.invoke({
        "context": context_text,
        "topic": topic
    })

    # Dict가 아닌, 문자열(String) 그대로 반환해야 ReportResponse 스키마 검증 통과!
    return response.content