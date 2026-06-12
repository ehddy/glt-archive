const EXACT_MESSAGES = {
  '이미 등록된 문장입니다.': '이 문장은 이미 같은 출처로 등록되어 있어요.',
  '출처는 필수입니다.': '출처를 함께 적어 주세요.',
  '도서를 선택하거나 출처를 직접 입력해 주세요.': '도서를 선택하거나 출처를 입력해 주세요.',
  '문장을 입력해 주세요.': '문장을 입력해 주세요.',
  '선택한 작품을 찾을 수 없습니다.': '선택한 도서를 찾지 못했어요.',
  '선택한 출처를 찾을 수 없습니다.': '선택한 출처를 찾지 못했어요.',
  '요청에 실패했습니다.': '등록하지 못했어요. 잠시 후 다시 시도해 주세요.',
  '응답 시간이 초과되었습니다.': '응답이 늦어졌어요. 다시 시도해 주세요.',
  'API를 찾을 수 없습니다.': '서버에 연결하지 못했어요. 잠시 후 다시 시도해 주세요.',
}

const PATTERN_MESSAGES = [
  { test: /이미 등록/, message: '이 문장은 이미 같은 출처로 등록되어 있어요.' },
  { test: /timeout|초과|timed out/i, message: '응답이 늦어졌어요. 다시 시도해 주세요.' },
  { test: /network|fetch|failed to fetch/i, message: '인터넷 연결을 확인한 뒤 다시 시도해 주세요.' },
  { test: /503|서비스|GEMINI|API key/i, message: '잠시 후 다시 시도해 주세요.' },
  { test: /404|찾을 수 없|찾지 못/, message: '요청한 내용을 찾지 못했어요.' },
]

export function friendlyRegisterError(raw) {
  const text = String(raw || '').trim()
  if (!text) {
    return '등록하지 못했어요. 다시 시도해 주세요.'
  }

  if (EXACT_MESSAGES[text]) {
    return EXACT_MESSAGES[text]
  }

  for (const { test, message } of PATTERN_MESSAGES) {
    if (test.test(text)) {
      return message
    }
  }

  if (text.length > 80 || text.includes('Error') || text.includes('Exception')) {
    return '등록하지 못했어요. 입력 내용을 확인한 뒤 다시 시도해 주세요.'
  }

  return text
}
