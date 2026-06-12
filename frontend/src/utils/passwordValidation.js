const LETTER_RE = /[A-Za-z]/
const SPECIAL_RE = /[^A-Za-z0-9]/

export function getPasswordValidationError(password) {
  if (!password || password.length < 8) {
    return '비밀번호는 8자 이상이어야 해요.'
  }
  if (!LETTER_RE.test(password)) {
    return '비밀번호에 영문자를 포함해 주세요.'
  }
  if (!SPECIAL_RE.test(password)) {
    return '비밀번호에 특수문자를 포함해 주세요.'
  }
  return ''
}
