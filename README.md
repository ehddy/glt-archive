# 괴테는 모든 것을 말했다

> 한국 소설의 구절을 검색하고, 등록하고, 함께 편집하는 아카이브

**"이 말, 어디서 왔을까?"** — 문장만 기억나고 작품명이 생각나지 않을 때.  
구절·작가·작품으로 검색하고, 작품을 중심으로 구절이 가지처럼 뻗어 나가는 **라이브러리 그래프** UI로 탐색할 수 있습니다.

[![Repository](https://img.shields.io/badge/GitHub-glt--archive-181717?logo=github)](https://github.com/ehddy/glt-archive)

---

## 주요 기능

| 기능 | 설명 |
|------|------|
| **구절 검색** | 구절, 작가, 작품명 텍스트 매칭 검색 |
| **구절 등록** | 구절 · 작가 · 작품 3가지 필드로 간단 등록 |
| **협업 편집** | 구절 수정 + 버전 이력 자동 저장 |
| **책장 UI** | 책장에서 꺼낸 듯한 작품·구절 시각화 |
| **책 추천 챗봇** | Gemini로 비슷한 느낌의 작품·작가 추천 (우하단 📚) |
| **알라딘 도서 검색** | 구절 등록 시 알라딘 API로 작품 검색·선택, 상세 정보 DB 저장 |
| **시드 데이터** | 한국 문학 구절 12건 자동 등록 (최초 실행 시) |

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| Frontend | Vue 3 (Options API), Vue Router, Vite |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Database | **Supabase (PostgreSQL)** / SQLite (로컬 개발) |
| Infra | Docker Compose (선택, 로컬 PostgreSQL) |

프론트엔드는 **항상 백엔드 API(`/api`)** 를 통해 데이터를 가져옵니다.  
개발 환경에서는 Vite 프록시가 요청을 백엔드로 전달하고, 배포 환경에서는 nginx가 동일하게 처리합니다.

---

## 빠른 시작 (로컬)

Docker 없이 바로 실행할 수 있습니다.

### 필요 환경

- **Python** 3.11+
- **Node.js** 18+ ([nodejs.org](https://nodejs.org/) 또는 `conda install -c conda-forge nodejs=20`)

### 1. 저장소 클론

```powershell
git clone https://github.com/ehddy/glt-archive.git
cd glt-archive
```

### 2. Supabase DB 연동 (권장)

상세 가이드: **[docs/SUPABASE_SETUP.md](docs/SUPABASE_SETUP.md)**

1. [supabase.com](https://supabase.com) 가입 → 새 프로젝트 생성
2. **Project Settings → Database → Connection string (URI)** 복사
3. `backend/.env`에 설정:

```env
DATABASE_URL=postgresql://postgres.xxxxx:YOUR_PASSWORD@aws-0-ap-northeast-2.pooler.supabase.com:5432/postgres
```

### 3. 백엔드 환경 변수 (API 키)

```powershell
cd backend
copy .env.example .env
```

`.env` 파일에 Gemini API 키를 입력합니다. ([Google AI Studio](https://aistudio.google.com/apikey)에서 발급)

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash-lite
```

> 챗봇 없이 구절 검색만 사용할 경우 Gemini 설정은 생략할 수 있습니다.

알라딘 TTBKey도 같은 `.env`에 추가합니다. ([알라딘 Open API 가이드](https://www.aladin.co.kr/ttb/wguide.aspx))

```env
ALADIN_TTB_KEY=your_aladin_ttb_key_here
```

> 구절 등록 시 작품 검색에 알라딘 API가 필요합니다.

### 4. 백엔드 실행

```powershell
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

> `.env`를 수정했다면 백엔드를 **재시작**해야 챗봇에 반영됩니다.

- DB: Supabase URI 설정 시 클라우드 PostgreSQL, 미설정 시 SQLite (`backend/quotes.db`)
- API 문서: http://127.0.0.1:8000/docs
- 헬스체크: http://127.0.0.1:8000/api/health

### 5. 프론트엔드 실행 (새 터미널)

```powershell
cd frontend
npm install
npm run dev
```

터미널에 표시된 주소로 접속하세요. (보통 `http://localhost:5173`)

> **포트가 다를 수 있습니다.** 5173이 이미 사용 중이면 Vite가 5174, 5175 등 다른 포트를 사용합니다.  
> 반드시 **프론트 터미널에 출력된 URL**을 사용하고, 백엔드(8000)가 함께 실행 중인지 확인하세요.

### 한 번에 실행 (PowerShell)

```powershell
.\scripts\start-dev.ps1
```

---

## 접속 URL

| 서비스 | URL |
|--------|-----|
| Frontend | 터미널에 표시된 주소 (예: http://localhost:5173) |
| Backend API | http://127.0.0.1:8000 |
| API 문서 (Swagger) | http://127.0.0.1:8000/docs |

---

## API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| `GET` | `/api/health` | 서버 상태 확인 |
| `GET` | `/api/library` | 작품별 구절 라이브러리 (그래프용) |
| `GET` | `/api/quotes` | 구절 목록 |
| `GET` | `/api/quotes/search?q=` | 텍스트 검색 |
| `GET` | `/api/quotes/{id}` | 구절 상세 |
| `GET` | `/api/quotes/{id}/versions` | 수정 이력 |
| `POST` | `/api/quotes` | 구절 등록 |
| `PATCH` | `/api/quotes/{id}` | 구절 수정 |
| `GET` | `/api/authors` | 작가 목록 |
| `POST` | `/api/chat` | 책 추천 챗봇 (Gemini) |
| `GET` | `/api/aladin/search` | 알라딘 도서 검색 |
| `GET` | `/api/aladin/books/{item_id}` | 알라딘 도서 상세 조회 |
| `POST` | `/api/aladin/books/{item_id}` | 알라딘 도서 DB 저장 |

### 예시

```powershell
# 라이브러리 조회
Invoke-RestMethod "http://127.0.0.1:8000/api/library"

# 검색
Invoke-RestMethod "http://127.0.0.1:8000/api/quotes/search?q=기억"

# 등록
Invoke-RestMethod "http://127.0.0.1:8000/api/quotes" -Method POST `
  -ContentType "application/json" `
  -Body '{"text":"...", "author_name":"한강", "novel_title":"소년이 온다"}'
```

---

## Docker Compose (선택)

Docker가 설치된 환경에서 PostgreSQL + nginx 포함 전체 스택을 실행합니다.

```bash
docker compose up --build
```

| 서비스 | URL |
|--------|-----|
| Frontend | http://localhost |
| Backend API | http://localhost:8000 |
| PostgreSQL | localhost:5432 |

---

## 환경 변수

`backend/.env.example`을 참고해 `backend/.env`를 만들 수 있습니다.

```env
# 로컬 (기본값 — PostgreSQL 불필요)
DATABASE_URL=sqlite:///./quotes.db
```

Docker 환경에서는 `docker-compose.yml`이 PostgreSQL URL을 자동 설정합니다.

---

## DB 초기화

시드 데이터를 다시 넣으려면 `backend/quotes.db`를 삭제한 뒤 백엔드를 재시작하세요.

---

## 프로젝트 구조

```
glt-archive/
├── docker-compose.yml
├── scripts/
│   └── start-dev.ps1          # 로컬 개발 서버 일괄 실행
├── backend/
│   ├── app/
│   │   ├── main.py            # 앱 진입점, 라우터 등록
│   │   ├── routers/           # quotes, novels, authors API
│   │   ├── services/          # 비즈니스 로직
│   │   ├── models/            # SQLAlchemy 모델
│   │   ├── schemas/           # Pydantic 스키마
│   │   └── seed/              # 한국 문학 시드 데이터
│   ├── requirements.txt
│   └── Dockerfile
└── frontend/
    ├── src/
    │   ├── api/               # 백엔드 API 클라이언트 (/api 프록시)
    │   ├── views/             # Home, Register, QuoteDetail
    │   ├── components/        # BookNode, BookHub, QuoteBranch
    │   └── design-system/     # 디자인 토큰 & 공통 스타일
    ├── vite.config.js         # /api → 백엔드 프록시
    ├── nginx.conf             # 배포 시 /api 프록시
    └── Dockerfile
```

---

## 로드맵

- [ ] 알라딘 API 연동 (작품 검색 · ISBN 메타데이터)
- [ ] 의미 기반(시맨틱) 검색
- [ ] 사용자 인증 / 권한 관리
- [ ] 편집 diff UI

---

## 라이선스

MIT (또는 추후 명시)
