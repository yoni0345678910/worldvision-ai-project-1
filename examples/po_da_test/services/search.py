import uuid
import os
from dotenv import load_dotenv  # 1. 추가
from fastapi import HTTPException, status
from openai import OpenAI, AuthenticationError, RateLimitError, APITimeoutError, APIConnectionError
from examples.po_da_test.services.chat_history import history_manager

# 2. .env 파일의 환경변수 로드 추가
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def run_knowledge_search(
    query: str, 
    session_id: str = None,
    top_k: int = 3, 
    threshold: float = 0.7
):
    # 1. Validation (검색어 공백 및 최소 길이)
    clean_query = query.strip() if query else ""
    if not clean_query or len(clean_query) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="검색어는 공백을 제외하고 최소 2자 이상 입력해야 합니다."
        )

    # 2. session_id 생성 및 이력 조회
    if not session_id or not session_id.strip():
        session_id = str(uuid.uuid4())
    else:
        session_id = session_id.strip()

    prev_messages = history_manager.get_history(session_id)

    # 3. Prompt 메시지 구성 (기존 이력 포함)
    messages = [
        {"role": "system", "content": "너는 월드비전 지식 도우미야. 이전 대화 맥락을 기억하고 답변해줘."}
    ]
    messages.extend(prev_messages)
    messages.append({"role": "user", "content": clean_query})

    # 4. OpenAI API 호출
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            timeout=5.0
        )
        answer_text = response.choices[0].message.content

        # 5. 대화 이력 업데이트
        history_manager.add_user_message(session_id, clean_query)
        history_manager.add_assistant_message(session_id, answer_text)

        return {
            "session_id": session_id,
            "query": clean_query,
            "answer": answer_text,
            "sources": ["doc_01.pdf", "doc_02.pdf"]
        }

    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OpenAI API 키 인증에 실패했습니다."
        )
    except RateLimitError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="OpenAI API 호출 한도가 초과되었습니다."
        )
    except (APITimeoutError, APIConnectionError):
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="AI 서비스 연결 시간이 초과되었습니다."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"서버 내부 오류: {str(e)}"
        )