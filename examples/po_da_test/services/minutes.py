import os
import tempfile
from dotenv import load_dotenv
from fastapi import HTTPException, status, UploadFile
from openai import OpenAI, AuthenticationError, RateLimitError, APITimeoutError, APIConnectionError

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

async def process_audio_minutes(file: UploadFile):
    # 0. API Key 존재 검증
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OpenAI API 키가 설정되지 않았증니다. .env 파일을 확인해 주세요."
        )

    # 1. 파일 확장자 검증
    allowed_extensions = [".mp3", ".m4a", ".wav", ".mp4", ".mpeg"]
    file_ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"지원하지 않는 파일 형식입니다. (가능한 형식: {', '.join(allowed_extensions)})"
        )
    
    # 2. 파일 용량 및 0byte 검증
    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="빈 파일은 업로드할 수 없습니다."
        )

    # 3. 임시 파일로 저장 후 OpenAI Whisper API 호출
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
        tmp_file.write(contents)
        tmp_path = tmp_file.name

    try:
        # 3-1. Whisper API (STT: 음성 -> 텍스트)
        with open(tmp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        
        stt_text = transcript.text

        # 3-2. GPT를 통한 회의록 요약
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 회의록 정리 전문가야. 음성 변환 텍스트를 바탕으로 핵심 내용, 논의 사항, Action Item을 깔끔하게 요약해줘."},
                {"role": "user", "content": f"다음 회의 변환 텍스트를 요약해줘:\n\n{stt_text}"}
            ],
            timeout=30.0
        )
        
        summary = response.choices[0].message.content

        return {
            "filename": file.filename,
            "transcript": stt_text,
            "summary": summary
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
            detail=f"회의록 처리 중 내부 오류 발생: {str(e)}"
        )
    finally:
        # 임시 파일 삭제
        if os.path.exists(tmp_path):
            os.remove(tmp_path)