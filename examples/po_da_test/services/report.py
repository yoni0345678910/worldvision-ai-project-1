import os
from dotenv import load_dotenv
from fastapi import HTTPException, status
from openai import OpenAI, AuthenticationError, RateLimitError, APITimeoutError, APIConnectionError

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

async def generate_business_report(topic: str):
    # 0. API 키 검증
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OpenAI API 키가 설정되지 않았습니다. .env 파일을 확인해 주세요."
        )

    # 1. 입력값 검증 (공백 예외 처리)
    clean_topic = topic.strip() if topic else ""
    if not clean_topic:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="보고서 주제는 공백일 수 없습니다. 올바른 주제를 입력해 주세요."
        )

    # 2. GPT 보고서 생성 프롬프트 호출
    prompt = f"""
너는 전문 비즈니스 컨설턴트 및 기획자야.
제시된 주제를 바탕으로 고품질의 비즈니스 보고서 초안을 작성해줘.

[주제]: {clean_topic}

[보고서 구성]
1. 보고서 제목
2. 추진 배경 및 필요성
3. 현황 분석 및 주요 문제점
4. 세부 추진 방안
5. 기대 효과 및 향후 계획

전문적이고 명확한 어조로 작성해줘.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 보고서 작성 전문 AI 도우미야."},
                {"role": "user", "content": prompt}
            ],
            timeout=30.0
        )
        
        report_content = response.choices[0].message.content

        return {
            "topic": clean_topic,
            "report": report_content
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
            detail=f"보고서 생성 중 오류 발생: {str(e)}"
        )