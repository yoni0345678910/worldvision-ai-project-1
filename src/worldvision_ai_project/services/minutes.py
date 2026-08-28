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
            file=audio_file,
            language="ko"
        )
        real_transcript = transcript_obj.text
        print(f"[Whisper Transcript]: {real_transcript}")   #녹음 전체가 찍힐 수 있도록 수정

        # 음성 변환 결과가 빈 값일 때 예외 처리
        if not real_transcript or not real_transcript.strip():
            return {
                "summary": "인식된 음성 내용이 없어 회의록을 생성할 수 없습니다.",
                "key_issues": [],
                "decisions": []
            }

    except Exception as e:
        print(f"[Whisper STT Error]: {e}")
        return {
            "summary": "음성 변환에 실패하여 회의록을 생성할 수 없습니다.",
            "key_issues": [],
            "decisions": []
        }

    # 2. GPT를 이용해 실제 추출된 텍스트 기반 요약 및 구조화
    prompt = ChatPromptTemplate.from_template("""
당신은 정확성과 정보 보존을 최우선으로 하는 회의록 작성 전문가입니다.
아래 회의 음성 텍스트에 명시된 내용만 사용하여 회의록을 작성하세요.

[회의 내용]:
{transcript}

[작성 지침]:
1. 회의의 핵심 목적과 전체 흐름을 summary에 2~3줄로 요약하세요.
2. 주요 논의 주제, 문제점, 검토 사항은 key_issues에 빠짐없이 정리하세요.
3. 회의에서 결정되었거나 실행하기로 한 내용은 decisions에 모두 포함하세요.
4. 특히 다음 정보가 원문에 있다면 절대 생략하지 마세요.
   - 담당자
   - 담당 업무
   - 마감일 또는 시간
   - 후속 조치
5. 담당자, 업무, 기한이 함께 언급된 경우 하나의 결정사항 안에 함께 작성하세요.
   예: "세모세모님은 내일 오전까지 프론트엔드와 백엔드 API 연결 상태를 확인한다."
6. 원문에 없는 담당자, 일정, 결정사항을 추측하거나 생성하지 마세요.
7. 논의만 되었고 확정되지 않은 내용은 결정사항으로 작성하지 마세요.
8. 내용이 여러 개라면 임의로 2개만 선택하지 말고 중요한 항목을 모두 반환하세요.
9. 반드시 아래 JSON 형식만 출력하세요. 코드블록이나 추가 설명은 출력하지 마세요.

[반환 형식]:
{{
  "summary": "회의 전체 내용을 2~3줄로 요약한 문자열",
  "key_issues": [
    "주요 논의사항 1",
    "주요 논의사항 2"
  ],
  "decisions": [
    "담당자·업무·기한을 포함한 결정사항 1",
    "결정사항 2"
  ]
}}
""")
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)   #창의성이 필요 없으므로 0이 적합
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