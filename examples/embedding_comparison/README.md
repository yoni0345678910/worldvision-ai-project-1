# Embedding Model Comparison

DA 임베딩 모델 비교 테스트를 위한 예제 코드입니다.

기존 RAG 튜닝 프로토타입을 기반으로 하며,
동일한 검색 조건에서 OpenAI 임베딩 모델별 검색 결과를 비교할 수 있도록 구성했습니다.

## 비교 모델

- `text-embedding-3-small`
- `text-embedding-3-large`

## 테스트 방법

1. 동일한 PDF 문서를 업로드합니다.
2. Chunk Size, Chunk Overlap, Retriever k 값을 동일하게 설정합니다.
3. Embedding Model에서 비교할 모델을 선택합니다.
4. 동일한 질문을 입력합니다.
5. `답변 근거 문서 보기`에서 Retriever가 검색한 문서 조각과 페이지를 확인합니다.
6. Embedding Model만 변경한 뒤 동일한 조건과 질문으로 다시 테스트합니다.
7. small / large 모델의 검색 결과를 비교합니다.

## 비교 시 고정할 조건

임베딩 모델 외의 조건은 동일하게 유지합니다.

- PDF 문서
- Chunk Size
- Chunk Overlap
- Retriever k
- 질문
- RAG Prompt
- LLM
- Vector Store (FAISS)

## 비교 기준

최종 생성 답변보다는 `답변 근거 문서 보기`에 표시되는
Retriever의 검색 결과를 기준으로 비교하는 것을 권장합니다.

예를 들어 다음 항목을 확인할 수 있습니다.

- 정답 근거가 포함된 Chunk가 Top-K 안에 검색되었는지
- 정답 근거 Chunk가 몇 번째 순위로 검색되었는지
- 두 모델이 검색한 문서 Chunk에 차이가 있는지

최종 생성 답변은 PDF 텍스트 추출 상태와 LLM의 응답에도 영향을 받을 수 있으므로,
임베딩 모델 자체의 검색 성능을 비교할 때는 Retriever 결과를 우선 확인합니다.

## 실행 방법

OpenAI API Key를 로컬 `.env` 파일에 설정한 후 실행합니다.

```env
OPENAI_API_KEY=your_api_key
streamlit run app.py
```
.env 파일과 API Key는 GitHub에 업로드하지 말아주세요햣 .

현재 프로젝트의 최종 RAG 구조는 PostgreSQL + pgvector 기반으로 개발 중이며,
본 코드는 DA 임베딩 모델 비교를 위한 사전 테스트용 FAISS 환경입니다.

최종 모델 선정 또는 통합 단계에서는 실제 프로젝트의 pgvector 환경에서
추가 검증할 수 있습니다.