export const THEMES = [
  {
    id: 'hanji',
    name: '따뜻한 한지',
    hint: '베이지·테라코타, 지금 쓰는 톤',
    metaColor: '#faf6f0',
  },
  {
    id: 'night',
    name: '밤의 서재',
    hint: '짙은 남색, 금빛 포인트',
    metaColor: '#1c2433',
  },
  {
    id: 'mist',
    name: '이른 아침',
    hint: '차분한 회청색, 세이지 포인트',
    metaColor: '#eef2f4',
  },
  {
    id: 'rose',
    name: '장미빛 오후',
    hint: '블러시 핑크, 와인 포인트',
    metaColor: '#faf0ee',
  },
  {
    id: 'forest',
    name: '숲속 서재',
    hint: '딥 그린·페이퍼 크림',
    metaColor: '#edf0e8',
  },
]

const STORAGE_KEY = 'glt-theme-trial'

const DEFAULT_THEME_ID = 'mist'

export function getSavedThemeId() {
  const saved = localStorage.getItem(STORAGE_KEY)
  return THEMES.some((theme) => theme.id === saved) ? saved : DEFAULT_THEME_ID
}

export function applyTheme(themeId) {
  const theme = THEMES.find((item) => item.id === themeId) || THEMES[0]
  document.documentElement.setAttribute('data-theme', theme.id)
  localStorage.setItem(STORAGE_KEY, theme.id)

  const meta = document.querySelector('meta[name="theme-color"]')
  if (meta) meta.setAttribute('content', theme.metaColor)

  return theme
}

export function getThemeIndex(themeId) {
  return THEMES.findIndex((theme) => theme.id === themeId)
}

export function getNextThemeId(themeId) {
  const index = getThemeIndex(themeId)
  const next = index < 0 ? 0 : (index + 1) % THEMES.length
  return THEMES[next].id
}

export function getPrevThemeId(themeId) {
  const index = getThemeIndex(themeId)
  const prev = index < 0 ? 0 : (index - 1 + THEMES.length) % THEMES.length
  return THEMES[prev].id
}
