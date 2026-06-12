import json
import re

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.models.models import Novel
from app.schemas.schemas import BookRecommendation, ChatMessage, ChatResponse

SYSTEM_PROMPT = """당신은 한국 문학 추천 어시스턴트입니다.
사용자가 말하는 책·작가·문장·분위기·감정과 비슷한 느낌의 작품과 작가를 추천합니다.

규칙:
1. 반드시 한국어로 답합니다.
2. recommendations에는 2~4개의 작품을 넣습니다.
3. 각 추천마다 reason에 '왜 이 작품/작가가 비슷한 느낌인지' 구체적으로 설명합니다.
4. 아래 라이브러리 목록에 있는 작품이면 in_library=true, novel_id를 넣습니다.
5. 라이브러리에 없는 작품도 추천할 수 있으며 그때 in_library=false, novel_id=null 입니다.
6. reply에는 친근한 짧은 인사와 추천 요약을 담습니다.

반드시 아래 JSON 형식만 출력하세요. 다른 텍스트는 금지합니다.
{
  "reply": "전체 응답 메시지",
  "recommendations": [
    {
      "title": "작품명",
      "author": "작가명",
      "reason": "추천 이유",
      "in_library": true,
      "novel_id": 1
    }
  ]
}"""


def _build_catalog(db: Session) -> list[dict]:
    novels = (
        db.query(Novel)
        .options(
            joinedload(Novel.author),
            joinedload(Novel.quotes),
        )
        .order_by(Novel.title)
        .all()
    )
    catalog = []
    for novel in novels:
        quotes = [q.text for q in novel.quotes[:2]]
        catalog.append({
            "novel_id": novel.id,
            "title": novel.title,
            "author": novel.author.name if novel.author else "",
            "sample_quotes": quotes,
        })
    return catalog


def _catalog_text(catalog: list[dict]) -> str:
    if not catalog:
        return "(라이브러리에 등록된 작품 없음)"
    lines = []
    for item in catalog:
        quotes = " / ".join(item["sample_quotes"]) if item["sample_quotes"] else ""
        lines.append(
            f"- novel_id={item['novel_id']}, "
            f"《{item['title']}》 {item['author']}"
            + (f" | 문장: {quotes}" if quotes else "")
        )
    return "\n".join(lines)


def _build_user_prompt(message: str, history: list[ChatMessage], catalog: list[dict]) -> str:
    history_text = ""
    for item in history[-6:]:
        role = "사용자" if item.role == "user" else "어시스턴트"
        history_text += f"{role}: {item.content}\n"

    return f"""## 서비스 라이브러리
{_catalog_text(catalog)}

## 이전 대화
{history_text or "(없음)"}

## 사용자 메시지
{message}
"""


def _parse_json_response(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)


def _gemini_error_detail(exc: Exception) -> tuple[int, str]:
    msg = str(exc)
    if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower():
        return (
            429,
            "Gemini API 무료 사용 한도에 도달했습니다. 잠시 후 다시 시도하거나 "
            "Google AI Studio에서 사용량·결제 설정을 확인해 주세요.",
        )
    if (
        "401" in msg
        or "403" in msg
        or "400" in msg
        or "API key" in msg
        or "API_KEY_INVALID" in msg
        or "INVALID_ARGUMENT" in msg
        or "PERMISSION_DENIED" in msg
    ):
        return (
            401,
            "Gemini API 키가 올바르지 않습니다. "
            "[Google AI Studio](https://aistudio.google.com/apikey)에서 발급한 키를 "
            "backend/.env 의 GEMINI_API_KEY에 넣었는지 확인해 주세요.",
        )
    return 502, f"Gemini API 호출에 실패했습니다. 잠시 후 다시 시도해 주세요."


def _normalize_recommendations(
    raw: list,
    catalog: list[dict],
) -> list[BookRecommendation]:
    title_map = {
        (item["title"].strip(), item["author"].strip()): item["novel_id"]
        for item in catalog
    }
    results = []
    for item in raw[:4]:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        author = str(item.get("author", "")).strip()
        reason = str(item.get("reason", "")).strip()
        if not title or not author or not reason:
            continue

        novel_id = item.get("novel_id")
        in_library = bool(item.get("in_library", False))
        matched_id = title_map.get((title, author))
        if matched_id:
            in_library = True
            novel_id = matched_id
        elif novel_id not in {c["novel_id"] for c in catalog}:
            novel_id = None
            if in_library:
                in_library = False

        results.append(BookRecommendation(
            title=title,
            author=author,
            reason=reason,
            in_library=in_library,
            novel_id=novel_id if in_library else None,
        ))
    return results


def recommend_books(
    db: Session,
    message: str,
    history: list[ChatMessage] | None = None,
) -> ChatResponse:
    if not settings.gemini_api_key:
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY가 설정되지 않았습니다. backend/.env 파일을 확인해 주세요.",
        )

    history = history or []
    catalog = _build_catalog(db)
    prompt = _build_user_prompt(message, history, catalog)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7,
                max_output_tokens=2048,
                response_mime_type="application/json",
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
            detail="AI 응답을 해석하지 못했습니다. 다시 시도해 주세요.",
        ) from exc

    reply = str(data.get("reply", "")).strip()
    if not reply:
        reply = "비슷한 느낌의 작품을 추천해 드릴게요."

    recommendations = _normalize_recommendations(
        data.get("recommendations", []),
        catalog,
    )

    return ChatResponse(reply=reply, recommendations=recommendations)
