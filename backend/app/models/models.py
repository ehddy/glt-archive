from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    novels: Mapped[list["Novel"]] = relationship(back_populates="author")
    sources: Mapped[list["Source"]] = relationship(back_populates="author")
    quotes: Mapped[list["Quote"]] = relationship(back_populates="author")


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("authors.id"), nullable=True)
    source_type: Mapped[str] = mapped_column(String(20), default="custom", index=True)
    novel_id: Mapped[int | None] = mapped_column(
        ForeignKey("novels.id"), nullable=True, unique=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    author: Mapped["Author | None"] = relationship(back_populates="sources")
    novel: Mapped["Novel | None"] = relationship(back_populates="source")
    quotes: Mapped[list["Quote"]] = relationship(back_populates="source")


class Novel(Base):
    __tablename__ = "novels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    aladin_item_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True, index=True)
    isbn: Mapped[str | None] = mapped_column(String(20), nullable=True)
    isbn13: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    publisher: Mapped[str | None] = mapped_column(String(200), nullable=True)
    pub_date: Mapped[str | None] = mapped_column(String(30), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    price_sales: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_standard: Mapped[int | None] = mapped_column(Integer, nullable=True)
    category_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    aladin_link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    detail_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    author: Mapped["Author"] = relationship(back_populates="novels")
    quotes: Mapped[list["Quote"]] = relationship(back_populates="novel")
    source: Mapped["Source | None"] = relationship(back_populates="novel", uselist=False)


class Quote(Base):
    __tablename__ = "quotes"
    __table_args__ = (
        UniqueConstraint("source_id", "text", name="uq_quote_source_text"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    text: Mapped[str] = mapped_column(Text, index=True)
    novel_id: Mapped[int | None] = mapped_column(ForeignKey("novels.id"), nullable=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False, index=True)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("authors.id"), nullable=True)
    registered_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    novel: Mapped["Novel | None"] = relationship(back_populates="quotes")
    source: Mapped["Source | None"] = relationship(back_populates="quotes")
    author: Mapped["Author | None"] = relationship(back_populates="quotes")
    registered_by: Mapped["User | None"] = relationship(foreign_keys=[registered_by_id])
    versions: Mapped[list["QuoteVersion"]] = relationship(
        back_populates="quote", order_by="QuoteVersion.version"
    )
    bookmarks: Mapped[list["Bookmark"]] = relationship(back_populates="quote")
    likes: Mapped[list["QuoteLike"]] = relationship(back_populates="quote")
    scraps: Mapped[list["QuoteScrap"]] = relationship(back_populates="quote")


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_user_provider"),
        UniqueConstraint("email", name="uq_user_email"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    provider: Mapped[str] = mapped_column(String(20), default="local", index=True)
    provider_user_id: Mapped[str] = mapped_column(String(64), index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    likes: Mapped[list["QuoteLike"]] = relationship(back_populates="user")


class QuoteLike(Base):
    __tablename__ = "quote_likes"
    __table_args__ = (
        UniqueConstraint("user_id", "quote_id", name="uq_like_user_quote"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    quote_id: Mapped[int] = mapped_column(ForeignKey("quotes.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="likes")
    quote: Mapped["Quote"] = relationship(back_populates="likes")


class QuoteScrap(Base):
    __tablename__ = "quote_scraps"
    __table_args__ = (
        UniqueConstraint("user_id", "quote_id", name="uq_scrap_user_quote"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    quote_id: Mapped[int] = mapped_column(ForeignKey("quotes.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(foreign_keys=[user_id])
    quote: Mapped["Quote"] = relationship(back_populates="scraps")


class Bookmark(Base):
    __tablename__ = "bookmarks"
    __table_args__ = (UniqueConstraint("client_id", "quote_id", name="uq_bookmark_client_quote"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    client_id: Mapped[str] = mapped_column(String(64), index=True)
    quote_id: Mapped[int] = mapped_column(ForeignKey("quotes.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    quote: Mapped["Quote"] = relationship(back_populates="bookmarks")


class UserFeaturedNovel(Base):
    __tablename__ = "user_featured_novels"
    __table_args__ = (
        UniqueConstraint("user_id", "novel_id", name="uq_featured_user_novel"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    novel_id: Mapped[int] = mapped_column(ForeignKey("novels.id"), index=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(foreign_keys=[user_id])
    novel: Mapped["Novel"] = relationship(foreign_keys=[novel_id])


class QuoteVersion(Base):
    __tablename__ = "quote_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    quote_id: Mapped[int] = mapped_column(ForeignKey("quotes.id"))
    version: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    quote: Mapped["Quote"] = relationship(back_populates="versions")
