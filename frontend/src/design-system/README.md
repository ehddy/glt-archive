# GLT Design System

서비스 **괴테는 모든 것을 말했다** 의 UI 토큰과 컴포넌트 규칙입니다.

## 컨셉

- **Library Graph** — 작품(책)이 중심 노드, 구절이 가지처럼 뻗어 나감
- **Warm ink** — 따뜻한 종이 배경 + 먹색 텍스트 + 포레스트 그린 액센트

## 토큰 (`tokens.css`)

| 카테고리 | prefix | 예시 |
|---------|--------|------|
| 배경/표면 | `--glt-bg`, `--glt-surface` | |
| 텍스트 | `--glt-ink-*` | |
| 액센트 | `--glt-accent-*` | |
| 그래프 선 | `--glt-line-*` | |
| 책 색상 | `--glt-book-0` ~ `7` | 작품별 spine 색 |
| 간격 | `--glt-space-*` | 4px 단위 |
| 반경/그림자 | `--glt-radius-*`, `--glt-shadow-*` | |

## 컴포넌트 클래스 (`components.css`)

- `.glt-container` — 레이아웃 컨테이너
- `.glt-title` / `.glt-subtitle` / `.glt-eyebrow` — 타이포
- `.glt-card` / `.glt-card-raised` — 카드
- `.glt-btn-primary` / `.glt-btn-ghost` — 버튼
- `.glt-field` — 폼 필드
- `.glt-search` — 검색바
- `.glt-quote` — 구절 본문 (serif)

## Vue 컴포넌트

- `BookNode` — 작품(책) 노드
- `QuoteBranch` — 구절 가지 카드
- `BookHub` — 책 + 구절 그래프 단위
