import json
import re

from fastapi import HTTPException

from app.config import settings
from app.schemas.schemas import AiSearchArticle, AiSearchResponse
from app.services.chat_service import _gemini_error_detail, _parse_json_response

SYSTEM_PROMPT = """당신은 한국어 명문장·인용구 출처 조사 어시스턴트입니다.
Google 검색을 활용해 사용자 키워드와 관련된 실제 명문장·유명 인용구와 그 출처를 찾습니다.

규칙:
1. 반드시 한국어로 작성합니다.
2. 검색 결과에 근거한 문장만 포함합니다. 출처가 불확실하면 제외합니다.
3. 문학 작품, 수필, 연설, 인터뷰 등 다양한 출처를 포함할 수 있습니다.
4. articles는 3~6개를 반환합니다.
5. 각 article의 quote는 원문에 가깝게, 1~3문장 이내로 작성합니다.
6. source_title은 책 제목·작품명·강연명 등 구체적인 출처명이어야 합니다.
   "밤에 관한 명언"처럼 주제나 분류 설명은 넣지 마세요. author는 작가·화자 이름입니다.
7. context는 이 문장이 왜 유명한지, 어떤 맥락인지 1~2문장으로 설명합니다.
8. source_url은 가능하면 실제 참고 URL을 넣고, 없으면 빈 문자열 "".

반드시 아래 JSON만 출력하세요.
{
  "summary": "검색 결과 한 줄 요약",
  "articles": [
    {
      "quote": "명문장 원문",
      "source_title": "출처 작품/매체명",
      "author": "작가 또는 화자",
      "context": "맥락 설명",
      "source_url": "https://..."
    }
  ]
}"""


def _build_prompt(keyword: str) -> str:
    return f"""키워드: {keyword}

위 키워드와 관련된 한국어 명문장·유명 인용구를 Google 검색으로 조사하고,
출처(작품명, 작가)와 함께 JSON으로 정리해 주세요."""


def _normalize_articles(raw: list) -> list[AiSearchArticle]:
    articles = []
    for item in raw[:6]:
        if not isinstance(item, dict):
            continue
        quote = str(item.get("quote", "")).strip()
        source_title = str(item.get("source_title", "")).strip()
        author = str(item.get("author", "")).strip()
        context = str(item.get("context", "")).strip()
        source_url = str(item.get("source_url", "")).strip()
        if not quote or not source_title:
            continue
        if source_url and not re.match(r"^https?://", source_url):
            source_url = ""
        articles.append(
            AiSearchArticle(
                quote=quote,
                source_title=source_title,
                author=author,
                context=context,
                source_url=source_url or None,
            )
        )
    return articles


def search_quotes_by_ai(keyword: str) -> AiSearchResponse:
    q = keyword.strip()
    if not q:
        raise HTTPException(status_code=400, detail="키워드를 입력해 주세요.")

    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY가 설정되지 않았습니다. backend/.env 파일을 확인해 주세요.",
        )

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=_build_prompt(q),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.35,
                max_output_tokens=4096,
            ),
        )
        raw_text = response.text or ""
    except ImportError as exc:
        raise HTTPException(
            status_code=500,
            detail="google-genai 패키지가 설치되지 않았습니다.",
        ) from exc
    except Exception as exc:
        status, detail = _gemini_error_detail(exc)
        raise HTTPException(status_code=status, detail=detail) from exc

    try:
        data = _parse_json_response(raw_text)
    except (json.JSONDecodeError, TypeError) as exc:
        raise HTTPException(
            status_code=502,
            detail="AI 검색 결과를 해석하지 못했습니다. 다시 시도해 주세요.",
        ) from exc

    articles = _normalize_articles(data.get("articles", []))
    if not articles:
        raise HTTPException(
            status_code=404,
            detail="관련 명문장을 찾지 못했습니다. 다른 키워드로 시도해 보세요.",
        )

    summary = str(data.get("summary", "")).strip()
    if not summary:
        summary = f"「{q}」와 관련된 명문장 {len(articles)}건을 찾았습니다."

    return AiSearchResponse(query=q, summary=summary, articles=articles)
