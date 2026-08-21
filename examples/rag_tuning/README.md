# RAG Tuning Prototype

2주차 과제에서 구현한 RAG 파라미터 튜닝 및 검색 결과 비교용 프로토타입 코드입니다.

현재 프로젝트는 FastAPI + PostgreSQL/pgvector 기반으로 구성되어 있으므로,
본 예제의 Streamlit + FAISS 구조를 그대로 적용하기보다는
RAG 파라미터 조절 및 검색 결과 비교 방식을 참고하기 위한 코드입니다.

## 주요 기능

- PDF 문서 업로드 및 분석
- Chunk Size 조절
- Chunk Overlap 조절
- Retriever Top-K 조절
- 파라미터 변경 시 RAG Chain 재생성
- 문서 페이지 수 및 생성된 Chunk 수 확인
- Retriever가 검색한 실제 문서 조각 및 출처 페이지 확인

## RAG 처리 흐름

PDF 업로드  
→ Document Loader  
→ Text Splitter  
→ OpenAI Embedding  
→ FAISS Vector Store  
→ Retriever  
→ LLM  
→ Answer

## 파일 구성

- `app.py`
  - Streamlit 기반 RAG 테스트 UI
  - Chunk Size / Chunk Overlap / Top-K 조절
  - 파라미터 변경 감지 및 RAG Chain 재생성
  - 검색 결과와 실제 근거 문서 확인

- `rag_module.py`
  - PDF 문서 로드
  - Chunking
  - Embedding 생성
  - FAISS Vector Store 구성
  - Retriever 및 RAG Chain 생성

- `requirements.txt`
  - 기존 프로토타입 실행 시 사용한 Python 패키지 목록

## 현재 프로젝트 적용 시 참고사항

현재 프로젝트에서는 PostgreSQL + pgvector를 사용하고 있으므로
FAISS Vector Store 구현 자체보다는 다음 부분을 참고하여 활용할 수 있습니다.

- `chunk_size`, `chunk_overlap` 파라미터를 문서 Chunking 단계에 적용
- `top_k` 파라미터를 Retrieval 단계에 적용
- 파라미터 변경에 따른 RAG 검색 결과 비교
- Retriever가 실제 검색한 문서 및 출처 확인
- Document Loader → Chunking → Embedding → Vector DB 적재 흐름 참고

코드 내 `[RAG 튜닝 참고]`, `[출처 반환 참고]` 주석을 통해
관련 구현 부분을 확인할 수 있습니다.