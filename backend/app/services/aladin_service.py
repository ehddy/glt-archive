import json
import re
from typing import Any
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException

from app.config import settings

SEARCH_URL = "https://www.aladin.co.kr/ttb/api/ItemSearch.aspx"
LOOKUP_URL = "https://www.aladin.co.kr/ttb/api/ItemLookUp.aspx"
API_VERSION = "20131101"
LOOKUP_OPT_RESULT = "fulldescription,categoryIdList,authors,toc,ratingInfo"


def _require_key() -> str:
    key = settings.aladin_ttb_key.strip()
    if not key:
        raise HTTPException(
            status_code=503,
            detail="ALADIN_TTB_KEY가 설정되지 않았습니다. backend/.env 파일을 확인해 주세요.",
        )
    return key


def _parse_js_response(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if not cleaned:
        raise HTTPException(status_code=502, detail="알라딘 API 응답이 비어 있습니다.")

    if cleaned.startswith("{"):
        data = json.loads(cleaned)
    else:
        match = re.search(r"\((\{.*\})\)\s*;?\s*$", cleaned, re.DOTALL)
        if not match:
            raise HTTPException(status_code=502, detail="알라딘 API 응답 형식을 해석하지 못했습니다.")
        data = json.loads(match.group(1))

    if data.get("errorCode"):
        code = data.get("errorCode")
        message = data.get("errorMessage", "알라딘 API 오류")
        if code == 4:
            raise HTTPException(status_code=401, detail="알라딘 API 키가 올바르지 않거나 승인되지 않았습니다.")
        raise HTTPException(status_code=502, detail=f"알라딘 API 오류: {message}")

    return data


async def _fetch_aladin(url: str, params: dict[str, Any]) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return _parse_js_response(response.text)
    except HTTPException:
        raise
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="알라딘 API에 연결하지 못했습니다. 잠시 후 다시 시도해 주세요.",
        ) from exc
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=502,
            detail="알라딘 API 응답을 해석하지 못했습니다.",
        ) from exc


def _to_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _pick(item: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in item and item[key] not in (None, ""):
            return item[key]
    return None


def _as_dict_list(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        return [value]
    return []


def _extract_categories(category_data: Any) -> list[dict[str, Any]]:
    if isinstance(category_data, list):
        return _as_dict_list(category_data)
    if isinstance(category_data, dict):
        if "categoryName" in category_data:
            return [category_data]
        return _as_dict_list(category_data.get("categoryInfo"))
    return []


def parse_author_name(raw: str | None) -> str:
    if not raw:
        return "미상"
    name = str(raw).split(",")[0].strip()
    if "(" in name:
        name = name.split("(")[0].strip()
    return name[:100] or "미상"


def normalize_search_item(item: dict[str, Any]) -> dict[str, Any]:
    item_id = _to_int(_pick(item, "itemId", "itemid"))
    if not item_id:
        raise ValueError("itemId missing")

    return {
        "item_id": item_id,
        "title": str(_pick(item, "title") or "").strip(),
        "author": str(_pick(item, "author") or "").strip(),
        "publisher": str(_pick(item, "publisher") or "").strip(),
        "pub_date": _pick(item, "pubDate", "pubdate"),
        "description": _pick(item, "description"),
        "isbn": _pick(item, "isbn"),
        "isbn13": _pick(item, "isbn13"),
        "price_sales": _to_int(_pick(item, "priceSales", "pricesales")),
        "price_standard": _to_int(_pick(item, "priceStandard", "pricestandard")),
        "cover_url": _pick(item, "cover"),
        "link": _pick(item, "link"),
        "category_name": _pick(item, "categoryName", "categoryname"),
    }


def normalize_detail_item(item: dict[str, Any]) -> dict[str, Any]:
    base = normalize_search_item(item)
    sub_info = item.get("subInfo") or {}
    category_data = sub_info.get("categoryIdList") or item.get("categoryIdList")
    categories = _extract_categories(category_data)

    category_names = [
        str(cat.get("categoryName", "")).strip()
        for cat in categories
        if cat.get("categoryName")
    ]

    rating_raw = sub_info.get("ratingInfo") or item.get("ratingInfo") or {}
    rating = rating_raw if isinstance(rating_raw, dict) else {}

    authors_raw = sub_info.get("authors") or item.get("authors") or []
    if isinstance(authors_raw, dict):
        authors_raw = authors_raw.get("author") or authors_raw
    authors = _as_dict_list(authors_raw)

    detail_payload = {
        "sub_title": sub_info.get("subTitle"),
        "original_title": sub_info.get("originalTitle"),
        "item_page": _to_int(sub_info.get("itemPage")),
        "full_description": item.get("fullDescription") or sub_info.get("fullDescription"),
        "full_description2": item.get("fullDescription2") or sub_info.get("fullDescription2"),
        "toc": sub_info.get("toc") or item.get("toc"),
        "category_names": category_names,
        "rating_score": rating.get("ratingScore"),
        "rating_count": _to_int(rating.get("ratingCount")),
        "authors": [
            {
                "author_id": _to_int(author.get("authorId")),
                "author_name": author.get("authorName"),
                "author_type": author.get("authorTypeDesc") or author.get("authorType"),
            }
            for author in authors
            if isinstance(author, dict)
        ],
    }

    base["category_name"] = base.get("category_name") or (category_names[-1] if category_names else None)
    base["detail"] = detail_payload
    return base


async def search_books(
    query: str,
    max_results: int = 10,
    query_type: str = "Keyword",
) -> list[dict[str, Any]]:
    params = {
        "ttbkey": _require_key(),
        "Query": query.strip(),
        "QueryType": query_type,
        "MaxResults": max(1, min(max_results, 50)),
        "start": 1,
        "SearchTarget": "Book",
        "output": "js",
        "Version": API_VERSION,
        "Cover": "Mid",
    }
    data = await _fetch_aladin(SEARCH_URL, params)
    items = data.get("item") or []
    if isinstance(items, dict):
        items = [items]

    results = []
    for item in items:
        try:
            results.append(normalize_search_item(item))
        except ValueError:
            continue
    return results


async def lookup_book(item_id: int) -> dict[str, Any]:
    params = {
        "ttbkey": _require_key(),
        "itemIdType": "ItemId",
        "ItemId": item_id,
        "output": "js",
        "Version": API_VERSION,
        "Cover": "MidBig",
        "OptResult": LOOKUP_OPT_RESULT,
    }
    data = await _fetch_aladin(LOOKUP_URL, params)
    items = data.get("item") or []
    if isinstance(items, dict):
        items = [items]
    if not items:
        raise HTTPException(status_code=404, detail="알라딘에서 도서를 찾을 수 없습니다.")
    return normalize_detail_item(items[0])
