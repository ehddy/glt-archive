from fastapi import APIRouter

from app.schemas.schemas import AiSearchRequest, AiSearchResponse
from app.services.ai_search_service import search_quotes_by_ai

router = APIRouter(prefix="/api/ai-search", tags=["ai-search"])


@router.post("", response_model=AiSearchResponse)
def ai_search(payload: AiSearchRequest):
    return search_quotes_by_ai(payload.q)
