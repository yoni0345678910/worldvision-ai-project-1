"""
RAG 파라미터 튜닝 및 검색 결과 비교를 위한 Streamlit 테스트 UI.

조절 가능한 파라미터:
- Chunk Size
- Chunk Overlap
- Retriever Top-K

파라미터 조절 파트는 1. 사이드바 설정, 2. PDF 업로드 처리 중 해시 부분을 참고하시면 됩니다.
또한 실제 파라미터 적용은 rag_module.py의 create_rag_chain()에서 수행합니다.

출처 반환은 # 7. 실제 검색 출처 표시 부분 표시한 부분까지 참고해주시면 됩니다.

PDF 또는 RAG 파라미터가 변경되면 RAG Chain을 다시 생성하여
조건별 검색 결과와 실제 Retriever가 검색한 문서 조각을 비교할 수 있습니다.

※ 기존 프로토타입에서 사용한 참고용 코드이며,
현재 FastAPI 기반 서비스에 직접 연결된 코드는 아닙니다.
"""

import os
import hashlib
import tempfile

import streamlit as st

from rag_module import create_rag_chain


st.set_page_config(
    page_title="RAG 멘토링 챗봇",
    layout="wide"
)

st.title("🤖 PDF 기반 RAG 시스템")
st.markdown("업로드한 문서에 대해 질문해 보세요.")


# --------------------------------------------------
# 1. 사이드바 설정
# --------------------------------------------------

with st.sidebar:
    st.header("설정")

    uploaded_file = st.file_uploader(
        "PDF 파일을 업로드하세요",
        type=["pdf"]
    )

    st.divider()

    st.subheader("RAG 파라미터")

    chunk_size = st.slider(
        "Chunk Size",
        min_value=200,
        max_value=2000,
        value=1000,
        step=100
    )

    chunk_overlap = st.slider(
        "Chunk Overlap",
        min_value=0,
        max_value=500,
        value=200,
        step=50
    )

    top_k = st.slider(
        "Retriever k",
        min_value=1,
        max_value=10,
        value=4,
        step=1
    )


# --------------------------------------------------
# 2. PDF 업로드 처리
# --------------------------------------------------

