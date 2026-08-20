# World Vision AI Project

월드비전 생성형 AI 기반 업무지원 서비스의 FastAPI Entry 기본 구조입니다.

현재 지식검색, 회의록 생성, 보고서 생성 기능의 API 입출력 구조를 정의하고,
각 기능의 Workflow를 연결할 수 있도록 기본 Endpoint를 구성했습니다.

## 구현된 API

| Method | Endpoint | 설명 |
| --- | --- | --- |
| GET | `/health` | 서버 상태 확인 |
| POST | `/search` | 지식검색 요청 |
| POST | `/minutes` | 회의 음성 파일 업로드 및 회의록 생성 요청 |
| POST | `/report` | 보고서 생성 요청 |

현재 `/search`, `/minutes`, `/report`는 실제 AI Workflow 연결 전 단계이며,
입출력 규격 및 API 동작 확인을 위한 기본 응답을 반환합니다.

## 실행 방법

### 1. 의존성 설치

```bash
uv sync

```

### 2. 개발 서버 실행

```bash
uv run uvicorn worldvision_ai_project.main:app --reload --app-dir src
```

### 3. API 문서 확인

서버 실행 후 아래 주소에서 Swagger UI를 통해 API를 확인하고 테스트할 수 있습니다.

`http://127.0.0.1:8000/docs`

## 프로젝트 구조

```text
worldvision-ai-project/
├── src/
│   └── worldvision_ai_project/
│       ├── __init__.py
│       ├── main.py
│       └── schemas.py
├── .gitignore
├── .python-version
├── pyproject.toml
├── uv.lock
└── README.md
```

- `main.py`: FastAPI 애플리케이션 및 API Endpoint 정의
- `schemas.py`: Pydantic 기반 Request/Response 데이터 규격 정의
- `pyproject.toml`: 프로젝트 정보 및 의존성 설정
- `uv.lock`: 의존성 버전 정보

## 현재 구현 상태

- FastAPI Entry 기본 구조 구성
- Pydantic 기반 Request/Response 규격 정의
- `/health` 서버 상태 확인
- `/search` 지식검색 요청 및 입력값 검증
- `/minutes` 회의 음성 파일 업로드 및 요청 처리
- `/report` 보고서 생성 요청 및 입력값 검증
- Swagger UI를 통한 API 동작 테스트

현재 단계에서는 각 AI 기능의 실제 Workflow를 구현하지 않고,
FastAPI Entry와 기능별 입출력 인터페이스를 우선 구성했습니다.

## 향후 연동

각 Endpoint에 기능별 AI Workflow를 연결하여 확장할 수 있습니다.

- `/search` → RAG 기반 지식검색 Workflow
- `/minutes` → STT + LLM 기반 회의록 생성 Workflow
- `/report` → LLM 기반 보고서 생성 Workflow