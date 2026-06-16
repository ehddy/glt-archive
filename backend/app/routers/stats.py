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

RANK_LIMIT = 3


class DayCount(BaseModel):
    label: str   # "6/10"
    scraps: int
    likes: int


class TodayStats(BaseModel):
    scraps_today: int
    quotes_today: int
    total_quotes: int
    total_scraps: int


class StatsOverviewOut(BaseModel):
    date: str
    today_stats: TodayStats
    weekly_activity: list[DayCount] = []
    quote_of_day: QuoteOut | None = None
    top_today: list[QuoteOut] = []
    top_week: list[QuoteOut] = []
    top_alltime: list[QuoteOut] = []


@router.get("/overview", response_model=StatsOverviewOut)
def get_stats_overview(db: Session = Depends(get_db)):
    now = datetime.now()
    today = now.date().isoformat()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # ── 오늘 통계 ──────────────────────────────
    scraps_today = (
        db.query(func.count(QuoteScrap.id))
        .filter(QuoteScrap.created_at >= today_start)
        .scalar() or 0
    )
    quotes_today = (
        db.query(func.count(Quote.id))
        .filter(Quote.created_at >= today_start)
        .scalar() or 0
    )
    total_quotes = db.query(func.count(Quote.id)).scalar() or 0
    total_scraps = db.query(func.count(QuoteScrap.id)).scalar() or 0

    # ── 최근 7일 일별 활동 ─────────────────────
    cutoff_7d = now - timedelta(days=6)
    cutoff_7d_start = cutoff_7d.replace(hour=0, minute=0, second=0, microsecond=0)

    scrap_rows = (
        db.query(
            func.date(QuoteScrap.created_at).label("day"),
            func.count(QuoteScrap.id).label("cnt"),
        )
        .filter(QuoteScrap.created_at >= cutoff_7d_start)
        .group_by(func.date(QuoteScrap.created_at))
        .all()
    )
    like_rows = (
        db.query(
            func.date(QuoteLike.created_at).label("day"),
            func.count(QuoteLike.id).label("cnt"),
        )
        .filter(QuoteLike.created_at >= cutoff_7d_start)
        .group_by(func.date(QuoteLike.created_at))
        .all()
    )
    scrap_by_day = {str(r.day): int(r.cnt) for r in scrap_rows}
    like_by_day = {str(r.day): int(r.cnt) for r in like_rows}

    weekly_activity: list[DayCount] = []
    for i in range(7):
        d = (cutoff_7d_start + timedelta(days=i)).date()
        key = d.isoformat()
        weekly_activity.append(DayCount(
            label=f"{d.month}/{d.day}",
            scraps=scrap_by_day.get(key, 0),
            likes=like_by_day.get(key, 0),
        ))

    # ── 랭킹 쿼리 ──────────────────────────────
    cutoff_24h = now - timedelta(hours=24)

    # 오늘 가장 많이 담긴 (24h scrap → fallback 전체)
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
        .limit(RANK_LIMIT)
        .all()
    )
    if not today_quotes:
        fb_subq = (
            db.query(QuoteScrap.quote_id, func.count(QuoteScrap.id).label("cnt"))
            .group_by(QuoteScrap.quote_id)
            .subquery()
        )
        today_quotes = (
            db.query(Quote)
            .join(fb_subq, Quote.id == fb_subq.c.quote_id)
            .order_by(fb_subq.c.cnt.desc())
            .limit(RANK_LIMIT)
            .all()
        )

    # 이번 주 인기 (7일 like → fallback 전체)
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
        .limit(RANK_LIMIT)
        .all()
    )

    # 역대 인기 (전체 like)
    alltime_subq = (
        db.query(QuoteLike.quote_id, func.count(QuoteLike.id).label("cnt"))
        .group_by(QuoteLike.quote_id)
        .subquery()
    )
    alltime_quotes = (
        db.query(Quote)
        .join(alltime_subq, Quote.id == alltime_subq.c.quote_id)
        .order_by(alltime_subq.c.cnt.desc())
        .limit(RANK_LIMIT)
        .all()
    )
    if not week_quotes:
        week_quotes = alltime_quotes

    # 오늘의 문장
    pool = week_quotes or alltime_quotes
    if not pool:
        pool = db.query(Quote).order_by(Quote.created_at.desc()).limit(20).all()
    qod = pool[now.timetuple().tm_yday % len(pool)] if pool else None

    # 직렬화 (중복 제거)
    all_raw = list({
        q.id: q
        for q in today_quotes + week_quotes + alltime_quotes + ([qod] if qod else [])
    }.values())
    serialized = {out.id: out for out in serialize_quotes(db, all_raw)}

    return StatsOverviewOut(
        date=today,
        today_stats=TodayStats(
            scraps_today=scraps_today,
            quotes_today=quotes_today,
            total_quotes=total_quotes,
            total_scraps=total_scraps,
        ),
        weekly_activity=weekly_activity,
        quote_of_day=serialized.get(qod.id) if qod else None,
        top_today=[serialized[q.id] for q in today_quotes if q.id in serialized],
        top_week=[serialized[q.id] for q in week_quotes if q.id in serialized],
        top_alltime=[serialized[q.id] for q in alltime_quotes if q.id in serialized],
    )
