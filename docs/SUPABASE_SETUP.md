# Supabase DB 연동 가이드

이 프로젝트는 **Supabase(PostgreSQL)** 또는 로컬 **SQLite**를 `.env`의 `DATABASE_URL` 한 줄로 전환할 수 있습니다.

---

## 1. Supabase 가입

1. [https://supabase.com](https://supabase.com) 접속
2. **Start your project** → GitHub / Google / 이메일로 가입
3. 이메일 인증 완료 (이메일 가입 시)

---

## 2. 새 프로젝트 만들기 (가입 폼)

대시보드에서 **New project** 클릭 후 아래 항목을 입력합니다.

| 항목 | 설명 | 권장 예시 |
|------|------|-----------|
| **Organization** | 팀/개인 조직 | `personal` 또는 본인 이름 |
| **Project name** | 프로젝트 이름 | `glt-archive` |
| **Database password** | DB 접속 비밀번호 | **강한 비밀번호** (반드시 메모!) |
| **Region** | 서버 위치 | `Northeast Asia (Seoul)` |

> **Database password**는 나중에 다시 볼 수 없습니다. 비밀번호 관리자에 저장해 두세요.

프로젝트 생성에 1~2분 걸립니다. **Project is ready**가 뜰 때까지 기다립니다.

---

## 3. 연결 문자열(Connection URI) 복사

1. 왼쪽 메뉴 **Project Settings** (톱니바퀴)
2. **Database** 탭
3. **Connection string** 섹션
4. **Type**: `URI` 선택
5. **Method**: `Session pooler` 또는 `Direct connection` 선택
   - 이 프로젝트(FastAPI + SQLAlchemy)는 **Session pooler (포트 5432)** 권장
6. `[YOUR-PASSWORD]`를 2단계에서 만든 **Database password**로 교체
7. 전체 URI 복사

예시 형태:

```text
postgresql://postgres.xxxxxxxxxxxx:YOUR_PASSWORD@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres
```

### 비밀번호에 특수문자가 있을 때

`@`, `#`, `%` 등이 있으면 URL 인코딩이 필요합니다.

| 문자 | 인코딩 |
|------|--------|
| `@` | `%40` |
| `#` | `%23` |
| `%` | `%25` |
| `:` | `%3A` |

또는 Supabase 대시보드에서 **Reset database password**로 URL-safe 비밀번호를 새로 설정할 수 있습니다.

---

## 4. 프로젝트 `.env` 설정

`backend/.env` 파일을 열고 `DATABASE_URL`을 Supabase URI로 바꿉니다.

```env
# Supabase (PostgreSQL)
DATABASE_URL=postgresql://postgres.xxxxx:YOUR_PASSWORD@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres

# 아래 API 키들은 기존과 동일
GEMINI_API_KEY=...
ALADIN_TTB_KEY=...
```

로컬 SQLite로 되돌리려면:

```env
DATABASE_URL=sqlite:///./quotes.db
```

---

## 5. 백엔드 재시작

```powershell
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

첫 실행 시 테이블이 자동 생성되고, 비어 있으면 **시드 구절 12건**이 들어갑니다.

연결 확인:

```text
GET http://127.0.0.1:8000/api/health
```

응답 예시:

```json
{
  "status": "ok",
  "app": "괴테는 모든 것을 말했다",
  "database": "supabase"
}
```

---

## 6. Supabase 대시보드에서 데이터 확인

1. 왼쪽 **Table Editor**
2. `authors`, `novels`, `quotes`, `quote_versions` 테이블 확인
3. 구절 등록·검색 후 행이 추가되는지 확인

---

## 문제 해결

| 증상 | 해결 |
|------|------|
| `password authentication failed` | URI의 비밀번호 확인, 특수문자 URL 인코딩 |
| `could not connect to server` | Region/URI 오타, 방화벽·VPN 확인 |
| `SSL connection required` | URI 끝에 `?sslmode=require` 추가 (코드에서도 자동 처리) |
| 테이블이 없음 | 백엔드 재시작 후 `/api/health` 확인, 로그에 `[seed]` 메시지 확인 |
| 기존 SQLite 데이터 이전 | Supabase는 새 DB이므로 구절을 다시 등록하거나 별도 마이그레이션 필요 |

---

## 참고 링크

- [Supabase Dashboard](https://supabase.com/dashboard)
- [Supabase Database 연결 문서](https://supabase.com/docs/guides/database/connecting-to-postgres)
