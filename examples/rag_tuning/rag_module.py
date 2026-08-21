"""
RAG 파라미터 튜닝을 위해 구현한 기존 프로토타입 모듈.

#Rag_chain 생성, # [2단계] 문서 분할, # [5단계] Retriever 생성 부분을 중점적으로 확인해주시면 됩니다.

처리 흐름:
PDF Load
→ Chunking
→ OpenAI Embedding
→ FAISS Vector Store
→ Retriever
→ LLM

튜닝 파라미터:
- chunk_size: 문서 분할 크기
- chunk_overlap: 청크 간 중첩 크기
- top_k: Retriever가 검색할 문서 조각 수

※ 현재 프로젝트는 PostgreSQL + pgvector 기반이므로
FAISS 구현을 그대로 적용하기보다는,
파라미터 전달 및 RAG 품질 비교 구조를 참고하기 위한 코드입니다.
"""

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

#Rag_chain 생성
# [RAG 튜닝 참고]
# app.py에서 설정한 Chunk Size / Overlap / Top-K를 전달받아
# 문서 분할 및 Retriever 설정에 적용
def create_rag_chain(
    pdf_path,
    chunk_size=1000,
    chunk_overlap=200,
    top_k=4
):
    # [1단계] PDF 문서 로드
    loader = PyMuPDFLoader(pdf_path)
    docs = loader.load()

    if not docs:
        raise ValueError("PDF에서 읽을 수 있는 내용이 없습니다.")

    # [2단계] 문서 분할
    # [RAG 튜닝 참고]
    # Chunk Size와 Chunk Overlap은 문서 분할 단계에 적용되며,
    # 값 변경 시 문서를 다시 분할하고 Vector Store를 재생성
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
    embeddings = OpenAIEmbeddings()

    # [4단계] Vector DB 생성
    vectorstore = FAISS.from_documents(
        documents=split_documents,
        embedding=embeddings
    )

    # [5단계] Retriever 생성
    # [RAG 튜닝 참고]
    # Top-K는 Retrieval 단계에서 가져올 유사 문서 Chunk 수에 적용
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": top_k}
    )

    # [6단계] README의 프롬프트 실험 결과 반영
    template = """
당신은 사용자가 업로드한 문서를 기반으로 질문에 답변하는
문서 분석 AI 업무지원 도우미입니다.

다음 규칙을 반드시 지켜주세요.

1. 주어진 문서의 Context에 포함된 정보만 활용하여 답변합니다.
2. 문서에서 확인할 수 없는 내용은 임의로 생성하거나 추측하지 않습니다.
3. 질문에 대한 근거가 문서에서 확인되지 않는 경우
   "문서에서 해당 정보를 확인할 수 없습니다."라고 답변합니다.
4. 여러 문서 조각에 관련 정보가 존재하는 경우 필요한 내용을 종합합니다.
5. 답변은 한국어로 명확하고 간결하게 작성합니다.

[Context]
{context}

[Question]
{question}

논리적으로 생각해보세요.

[출력 형식]

[답변]
질문에 여러 기능, 요구사항 또는 구성 요소가 포함된 경우,
문서에서 확인되는 항목을 가능한 한 누락하지 않고 목록 형식으로 작성합니다.

- 서로 다른 상위 항목은 제목으로 구분합니다.
- 각 기능 또는 요구사항은 반드시 별도의 줄에 작성합니다.
- 하나의 항목에 여러 세부 기능이 포함된 경우 하위 목록으로 구분합니다.
- 여러 기능을 쉼표로 연결하여 하나의 문장으로 합치지 않습니다.
- 문서의 상위 항목과 하위 항목 관계를 가능한 한 유지합니다.
- 단일 정보에 대한 질문은 불필요하게 목록으로 나누지 않습니다.

예시:

사용자 기능:
- 기능 A
  - 세부 기능 A-1
  - 세부 기능 A-2
- 기능 B
- 기능 C
  - 세부 기능 C-1

관리자 기능:
- 기능 A
- 기능 B
"""

    prompt = ChatPromptTemplate.from_template(template)

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
        "top_k": top_k
    }

    # 답변용 chain + 출처 확인용 retriever + 통계 반환
    return rag_chain, retriever, stats