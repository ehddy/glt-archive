# glt-archive

문장을 검색·등록·스크랩하는 아카이브 웹앱.

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| Frontend | Vue 3 (Options API), Vue Router, Vite |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Database | Supabase (PostgreSQL) / SQLite (로컬) |

---

## 로컬 실행

### 필요 환경

- Python 3.11+
- Node.js 18+

### 백엔드

```powershell
cd backend
copy .env.example .env   # API 키 입력 후
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 프론트엔드 (새 터미널)

```powershell
cd frontend
npm install
npm run dev
```

### 환경 변수 (`backend/.env`)

```env
DATABASE_URL=postgresql://...   # Supabase URI (미설정 시 SQLite)
GEMINI_API_KEY=                 # 챗봇용 (선택)
ALADIN_TTB_KEY=                 # 도서 검색용 (선택)
```

---

## 접속

| 서비스 | URL |
|--------|-----|
| Frontend | http://localhost:5173 |
| Backend | http://127.0.0.1:8000 |
| API 문서 | http://127.0.0.1:8000/docs |
