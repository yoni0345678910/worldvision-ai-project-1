from dotenv import load_dotenv

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

# .env 파일의 API Key 로드
load_dotenv()


def format_docs(docs):
    """
    Retriever가 반환한 Document 객체에서
    실제 본문(page_content)만 추출하여 LLM에 전달
    """
    return "\n\n".join(doc.page_content for doc in docs)


# [RAG 튜닝 참고]
# app.py에서 설정한 Chunk Size / Overlap / Top-K / Embedding Model을 전달받아
# 문서 분할 및 Retriever 설정에 적용
def create_rag_chain(
    pdf_path,
    chunk_size=1000,
    chunk_overlap=200,
    top_k=4,
    embedding_model="text-embedding-3-small"
):
    # [1단계] PDF 문서 로드
    loader = PyMuPDFLoader(pdf_path)
    docs = loader.load()

    if not docs:
        raise ValueError("PDF에서 읽을 수 있는 내용이 없습니다.")

    # [2단계] 문서 분할
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )

    split_documents = text_splitter.split_documents(docs)

    if not split_documents:
        raise ValueError("PDF에서 생성된 청크가 없습니다.")

    # [3단계] 임베딩 생성
    # [임베딩 모델 비교 참고]
    # 동일한 조건에서 small / large 모델만 변경하여 검색 결과 비교
    embeddings = OpenAIEmbeddings(
        model=embedding_model
    )

    # [4단계] Vector DB 생성
    vectorstore = FAISS.from_documents(
        documents=split_documents,
        embedding=embeddings
    )

    # [5단계] Retriever 생성
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": top_k}
    )

    # [6단계] 엔지니어 작성 RAG 프롬프트 적용
    rag_prompt_template = """
당신은 월드비전 사내 지식검색 AI 도우미입니다.
아래 제공된 [참고 문서]만을 바탕으로 사용자의 질문에 친절하고 정확하게 답변해 주세요.
만약 참고 문서에서 답을 찾을 수 없다면 "제시된 문서에서 해당 정보를 찾을 수 없습니다."라고 답변하세요.

[참고 문서]:
{context}

[질문]:
{question}

[답변]:
"""

    prompt = ChatPromptTemplate.from_template(
        rag_prompt_template
    )

    # [7단계] LLM 설정
    llm = ChatOpenAI(
        model_name="gpt-4o",
        temperature=0
    )

    # [8단계] RAG Chain 생성
    rag_chain = (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    # UI에서 보여줄 문서 처리 통계
    stats = {
        "page_count": len(docs),
        "chunk_count": len(split_documents),
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "top_k": top_k,
        "embedding_model": embedding_model
    }

    # 답변용 chain + 출처 확인용 retriever + 통계 반환
    return rag_chain, retriever, stats