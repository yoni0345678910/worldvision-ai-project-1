# WorldVision AI Assistant Frontend

`src/worldvision_ai_project/main.py` 백엔드의 세 API에 맞춘 React + Vite 프론트엔드입니다.

- 사내 지식검색: 기존 서버 자료를 검색합니다. 문서 업로드 기능은 백엔드가 지원하지 않아 포함하지 않았습니다.
- AI 회의록: 백엔드가 지원하는 회의 음성 파일 업로드를 사용합니다.
- AI 보고서: 입력한 주제로 보고서 초안을 생성합니다.

## 로컬 실행

먼저 프로젝트 최상위 폴더에서 백엔드를 실행합니다.

```bash
uv run uvicorn worldvision_ai_project.main:app --app-dir src --reload --port 8000
```

그 다음 새 터미널에서 프론트엔드를 실행합니다.

```bash
cd frontend
npm install
npm run dev
```

브라우저에서 `http://localhost:5173`을 엽니다. 개발 환경에서는 Vite 프록시가 `/api` 요청을 `http://localhost:8000`으로 전달하므로 별도 CORS 설정이 필요하지 않습니다.

## 배포 API 주소 설정

다른 백엔드를 사용할 때만 `.env.example`을 `.env`로 복사하고 주소를 바꿉니다.

```env
VITE_API_BASE_URL=
VITE_PROXY_TARGET=https://백엔드주소.run.app
```

`.env`를 바꾼 뒤에는 프론트엔드 개발 서버를 껐다가 다시 실행해야 합니다.

다른 도메인에 프론트엔드를 배포하면 백엔드에 해당 프론트엔드 주소를 허용하는 CORS 설정이 필요합니다.
