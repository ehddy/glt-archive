from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from app.auth.password import validate_signup_password


class AuthorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class AuthorOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class NovelCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author_id: int


class NovelOut(BaseModel):
    id: int
    title: str
    author_id: int
    created_at: datetime
    author: AuthorOut | None = None
    isbn: str | None = None
    isbn13: str | None = None
    publisher: str | None = None
    pub_date: str | None = None
    description: str | None = None
    cover_url: str | None = None
    price_sales: int | None = None
    price_standard: int | None = None
    category_name: str | None = None
    aladin_link: str | None = None
    aladin_item_id: int | None = None
    quote_count: int = 0

    model_config = {"from_attributes": True}


class AladinBookSearchItem(BaseModel):
    item_id: int
    title: str
    author: str
    publisher: str = ""
    pub_date: str | None = None
    description: str | None = None
    isbn: str | None = None
    isbn13: str | None = None
    price_sales: int | None = None
    price_standard: int | None = None
    cover_url: str | None = None
    link: str | None = None
    category_name: str | None = None


class AladinBookDetail(AladinBookSearchItem):
    detail: dict | None = None


class CustomSourceInput(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author_name: str | None = Field(None, max_length=100)


class SourceOut(BaseModel):
    id: int
    title: str
    source_type: str
    author: AuthorOut | None = None
    cover_url: str | None = None
    novel_id: int | None = None
    aladin_item_id: int | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class QuoteCreate(BaseModel):
    text: str = Field(..., min_length=2)
    novel_id: int | None = None
    aladin_item_id: int | None = None
    source_id: int | None = None
    custom_source: CustomSourceInput | None = None

    @model_validator(mode="after")
    def require_source(self):
        if not any(
            (
                self.aladin_item_id,
                self.novel_id,
                self.source_id,
                self.custom_source,
            )
        ):
            raise ValueError("출처는 필수입니다.")
        return self


class QuoteUpdate(BaseModel):
    text: str | None = None


class QuoteVersionOut(BaseModel):
    id: int
    version: int
    text: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RegisteredByOut(BaseModel):
    id: int
    name: str | None = None

    model_config = {"from_attributes": True}


class UserPublicOut(BaseModel):
    id: int
    name: str | None = None
    avatar_url: str | None = None

    model_config = {"from_attributes": True}


class AvatarIn(BaseModel):
    avatar_url: str


class QuoteOut(BaseModel):
    id: int
    text: str
    version: int
    created_at: datetime
    updated_at: datetime
    like_count: int = 0
    scrap_count: int = 0
    novel: NovelOut | None = None
    source: SourceOut | None = None
    author: AuthorOut | None = None
    registered_by: RegisteredByOut | None = None

    model_config = {"from_attributes": True}


class UserOut(BaseModel):
    id: int
    provider: str
    name: str | None = None
    email: str | None = None
    avatar_url: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    name: str | None = Field(None, max_length=100)

    @field_validator("password")
    @classmethod
    def check_password_strength(cls, value: str) -> str:
        validate_signup_password(value)
        return value


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=1, max_length=128)


class AuthTokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class LikeActionOut(BaseModel):
    quote_id: int
    liked: bool
    like_count: int


class LikeIdsOut(BaseModel):
    quote_ids: list[int]


class MyLibraryNovelOut(BaseModel):
    id: int
    title: str
    author: AuthorOut | None = None
    cover_url: str | None = None
    scrap_count: int = 0
    publisher: str | None = None

    model_config = {"from_attributes": True}


class ScrapActionOut(BaseModel):
    quote_id: int
    scrapped: bool
    scrap_count: int


class ScrapIdsOut(BaseModel):
    quote_ids: list[int]


class QuoteSearchResult(BaseModel):
    quote: QuoteOut
    score: float
    match_type: str


class NovelWithQuotesOut(BaseModel):
    id: int
    title: str
    author: AuthorOut | None = None
    quote_count: int
    quotes: list[QuoteOut]
    cover_url: str | None = None
    publisher: str | None = None
    pub_date: str | None = None
    aladin_item_id: int | None = None


class NovelSummaryOut(BaseModel):
    id: int
    title: str
    author: AuthorOut | None = None
    quote_count: int = 0
    cover_url: str | None = None


class PaginatedNovelsOut(BaseModel):
    items: list[NovelSummaryOut]
    total: int
    skip: int
    limit: int


class PaginatedQuotesOut(BaseModel):
    items: list[QuoteOut]
    total: int
    skip: int
    limit: int


class NovelDetailOut(NovelOut):
    quote_count: int = 0
    quotes: list[QuoteOut] = Field(default_factory=list)
    detail: dict | None = None


class LibraryOut(BaseModel):
    books: list[NovelWithQuotesOut]
    unlinked: list[QuoteOut]
    total_quotes: int
    total_books: int


class LibraryStatsOut(BaseModel):
    total_books: int
    total_quotes: int


class HomeOut(BaseModel):
    stats: LibraryStatsOut
    featured_books: list[NovelWithQuotesOut]
    recent_quotes: list[QuoteOut]
    liked_ids: list[int] = Field(default_factory=list)


class BookmarkIdsOut(BaseModel):
    quote_ids: list[int]


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)


class BookRecommendation(BaseModel):
    title: str
    author: str
    reason: str
    in_library: bool = False
    novel_id: int | None = None


class ChatResponse(BaseModel):
    reply: str
    recommendations: list[BookRecommendation] = Field(default_factory=list)


class AiSearchRequest(BaseModel):
    q: str = Field(..., min_length=1, max_length=200)


class AiSearchArticle(BaseModel):
    quote: str
    source_title: str
    author: str = ""
    context: str = ""
    source_url: str | None = None


class AiSearchResponse(BaseModel):
    query: str
    summary: str
    articles: list[AiSearchArticle]


class FeaturedNovelsOut(BaseModel):
    novel_ids: list[int]


class FeaturedNovelsIn(BaseModel):
    novel_ids: list[int] = Field(..., max_length=3)
