import os

from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 1. 회의록 구조화 프롬프트 템플릿
MINUTES_PROMPT_TEMPLATE = """
당신은 월드비전의 전문 회의록 작성 AI 도우미입니다.
아래 제공된 [회의 음성 텍스트]를 바탕으로 회의록을 작성해 주세요.

[요구사항]:
1. 회의의 전체적인 요약(minutes)을 작성하세요.
2. 회의에서 다루어진 주요 논의사항(key_points)을 리스트 형식으로 정리하세요.
3. 최종 결정된 사항(decisions)이 있다면 명확하게 작성해 주세요.

[회의 음성 텍스트]:
{transcript}

[출력 형식]:
답변은 아래 항목을 명확히 구분하여 작성하세요.
- 회의 요약:
- 주요 논의사항:
- 결정사항:
"""

# 2. 음성 파일 STT 및 회의록 생성 핵심 함수
def process_audio_minutes(audio_file_bytes: bytes, file_name: str):
    # 1) 음성 파일 임시 저장
    temp_file_path = f"temp_{file_name}"
    with open(temp_file_path, "wb") as f:
        f.write(audio_file_bytes)
        
    try:
        # 2) Whisper STT 호출 (음성 -> 텍스트)
        client = OpenAI()
        with open(temp_file_path, "rb") as audio_file:
            transcript_response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        transcript_text = transcript_response.text

        # 3) LLM을 통한 회의 내용 구조화
        prompt = ChatPromptTemplate.from_template(MINUTES_PROMPT_TEMPLATE)
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        chain = prompt | llm

        response = chain.invoke({"transcript": transcript_text})

        return {
            "minutes": response.content,
            "transcript": transcript_text
        }
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)