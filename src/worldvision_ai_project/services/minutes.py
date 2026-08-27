import io
import json
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# OpenAI 클라이언트 초기화 (.env의 OPENAI_API_KEY 사용)
client = OpenAI()

def process_audio_minutes(audio_file_bytes: bytes, file_name: str = "meeting.m4a"):
    try:
        # 1. 실제 음성 바이너리 데이터를 파일 객체 형태로 전환하여 Whisper STT 실행
        audio_file = io.BytesIO(audio_file_bytes)
        audio_file.name = file_name  # Whisper API가 확장자를 인식할 수 있도록 이름 지정

        transcript_obj = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
        real_transcript = transcript_obj.text

        # 음성 변환 결과가 빈 값일 때 예외 처리
        if not real_transcript or not real_transcript.strip():
            real_transcript = f"파일명 {file_name}에서 인식된 음성 텍스트가 없습니다."

    except Exception as e:
        print(f"[Whisper STT Error]: {e}")
        real_transcript = f"음성 변환 실패 (파일명: {file_name})"

    # 2. GPT를 이용해 실제 추출된 텍스트 기반 요약 및 구조화
    prompt = ChatPromptTemplate.from_template("""
    당신은 회의록 작성 전문가입니다. 아래 회의 음성 텍스트를 분석하여 반드시 아래 지정된 JSON 형식으로만 답변해 주세요.

    [회의 내용]:
    {transcript}

    [반환 형식 (JSON만 출력)]:
    {{
      "summary": "회의 전체 내용을 2~3줄로 요약한 문자열",
      "key_issues": ["주요 논의사항 1", "주요 논의사항 2"],
      "decisions": ["결정사항 1", "결정사항 2"]
    }}
    """)
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
    chain = prompt | llm
    
    response = chain.invoke({"transcript": real_transcript})
    
    # 3. JSON 파싱
    try:
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
            
        result_json = json.loads(content.strip())
        
        return {
            "summary": result_json.get("summary", "요약 내용을 추출하지 못했습니다."),
            "key_issues": result_json.get("key_issues", ["주요 논의사항 없음"]),
            "decisions": result_json.get("decisions", ["결정사항 없음"])
        }
    except Exception as e:
        return {
            "summary": response.content,
            "key_issues": ["분석 중 논의사항 추출 실패"],
            "decisions": ["분석 중 결정사항 추출 실패"]
        }