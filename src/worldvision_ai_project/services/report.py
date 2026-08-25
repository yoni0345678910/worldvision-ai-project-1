from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

REPORT_PROMPT_TEMPLATE = """
당신은 월드비전의 수석 AI 비즈니스 컨설턴트입니다.
제시된 주제({topic})에 대해 전문적이고 고품질의 Business Report 초안을 작성해 주세요.

[보고서 작성 가이드라인]:
1. 주제: {topic}
2. Markdown 형식으로 깔끔하게 정리해 주세요.
3. 아래 목차 구조를 반드시 포함하세요.
   - # [주제] AI 분석 및 보고서
   - ## 1. 개요 및 추진 배경
   - ## 2. 주요 현황 및 분석
   - ## 3. 기대 효과 및 실행 제언

[보고서 본문]:
"""

def generate_ai_report(topic: str) -> str:
    prompt = ChatPromptTemplate.from_template(REPORT_PROMPT_TEMPLATE)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    
    chain = prompt | llm
    response = chain.invoke({"topic": topic})
    
    return response.content