if uploaded_file:

    file_bytes = uploaded_file.getvalue()

    # 파일 내용 + RAG 파라미터를 함께 해시화
    # → PDF 또는 파라미터가 바뀌면 체인을 새로 생성
    # [RAG 튜닝 참고]
    # PDF뿐 아니라 RAG 파라미터도 해시에 포함하여
    # Chunk Size / Overlap / Top-K 중 하나라도 변경되면
    # 새로운 설정으로 RAG Chain을 다시 생성
    hash_input = (
        file_bytes
        + str(chunk_size).encode()
        + str(chunk_overlap).encode()
        + str(top_k).encode()
    )

    current_hash = hashlib.sha256(hash_input).hexdigest()

    # 처음 업로드하거나 PDF/파라미터가 변경된 경우
    if st.session_state.get("rag_hash") != current_hash:

        temp_path = None

        try:
            with st.spinner("문서를 분석 중입니다..."):

                # 안전한 임시 PDF 생성
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf"
                ) as temp_file:

                    temp_file.write(file_bytes)
                    temp_path = temp_file.name

                # 새로운 문서 기준 RAG Chain 생성
                # [RAG 튜닝 참고]
                # UI에서 선택한 파라미터를 실제 RAG 생성 함수에 전달
                rag_chain, retriever, stats = create_rag_chain(
                    temp_path,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    top_k=top_k
                )

                # 세션에 저장
                st.session_state.rag_chain = rag_chain
                st.session_state.retriever = retriever
                st.session_state.stats = stats

                # 현재 PDF + 파라미터 상태 저장
                st.session_state.rag_hash = current_hash

                # 새 문서 또는 파라미터 변경 시
                # 기존 대화 기록 초기화
                st.session_state.messages = []

            st.success("분석 완료!")

        except Exception as e:

            # 실패한 체인을 남겨두지 않음
            st.session_state.pop("rag_chain", None)
            st.session_state.pop("retriever", None)
            st.session_state.pop("stats", None)
            st.session_state.pop("rag_hash", None)

            st.error(
                "문서를 분석하는 중 오류가 발생했습니다."
            )

            with st.expander("오류 상세 보기"):
                st.exception(e)

        finally:

            # RAG 생성 후 임시 PDF 삭제
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)


    # --------------------------------------------------
    # 3. 문서 처리 결과 표시
    # --------------------------------------------------

    if "stats" in st.session_state:

        stats = st.session_state.stats

        st.subheader("📊 문서 처리 결과")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "페이지 수",
                stats["page_count"]
            )

        with col2:
            st.metric(
                "청크 수",
                stats["chunk_count"]
            )

        with col3:
            st.metric(
                "Chunk Size",
                stats["chunk_size"]
            )

        with col4:
            st.metric(
                "Retriever k",
                stats["top_k"]
            )

        st.caption(
            f"Chunk Overlap: {stats['chunk_overlap']}"
        )

        st.divider()


    # --------------------------------------------------
    # 4. 채팅 인터페이스
    # --------------------------------------------------

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 기존 대화 표시
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            # 이전 답변의 출처도 다시 표시
            if (
                message["role"] == "assistant"
                and message.get("sources")
            ):

                with st.expander("답변 근거 문서 보기"):

                    for index, source in enumerate(
                        message["sources"],
                        start=1
                    ):

                        st.markdown(
                            f"**출처 {index} — "
                            f"{source['page']}**"
                        )

                        st.write(source["content"])

                        st.divider()


    # --------------------------------------------------
    # 5. 사용자 질문 처리
    # --------------------------------------------------

    prompt = st.chat_input("질문을 입력하세요")

if "rag_chain" in st.session_state and prompt:
        # 사용자 메시지 저장
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        with st.chat_message("user"):
            st.markdown(prompt)


        # --------------------------------------------------
        # 6. 답변 생성
        # --------------------------------------------------

        with st.chat_message("assistant"):

            try:

                with st.spinner("답변 생성 중..."):

                    # RAG 답변 생성
                    response = (
                        st.session_state
                        .rag_chain
                        .invoke(prompt)
                    )

                    # 실제 Retriever가 찾은 문서 조각
                    source_docs = (
                        st.session_state
                        .retriever
                        .invoke(prompt)
                    )

                st.markdown(response)


                # ------------------------------------------
                # 7. 실제 검색 출처 표시
                # ------------------------------------------
                # [출처 반환 참고]
                # Retriever가 실제 검색한 Document의 metadata와 본문을 이용해
                # 답변 근거 페이지 및 Chunk 내용을 표시
                sources = []

                for doc in source_docs:

                    page_number = doc.metadata.get(
                        "page",
                        None
                    )

                    if isinstance(page_number, int):
                        page_label = (
                            f"페이지 {page_number + 1}"
                        )
                    else:
                        page_label = "페이지 정보 없음"

                    sources.append(
                        {
                            "page": page_label,
                            "content": doc.page_content
                        }
                    )
                #여기까지 출처 반환 참고           

                with st.expander(
                    "답변 근거 문서 보기"
                ):

                    for index, source in enumerate(
                        sources,
                        start=1
                    ):

                        st.markdown(
                            f"**출처 {index} — "
                            f"{source['page']}**"
                        )

                        st.write(source["content"])

                        st.divider()


                # 답변 + 출처를 대화 기록에 저장
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": response,
                        "sources": sources
                    }
                )


            except Exception as e:

                st.error(
                    "답변을 생성하는 중 오류가 발생했습니다."
                )

                with st.expander("오류 상세 보기"):
                    st.exception(e)


else:

    st.info(
        "왼쪽 사이드바에서 PDF 파일을 "
        "업로드하면 대화가 시작됩니다."
    )