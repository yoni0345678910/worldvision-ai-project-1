# Embedding Model Comparison

DA 임베딩 모델 비교 테스트를 위한 코드입니다.

기존 RAG 튜닝 프로토타입을 기반으로 하며,
동일한 검색 조건에서 OpenAI 임베딩 모델별 검색 결과를 비교할 수 있습니다.

## 비교 모델

- text-embedding-3-small
- text-embedding-3-large

## 테스트 방법

1. PDF 문서를 업로드합니다.
2. Chunk Size, Chunk Overlap, Retriever k를 설정합니다.
3. Embedding Model에서 비교할 모델을 선택합니다.
4. 동일한 질문을 입력합니다.
5. `답변 근거 문서 보기`에서 Retriever가 검색한 문서 조각과 페이지를 확인합니다.
6. Embedding Model만 변경한 뒤 동일한 질문으로 다시 테스트합니다.
7. small / large 모델의 검색 결과를 비교합니다.

## 비교 시 유의사항

임베딩 모델 비교 시 다음 조건은 동일하게 유지합니다.

- PDF 문서
- Chunk Size
- Chunk Overlap
- Retriever k
- 질문

Embedding Model만 변경하여 검색 결과를 비교합니다.

최종 생성 답변은 LLM 및 PDF 텍스트 추출 상태의 영향을 받을 수 있으므로,
임베딩 모델의 검색 성능 비교 시에는 `답변 근거 문서 보기`에 표시되는
Retriever의 검색 결과를 기준으로 확인하는 것을 권장합니다.

## 실행

프로젝트의 OpenAI API Key 설정 후 실행합니다.

```bash
streamlit run app.py
