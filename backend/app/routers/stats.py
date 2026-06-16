from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Quote, QuoteLike, QuoteScrap
from app.schemas.schemas import QuoteOut
from app.services.quote_serializer import serialize_quotes

router = APIRouter(prefix="/api/stats", tags=["stats"])


class StatsOverviewOut(BaseModel):
    date: str
    quote_of_day: QuoteOut | None = None
    top_today: list[QuoteOut] = []
    top_week: list[QuoteOut] = []
    top_alltime: list[QuoteOut] = []


@router.get("/overview", response_model=StatsOverviewOut)
def get_stats_overview(db: Session = Depends(get_db)):
    now = datetime.now()
    today = now.date().isoformat()

    # 오늘 가장 많이 담긴 문장 (최근 24h scrap)
    cutoff_24h = now - timedelta(hours=24)
    today_subq = (
        db.query(QuoteScrap.quote_id, func.count(QuoteScrap.id).label("cnt"))
        .filter(QuoteScrap.created_at >= cutoff_24h)
        .group_by(QuoteScrap.quote_id)
        .subquery()
    )
    today_quotes = (
        db.query(Quote)
        .join(today_subq, Quote.id == today_subq.c.quote_id)
        .order_by(today_subq.c.cnt.desc())
        .limit(5)
        .all()
    )

    # 이번 주 인기 문장 (최근 7일 like)
    cutoff_7d = now - timedelta(days=7)
    week_subq = (
        db.query(QuoteLike.quote_id, func.count(QuoteLike.id).label("cnt"))
        .filter(QuoteLike.created_at >= cutoff_7d)
        .group_by(QuoteLike.quote_id)
        .subquery()
    )
    week_quotes = (
        db.query(Quote)
        .join(week_subq, Quote.id == week_subq.c.quote_id)
        .order_by(week_subq.c.cnt.desc())
        .limit(5)
        .all()
    )

    # 역대 인기 문장 (전체 like)
    alltime_subq = (
        db.query(QuoteLike.quote_id, func.count(QuoteLike.id).label("cnt"))
        .group_by(QuoteLike.quote_id)
        .subquery()
    )
    alltime_quotes = (
        db.query(Quote)
        .join(alltime_subq, Quote.id == alltime_subq.c.quote_id)
        .order_by(alltime_subq.c.cnt.desc())
        .limit(5)
        .all()
    )

    # 오늘의 문장: 이번 주 인기 > 역대 인기 > 전체 최신 중 날짜 기반 선택
    pool = week_quotes or alltime_quotes
    if not pool:
        pool = db.query(Quote).order_by(Quote.created_at.desc()).limit(20).all()
    qod = pool[now.timetuple().tm_yday % len(pool)] if pool else None

    # 한 번에 직렬화 (중복 제거)
    all_raw = list({
        q.id: q
        for q in today_quotes + week_quotes + alltime_quotes + ([qod] if qod else [])
    }.values())
    serialized = {out.id: out for out in serialize_quotes(db, all_raw)}

    return StatsOverviewOut(
        date=today,
        quote_of_day=serialized.get(qod.id) if qod else None,
        top_today=[serialized[q.id] for q in today_quotes if q.id in serialized],
        top_week=[serialized[q.id] for q in week_quotes if q.id in serialized],
        top_alltime=[serialized[q.id] for q in alltime_quotes if q.id in serialized],
    )
