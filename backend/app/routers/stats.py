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
    top_scraps_today: list[QuoteOut] = []
    top_scraps_week: list[QuoteOut] = []
    top_scraps_alltime: list[QuoteOut] = []
    top_likes_today: list[QuoteOut] = []
    top_likes_week: list[QuoteOut] = []
    top_likes_alltime: list[QuoteOut] = []


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

    # ── 전체 통계 (로그인 여부 무관) ───────────────────────────
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

    cutoff_24h = now - timedelta(hours=24)

    def _rank(model, time_filter=None):
        q = db.query(model.quote_id, func.count(model.id).label("cnt"))
        if time_filter is not None:
            q = q.filter(model.created_at >= time_filter)
        subq = q.group_by(model.quote_id).subquery()
        return (
            db.query(Quote).join(subq, Quote.id == subq.c.quote_id)
            .order_by(subq.c.cnt.desc()).limit(RANK_LIMIT).all()
        )

    # ── 스크랩 기준 (오늘/이번주/역대) ─────────────────────────
    st = _rank(QuoteScrap, cutoff_24h)
    sw = _rank(QuoteScrap, cutoff_7d_start)
    sa = _rank(QuoteScrap)
    if not st: st = sa
    if not sw: sw = sa

    # ── 좋아요 기준 (오늘/이번주/역대) ─────────────────────────
    lt = _rank(QuoteLike, cutoff_24h)
    lw = _rank(QuoteLike, cutoff_7d_start)
    la = _rank(QuoteLike)
    if not lt: lt = la
    if not lw: lw = la

    # ── 오늘의 문장 pool ────────────────────────────────────────
    pool = la or sa
    if not pool:
        pool = db.query(Quote).order_by(Quote.created_at.desc()).limit(20).all()
    qod = pool[now.timetuple().tm_yday % len(pool)] if pool else None

    all_raw = list({
        q.id: q
        for q in st + sw + sa + lt + lw + la + ([qod] if qod else [])
    }.values())
    serialized = {out.id: out for out in serialize_quotes(db, all_raw)}

    def _ser(qs): return [serialized[q.id] for q in qs if q.id in serialized]

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
        top_scraps_today=_ser(st),
        top_scraps_week=_ser(sw),
        top_scraps_alltime=_ser(sa),
        top_likes_today=_ser(lt),
        top_likes_week=_ser(lw),
        top_likes_alltime=_ser(la),
    )
