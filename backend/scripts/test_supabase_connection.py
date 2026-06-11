"""Supabase 연결 테스트 (비밀번호 출력 없음)."""
from urllib.parse import urlparse

import psycopg2

from app.config import settings

REGIONS = [
    "ap-northeast-2",
    "ap-northeast-1",
    "ap-southeast-1",
    "us-east-1",
    "us-west-1",
    "eu-west-1",
    "eu-central-1",
    "sa-east-1",
]
PREFIXES = ["aws-0", "aws-1"]


def main() -> None:
    parsed = urlparse(settings.database_url)
    if not parsed.hostname or "pooler" not in parsed.hostname:
        print("not_pooler_uri")
        return

    user = parsed.username or ""
    if not user.startswith("postgres."):
        ref = user.replace("postgres", "").strip(".") or "unknown"
        user = f"postgres.{ref}" if ref != "postgres" else user

    ref = user.split(".", 1)[1] if "." in user else ""
    password = parsed.password or ""

    print(f"project_ref: {ref or '(from uri)'}")
    print("testing pooler regions...")

    for prefix in PREFIXES:
        for region in REGIONS:
            host = f"{prefix}-{region}.pooler.supabase.com"
            try:
                conn = psycopg2.connect(
                    host=host,
                    port=5432,
                    user=user,
                    password=password,
                    dbname="postgres",
                    sslmode="require",
                    connect_timeout=8,
                )
                conn.close()
                print(f"OK: {host}")
                print(f"SUGGESTED_DATABASE_URL=postgresql://{user}:***@{host}:5432/postgres")
                return
            except psycopg2.OperationalError as exc:
                msg = str(exc).split("\n", 1)[0]
                if "tenant/user" in msg or "password authentication" in msg:
                    print(f"NEAR: {host} ({msg[:60]})")
                elif "ENOTFOUND" not in msg and "could not translate" not in msg:
                    print(f"FAIL: {host} ({msg[:60]})")

    # Direct connection fallback
    if ref:
        host = f"db.{ref}.supabase.co"
        try:
            conn = psycopg2.connect(
                host=host,
                port=5432,
                user="postgres",
                password=password,
                dbname="postgres",
                sslmode="require",
                connect_timeout=8,
            )
            conn.close()
            print(f"OK_DIRECT: {host}")
            return
        except psycopg2.OperationalError as exc:
            print(f"DIRECT_FAIL: {msg[:80] if (msg := str(exc).split(chr(10))[0]) else exc}")

    print("NO_MATCH")


if __name__ == "__main__":
    main()
