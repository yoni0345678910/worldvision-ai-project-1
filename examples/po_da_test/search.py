from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# services 폴더 안에 있는 rag.py를 정확히 지칭하도록 수정
from examples.po_da_test.services.rag import search_similar_docs

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

def run_knowledge_search(
    query: str, 
    embedding_model: str = "text-embedding-3-small",
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
    top_k: int = 3
):
    docs = search_similar_docs(
        query=query, 
        k=top_k, 
        embedding_model=embedding_model,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    context_text = "\n\n".join([doc.page_content for doc in docs]) if docs else "참고할 문서가 없습니다."
    sources = [doc.metadata.get("source", "알 수 없는 출처") for doc in docs] if docs else []
    
    prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    chain = prompt | llm
    response = chain.invoke({
        "context": context_text,
        "question": query
    })
    
    return {
        "answer": response.content,
        "sources": sources
    }