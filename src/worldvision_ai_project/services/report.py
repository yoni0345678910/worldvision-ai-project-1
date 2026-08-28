# src/worldvision_ai_project/services/report.py

from worldvision_ai_project.services.rag import search_similar_docs
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langfuse import observe

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
3. 보고서의 사실, 수치, 기관명, 사업 성과는 반드시 참고 문서에서 확인된 내용만 사용하세요.
4. 참고 문서에서 확인할 수 없는 사실이나 수치를 추측하거나 임의로 생성하지 마세요.
5. 참고 문서만으로 답변하기 어려운 내용은 "제공된 자료에서 확인할 수 없습니다."라고 명시하세요.
6. 향후 시사점 및 제언은 참고 문서를 바탕으로 작성하되, 확인된 사실과 제언을 명확히 구분하세요.
7. 참고 문서에 명시적으로 포함되지 않은 사업, 성과, 재무 상태, 증가·감소 여부, 인과관계를 사실처럼 서술하지 마세요.
8. 일반적인 월드비전 활동이나 상식에 근거하여 참고 문서의 빈 내용을 보완하지 마세요.
9. 각 주요 성과는 참고 문서에서 직접 확인 가능한 내용만 작성하세요. 근거가 부족한 항목은 작성하지 마세요.
10. 충분한 근거가 검색되지 않은 경우 보고서 분량을 억지로 채우지 말고, 확인 가능한 내용만 작성한 뒤 자료가 부족함을 명시하세요.
11. 수치와 단위, 항목명은 참고 문서에서 서로의 관계가 명확히 확인되는 경우에만 함께 사용하세요.
    서로 다른 항목의 수치나 단위를 임의로 결합하거나 변환하지 마세요.
    특히 금액, 인원수, 비율 등의 수치는 각각 어떤 항목을 의미하는지 확인한 뒤 작성하세요.
    
[작성된 보고서]:
"""

@observe(name="report-generation")
def generate_ai_report(topic: str):
    try:
        docs = search_similar_docs(query=topic, k=8)
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