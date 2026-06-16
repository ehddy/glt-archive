from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.auth.deps import get_current_user_optional
from app.database import get_db
from app.models.models import Novel, Quote, QuoteLike, QuoteScrap, User
from app.schemas.schemas import AuthorOut, QuoteOut
from app.services.quote_serializer import serialize_quotes

router = APIRouter(prefix="/api/stats", tags=["stats"])

RANK_LIMIT = 3
BOOK_LIMIT = 10


class DayCount(BaseModel):
    label: str
    scraps: int
    likes: int


class TodayStats(BaseModel):
    scraps_today: int
    quotes_today: int
    total_quotes: int
    total_scraps: int


class PopularBookOut(BaseModel):
    id: int
    title: str
    cover_url: str | None = None
    author: AuthorOut | None = None
    quote_count: int = 0

    model_config = {"from_attributes": True}


class StatsOverviewOut(BaseModel):
    date: str
    is_personal: bool = False
    today_stats: TodayStats
    weekly_activity: list[DayCount] = []
    top_books: list[PopularBookOut] = []
    quote_of_day: QuoteOut | None = None
    top_today: list[QuoteOut] = []
    top_week: list[QuoteOut] = []
    top_alltime: list[QuoteOut] = []


@router.get("/overview", response_model=StatsOverviewOut)
def get_stats_overview(
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    now = datetime.now()
    today = now.date().isoformat()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    cutoff_7d = now - timedelta(days=6)
    cutoff_7d_start = cutoff_7d.replace(hour=0, minute=0, second=0, microsecond=0)
    uid = current_user.id if current_user else None

    # ── 오늘 통계 ──────────────────────────────────────────────
    if uid:
        scraps_today = (
            db.query(func.count(QuoteScrap.id))
            .filter(QuoteScrap.user_id == uid, QuoteScrap.created_at >= today_start)
            .scalar() or 0
        )
        quotes_today = (
            db.query(func.count(Quote.id))
            .filter(Quote.registered_by_id == uid, Quote.created_at >= today_start)
            .scalar() or 0
        )
    else:
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
    total_scraps = (
        db.query(func.count(QuoteScrap.id))
        .filter(QuoteScrap.user_id == uid)
        .scalar() or 0
    ) if uid else db.query(func.count(QuoteScrap.id)).scalar() or 0

    # ── 7일 일별 활동 (개인 or 전체) ───────────────────────────
    def _week_rows(model, uid_col):
        q = db.query(
            func.date(model.created_at).label("day"),
            func.count(model.id).label("cnt"),
        ).filter(model.created_at >= cutoff_7d_start)
        if uid:
            q = q.filter(uid_col == uid)
        return q.group_by(func.date(model.created_at)).all()

    scrap_rows = _week_rows(QuoteScrap, QuoteScrap.user_id)
    like_rows = _week_rows(QuoteLike, QuoteLike.user_id)
    scrap_by_day = {str(r.day): int(r.cnt) for r in scrap_rows}
    like_by_day = {str(r.day): int(r.cnt) for r in like_rows}

    weekly_activity: list[DayCount] = []
    for i in range(7):
        d = (cutoff_7d_start + timedelta(days=i)).date()
        weekly_activity.append(DayCount(
            label=f"{d.month}/{d.day}",
            scraps=scrap_by_day.get(d.isoformat(), 0),
            likes=like_by_day.get(d.isoformat(), 0),
        ))

    # ── 인기 책 (문장 많이 나온 책) ────────────────────────────
    book_rows = (
        db.query(Quote.novel_id, func.count(Quote.id).label("cnt"))
        .filter(Quote.novel_id.isnot(None))
        .group_by(Quote.novel_id)
        .order_by(func.count(Quote.id).desc())
        .limit(BOOK_LIMIT)
        .all()
    )
    novel_id_order = [r[0] for r in book_rows]
    cnt_map = {r[0]: r[1] for r in book_rows}
    novels_list = (
        db.query(Novel)
        .options(joinedload(Novel.author))
        .filter(Novel.id.in_(novel_id_order))
        .all()
    ) if novel_id_order else []
    novels_by_id = {n.id: n for n in novels_list}
    top_books = [
        PopularBookOut(
            id=nid,
            title=novels_by_id[nid].title,
            cover_url=novels_by_id[nid].cover_url,
            author=AuthorOut.model_validate(novels_by_id[nid].author) if novels_by_id[nid].author else None,
            quote_count=cnt_map[nid],
        )
        for nid in novel_id_order if nid in novels_by_id
    ]

    # ── 랭킹 ───────────────────────────────────────────────────
    cutoff_24h = now - timedelta(hours=24)

    today_subq = (
        db.query(QuoteScrap.quote_id, func.count(QuoteScrap.id).label("cnt"))
        .filter(QuoteScrap.created_at >= cutoff_24h)
        .group_by(QuoteScrap.quote_id).subquery()
    )
    today_quotes = (
        db.query(Quote).join(today_subq, Quote.id == today_subq.c.quote_id)
        .order_by(today_subq.c.cnt.desc()).limit(RANK_LIMIT).all()
    )
    if not today_quotes:
        fb = db.query(QuoteScrap.quote_id, func.count(QuoteScrap.id).label("cnt")).group_by(QuoteScrap.quote_id).subquery()
        today_quotes = db.query(Quote).join(fb, Quote.id == fb.c.quote_id).order_by(fb.c.cnt.desc()).limit(RANK_LIMIT).all()

    week_subq = (
        db.query(QuoteLike.quote_id, func.count(QuoteLike.id).label("cnt"))
        .filter(QuoteLike.created_at >= cutoff_7d)
        .group_by(QuoteLike.quote_id).subquery()
    )
    week_quotes = (
        db.query(Quote).join(week_subq, Quote.id == week_subq.c.quote_id)
        .order_by(week_subq.c.cnt.desc()).limit(RANK_LIMIT).all()
    )
    alltime_subq = (
        db.query(QuoteLike.quote_id, func.count(QuoteLike.id).label("cnt"))
        .group_by(QuoteLike.quote_id).subquery()
    )
    alltime_quotes = (
        db.query(Quote).join(alltime_subq, Quote.id == alltime_subq.c.quote_id)
        .order_by(alltime_subq.c.cnt.desc()).limit(RANK_LIMIT).all()
    )
    if not week_quotes:
        week_quotes = alltime_quotes

    pool = week_quotes or alltime_quotes
    if not pool:
        pool = db.query(Quote).order_by(Quote.created_at.desc()).limit(20).all()
    qod = pool[now.timetuple().tm_yday % len(pool)] if pool else None

    all_raw = list({
        q.id: q
        for q in today_quotes + week_quotes + alltime_quotes + ([qod] if qod else [])
    }.values())
    serialized = {out.id: out for out in serialize_quotes(db, all_raw)}

    return StatsOverviewOut(
        date=today,
        is_personal=uid is not None,
        today_stats=TodayStats(
            scraps_today=scraps_today,
            quotes_today=quotes_today,
            total_quotes=total_quotes,
            total_scraps=total_scraps,
        ),
        weekly_activity=weekly_activity,
        top_books=top_books,
        quote_of_day=serialized.get(qod.id) if qod else None,
        top_today=[serialized[q.id] for q in today_quotes if q.id in serialized],
        top_week=[serialized[q.id] for q in week_quotes if q.id in serialized],
        top_alltime=[serialized[q.id] for q in alltime_quotes if q.id in serialized],
    )
