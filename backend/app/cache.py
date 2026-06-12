import threading
import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


class TtlCache:
    """프로세스 메모리 TTL 캐시 — DB 읽기 API용."""

    def __init__(self, default_ttl: float = 60.0):
        self._default_ttl = default_ttl
        self._store: dict[str, tuple[float, object]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> object | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if time.monotonic() >= expires_at:
                del self._store[key]
                return None
            return value

    def set(self, key: str, value: object, ttl: float | None = None) -> None:
        ttl = self._default_ttl if ttl is None else ttl
        with self._lock:
            self._store[key] = (time.monotonic() + ttl, value)

    def invalidate_prefix(self, prefix: str) -> None:
        with self._lock:
            for key in list(self._store):
                if key.startswith(prefix):
                    del self._store[key]

    def clear(self) -> None:
        with self._lock:
            self._store.clear()

    def get_or_set(
        self,
        key: str,
        factory: Callable[[], T],
        *,
        ttl: float | None = None,
        enabled: bool = True,
    ) -> T:
        if not enabled:
            return factory()

        cached = self.get(key)
        if cached is not None:
            return cached  # type: ignore[return-value]

        value = factory()
        self.set(key, value, ttl=ttl)
        return value


read_cache = TtlCache()


def invalidate_read_cache() -> None:
    """문장·도서 등록/수정 후 읽기 캐시를 비웁니다."""
    read_cache.clear()
