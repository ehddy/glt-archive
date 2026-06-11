from datetime import datetime

from pydantic import BaseModel, Field


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


class QuoteCreate(BaseModel):
    text: str = Field(..., min_length=2)
    novel_id: int | None = None
    aladin_item_id: int | None = None


class QuoteUpdate(BaseModel):
    text: str | None = None


class QuoteVersionOut(BaseModel):
    id: int
    version: int
    text: str
    created_at: datetime

    model_config = {"from_attributes": True}


class QuoteOut(BaseModel):
    id: int
    text: str
    version: int
    created_at: datetime
    updated_at: datetime
    novel: NovelOut | None = None
    author: AuthorOut | None = None

    model_config = {"from_attributes": True}


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
