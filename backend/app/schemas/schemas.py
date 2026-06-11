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

    model_config = {"from_attributes": True}


class QuoteCreate(BaseModel):
    text: str = Field(..., min_length=2)
    novel_id: int | None = None
    author_id: int | None = None
    novel_title: str | None = None
    author_name: str | None = None


class QuoteUpdate(BaseModel):
    text: str | None = None
    novel_title: str | None = None
    author_name: str | None = None


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


class LibraryOut(BaseModel):
    books: list[NovelWithQuotesOut]
    unlinked: list[QuoteOut]
    total_quotes: int
    total_books: int
