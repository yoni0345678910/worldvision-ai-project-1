FROM python:3.11-slim

WORKDIR /app

# 시스템 필수 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 프로젝트 설정 및 의존성 패키지 설치
COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN pip install --no-cache-dir .

EXPOSE 8000

# uvicorn 실행
CMD ["uvicorn", "worldvision_ai_project.main:app", "--host", "0.0.0.0", "--port", "8000"]