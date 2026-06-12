/**
 * API 요청 큐 — Supabase 등 DB 연결 한도를 넘지 않도록 동시 요청 수를 제한합니다.
 */
export function createRequestQueue(concurrency = 2) {
  let active = 0
  const pending = []

  function drain() {
    while (active < concurrency && pending.length > 0) {
      active += 1
      const { run, resolve, reject } = pending.shift()
      Promise.resolve()
        .then(run)
        .then(resolve, reject)
        .finally(() => {
          active -= 1
          drain()
        })
    }
  }

  function enqueue(run) {
    return new Promise((resolve, reject) => {
      pending.push({ run, resolve, reject })
      drain()
    })
  }

  return { enqueue }
}

/** DB 조회 API용 — 한 번에 하나씩 순서대로 처리 */
export const dbRequestQueue = createRequestQueue(1)
