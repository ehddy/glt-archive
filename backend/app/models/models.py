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
    quotes: Mapped[list["Quote"]] = relationship(back_populates="author")


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


class Quote(Base):
    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    text: Mapped[str] = mapped_column(Text, index=True)
    novel_id: Mapped[int | None] = mapped_column(ForeignKey("novels.id"), nullable=True)
    author_id: Mapped[int | None] = mapped_column(ForeignKey("authors.id"), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    novel: Mapped["Novel | None"] = relationship(back_populates="quotes")
    author: Mapped["Author | None"] = relationship(back_populates="quotes")
    versions: Mapped[list["QuoteVersion"]] = relationship(
        back_populates="quote", order_by="QuoteVersion.version"
    )
    bookmarks: Mapped[list["Bookmark"]] = relationship(back_populates="quote")


class Bookmark(Base):
    __tablename__ = "bookmarks"
    __table_args__ = (UniqueConstraint("client_id", "quote_id", name="uq_bookmark_client_quote"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    client_id: Mapped[str] = mapped_column(String(64), index=True)
    quote_id: Mapped[int] = mapped_column(ForeignKey("quotes.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    quote: Mapped["Quote"] = relationship(back_populates="bookmarks")


class QuoteVersion(Base):
    __tablename__ = "quote_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    quote_id: Mapped[int] = mapped_column(ForeignKey("quotes.id"))
    version: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    quote: Mapped["Quote"] = relationship(back_populates="versions")
