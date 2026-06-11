# Vercel 배포 (프론트 + 백엔드 한 프로젝트)

프론트(Vite)와 백엔드(FastAPI)를 **같은 Vercel 프로젝트**에서 배포합니다.

- `/` → Vue 정적 파일 (`frontend/dist`)
- `/api/*` → FastAPI 서버리스 함수 (`api/index.py`)

## 1. Vercel 대시보드 설정 (중요)

**Settings → Build and Deployment** 에서 아래처럼 바꿉니다.

| 항목 | 값 |
|------|-----|
| **Root Directory** | 비움 (`.` = 저장소 루트) |
| **Framework Preset** | Other |
| **Install Command** | `cd frontend && npm install` |
| **Build Command** | `cd frontend && npm run build` |
| **Output Directory** | `frontend/dist` |

> 지금 `frontend`만 Root로 두면 **백엔드 폴더가 배포에 포함되지 않습니다.**  
> 반드시 Root Directory를 **비우거나 프로젝트 루트**로 설정하세요.

`vercel.json`이 루트에 있으면 위 명령은 자동 적용됩니다. 대시보드 값과 겹치면 `vercel.json`이 우선합니다.

## 2. 환경 변수 (Settings → Environment Variables)

| 변수 | 필수 | 설명 |
|------|------|------|
| `DATABASE_URL` | ✅ | Supabase PostgreSQL URI (SQLite는 Vercel에서 **불가**) |
| `ALADIN_TTB_KEY` | ✅ | 알라딘 API 키 |
| `GEMINI_API_KEY` | 챗봇용 | Gemini API 키 |
| `GEMINI_MODEL` | 선택 | 기본 `gemini-2.5-flash-lite` |
| `CORS_ORIGINS` | 선택 | 커스텀 도메인 추가 시 `https://your-domain.com` |

Supabase 연결 방법: [SUPABASE_SETUP.md](./SUPABASE_SETUP.md)

## 3. 배포 후 확인

```text
https://<your-project>.vercel.app/api/health
```

`{"status":"ok", ...}` 가 나오면 백엔드 연결 성공입니다.

## 4. 로컬에서 Vercel과 비슷하게 테스트

```powershell
npm i -g vercel
cd <프로젝트 루트>
vercel dev
```

- 프론트: `http://localhost:3000`
- API: `http://localhost:3000/api/health`

## 5. 구조

```text
mvp_project/
├── vercel.json          # 빌드·라우팅
├── api/
│   ├── index.py         # FastAPI 진입점
│   └── requirements.txt
├── backend/             # FastAPI 앱
└── frontend/            # Vue + Vite
```

프론트는 `VITE_API_BASE` 없이 **같은 도메인 `/api`** 를 호출합니다 (이미 `frontend/src/api/index.js` 기본값).

## 6. 주의사항

- **DB**: Vercel 서버리스는 디스크가 없어 SQLite를 쓸 수 없습니다. Supabase(PostgreSQL) 필수.
- **챗봇**: 응답이 길면 서버리스 타임아웃(무료 플랜 10초)에 걸릴 수 있습니다. `vercel.json`에 `maxDuration: 60` 설정해 두었으나 Pro 플랜에서만 60초까지 가능합니다.
- **시드 데이터**: 최초 데이터는 로컬에서 `python backend/scripts/reset_aladin_seed.py` 실행 후 Supabase에 넣거나, 배포 후 **+ 등록**으로 추가하세요.

## 7. (선택) Vercel Services 방식

Vercel이 **Services** 프리셋을 지원하는 팀/프로젝트라면 `vercel.json` 대신 아래도 가능합니다.

```json
{
  "experimentalServices": {
    "web": {
      "entrypoint": "frontend",
      "framework": "vite",
      "routePrefix": "/"
    },
    "api": {
      "entrypoint": "api/index.py",
      "framework": "fastapi",
      "routePrefix": "/api"
    }
  }
}
```

Framework Preset을 **Services**로 바꿔야 합니다. 일반 Hobby 프로젝트는 위 **vercel.json + api/index.py** 방식을 권장합니다.
