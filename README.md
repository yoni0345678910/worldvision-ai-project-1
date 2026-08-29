👉 [WorldVision AI Assistant 바로가기](https://worldvision-ai-371850336678.asia-northeast3.run.app/docs)
현재 테스트 배포 버전이며, 최종 배포 완료 후 서비스 URL로 업데이트 예정입니다.

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
| **이수빈** | 프로젝트 오너 | • 전체 프로젝트 일정 및 리소스 관리<br>• 서비스 요구사항 정의 및 최종 결과물 검수 |
| **김가연** | AI 솔루션 아키텍트 | • 시스템 전체 AI 백엔드/서비스 아키텍처 설계<br>• 데이터 흐름 및 파이프라인 구조화 |
| **유고은** | AI 엔지니어 | • FastAPI 기반 RESTful API 설계 및 연동<br>• LangChain / OpenAI 활용 핵심 서비스 모듈 개발<br>• RAG 지식검색 및 Whisper STT 회의록 변환 기능 구현 |
| **김은채** | AI 데이터 사이언티스트 | • 서비스 입출력 데이터 전처리 및 품질 검증<br>• RAG 텍스트 임베딩 데이터셋 구성 및 프롬프트 최적화 |
| **정예은** | 클라우드 엔지니어 | • 개발 및 배포 환경(Environment) 설정<br>• 의존성 관리, 서버 파이프라인 및 가상환경 안정화 |

---

## 🛠️ 3. 기술 스택 (Tech Stack)

* **Language**: Python 3.14
* **Package Manager**: `uv`
* **Framework**: FastAPI, Uvicorn
* **AI & LLM**: LangChain, LangGraph, OpenAI API (GPT-4o / GPT-4o-mini, Whisper STT)
* **Database / Vector Search**: PostgreSQL, `pgvector`
* **Monitoring / Tracing**: Langfuse

---

## 🔥 4. 주요 기능 설명

### 1) 🔍 사내 지식검색 API (`/api/v1/search`)
* PostgreSQL/pgvector 기반 RAG 지식검색 및 사내 문서 기반 답변 생성
* Vector Search와 Keyword Search를 결합한 Hybrid Retrieval 적용
* Source/Page Metadata 기반 동일 페이지 Chunk 조회 및 Reranking을 통한 검색 정확도 개선
* 답변과 함께 참고 문서의 출처(Source) 제공

### 2) 📝 AI 회의록 작성 API (`/api/v1/minutes`)
* 회의 음성 파일(mp3, m4a 등) 업로드 및 Whisper 기반 STT 수행
* 회의 요약, 주요 논의사항, 결정사항을 구조화하여 자동 생성
* 업로드된 회의 내용을 기반으로 AI 회의록 생성

### 3) 📊 AI 보고서 생성 API (`/api/v1/report`)
* 사용자가 입력한 주제를 기반으로 AI 보고서 초안 생성
* 보고서 제목, 요약 및 본문을 구조화하여 제공

### 4) 🤖 LangGraph 기반 AI Agent
* LangGraph를 활용하여 사용자 요청에 따라 지식검색, 회의록, 보고서 기능으로 자동 라우팅
* 기능별 서비스 모듈을 하나의 Agent Workflow로 통합

### 5) 🧠 대화 Memory
* Session 기반 대화 History 관리
* Semantic Memory를 활용하여 이전 대화의 관련 정보를 검색하고 답변 Context에 반영

### 6) 📈 Langfuse 모니터링
* Langfuse를 활용한 AI 요청 및 실행 과정 Tracing
* RAG 검색 및 Agent Workflow의 실행 흐름 모니터링

## 📸 5. 데모 화면

WorldVision AI Assistant는 **사내 지식검색, AI 회의록 작성, AI 보고서 생성** 기능을 하나의 웹 인터페이스에서 제공합니다.

### 🔍 사내 지식검색
사내 문서를 기반으로 사용자의 질문과 관련된 정보를 검색하고, 출처를 기반으로 답변을 생성합니다.

![사내 지식검색 데모](docs/images/지식검색_데모.png)

### 📝 AI 회의록
회의 음성 파일을 업로드하면 STT를 통해 내용을 변환하고, 주요 논의사항과 결정사항을 구조화된 회의록으로 생성합니다.

![AI 회의록 데모](docs/images/회의록_데모.png)

### 📊 AI 보고서
사용자가 보고서 주제를 입력하면 관련 내용을 바탕으로 구조화된 보고서 초안을 생성합니다.

![AI 보고서 데모](docs/images/보고서_데모.png)


### 1) 환경 변수 설정

프로젝트 최상위 경로에 `.env` 파일을 생성하고 아래 환경 변수를 설정합니다.

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# PostgreSQL / pgvector
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE

# Langfuse
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
