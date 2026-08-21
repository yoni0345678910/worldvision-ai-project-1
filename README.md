# 🌍 WorldVision AI Assistant (월드비전 AI 어시스턴트)

월드비전 임직원의 업무 효율 향상 및 단순 반복 업무 축소를 위한 **AI 백엔드 프로토타입 시스템**입니다.

---

## 📌 1. 프로젝트 소개
* **서비스명**: 월드비전 AI 어시스턴트 (WorldVision AI Assistant API)
* **목적**: 
  * 사내 문서 기반의 정확한 정보 제공 (지식검색 RAG)
  * 회의 음성 파일의 자동 텍스트 변환 및 주요 안건/결정사항 요약 (AI 회의록)
  * 백엔드 API 중심의 확장성 있는 AI 에이전트 구조 설계

---

## 👥 2. 팀원 및 역할 분담

| 이름 | 역할 | 담당 업무 |
| :---: | :---: | :--- |
| **유고은** | 백엔드 & AI 엔지니어링 | • FastAPI 기반 RESTful API 아키텍처 설계<br>• LangChain / OpenAI 연동 서비스 모듈 개발<br>• RAG 기반 지식검색 및 Whisper STT 회의록 변환 파이프라인 구축 |
| **[팀원2 이름]** | [담당 역할] | • [주요 담당 업무 작성] |
| **[팀원3 이름]** | [담당 역할] | • [주요 담당 업무 작성] |

---

## 🛠️ 3. 기술 스택 (Tech Stack)

* **Language**: Python 3.14
* **Package Manager**: `uv`
* **Framework**: FastAPI, Uvicorn
* **AI & LLM**: LangChain, OpenAI API (GPT-4o / GPT-4o-mini, Whisper STT)
* **Database / Vector Search**: PostgreSQL, `pgvector`

---

## 🔥 4. 주요 기능 설명

### 1) 🔍 사내 지식검색 API (`/api/v1/search`)
* PostgreSQL/pgvector 기반의 임베딩 문서 유사도 검색(RAG) 지원
* 사용자 질문에 맞춰 사내 문서 내 정확한 출처(Source)와 함께 답변 생성

### 2) 📝 AI 회의록 작성 API (`/api/v1/minutes`)
* 회의 음성 파일(mp3, m4a 등) 업로드 및 Whisper 모델 기반 STT(Text Extraction) 수행
* 회의 요약, 주요 논의사항, 최종 결정사항을 구조화된 JSON 형태로 자동 추출

### 3) 📊 AI 보고서 생성 API (`/api/v1/report` - 예정)
* 수집된 개요 및 데이터를 바탕으로 AI 자동 보고서 초안 생성

---

## 📸 5. 데모 스크린샷
<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/f311c6ac-adca-459b-989a-545cac5c3456" />

### API 문서화 및 대시보드 (Swagger UI)
![Swagger UI](https://via.placeholder.com/800x400?text=Swagger+UI+Screenshot+Here)
> `http://127.0.0.1:8000/docs` 경로에서 interactive하게 API 테스트를 진행할 수 있습니다.

---

## 🚀 6. 실행 방법 (Local Run)

### 1) 환경 변수 설정
최상위 경로에 `.env` 파일 생성 후 OpenAI API 키 등록:
```env
OPENAI_API_KEY=sk-proj-...