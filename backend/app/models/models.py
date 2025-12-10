import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Text, Integer, Boolean, Numeric, DateTime, 
    ForeignKey, Enum, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.config.database import Base


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supabase_uid: Mapped[Optional[str]] = mapped_column(String(128), unique=True, nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="user")
    preferred_language: Mapped[str] = mapped_column(String(10), default="th")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    favorites: Mapped[List["Favorite"]] = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    search_history: Mapped[List["SearchHistory"]] = relationship("SearchHistory", back_populates="user", cascade="all, delete-orphan")
    interactions: Mapped[List["UserInteraction"]] = relationship("UserInteraction", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("role IN ('user', 'admin', 'moderator')", name="check_user_role"),
    )


class Author(Base):
    __tablename__ = "authors"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_th: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    biography: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    biography_th: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    books: Mapped[List["Book"]] = relationship("Book", back_populates="author")


class Publisher(Base):
    __tablename__ = "publishers"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_th: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_th: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    books: Mapped[List["Book"]] = relationship("Book", back_populates="publisher")


class Tag(Base):
    __tablename__ = "tags"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name_th: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    category: Mapped[str] = mapped_column(String(50), default="genre")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint("category IN ('genre', 'theme', 'demographic', 'content_warning')", name="check_tag_category"),
    )


class BookTag(Base):
    __tablename__ = "book_tags"
    
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)


class Book(Base):
    __tablename__ = "books"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    title_th: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    original_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description_th: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cover_image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(20), default="manga")
    status: Mapped[str] = mapped_column(String(20), default="ongoing")
    publication_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_chapters: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_volumes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    author_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("authors.id", ondelete="SET NULL"), nullable=True)
    publisher_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("publishers.id", ondelete="SET NULL"), nullable=True)
    average_rating: Mapped[float] = mapped_column(Numeric(3, 2), default=0.00)
    total_ratings: Mapped[int] = mapped_column(Integer, default=0)
    total_reviews: Mapped[int] = mapped_column(Integer, default=0)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author: Mapped[Optional["Author"]] = relationship("Author", back_populates="books")
    publisher: Mapped[Optional["Publisher"]] = relationship("Publisher", back_populates="books")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="book", cascade="all, delete-orphan")
    favorites: Mapped[List["Favorite"]] = relationship("Favorite", back_populates="book", cascade="all, delete-orphan")
    tags: Mapped[List["Tag"]] = relationship("Tag", secondary="book_tags", lazy="joined")
    interactions: Mapped[List["UserInteraction"]] = relationship("UserInteraction", back_populates="book", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint("type IN ('manga', 'novel', 'light_novel', 'manhwa', 'manhua')", name="check_book_type"),
        CheckConstraint("status IN ('ongoing', 'completed', 'hiatus', 'cancelled')", name="check_book_status"),
    )


class Review(Base):
    __tablename__ = "reviews"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_spoiler: Mapped[bool] = mapped_column(Boolean, default=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=True)
    helpful_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="reviews")
    book: Mapped["Book"] = relationship("Book", back_populates="reviews")
    
    __table_args__ = (
        UniqueConstraint("user_id", "book_id", name="unique_user_book_review"),
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_review_rating"),
    )


class Favorite(Base):
    __tablename__ = "favorites"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    list_name: Mapped[str] = mapped_column(String(50), default="favorites")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="favorites")
    book: Mapped["Book"] = relationship("Book", back_populates="favorites")
    
    __table_args__ = (
        UniqueConstraint("user_id", "book_id", "list_name", name="unique_user_book_list"),
        CheckConstraint("list_name IN ('favorites', 'reading', 'completed', 'plan_to_read', 'dropped')", name="check_list_name"),
    )


class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    search_query: Mapped[str] = mapped_column(String(500), nullable=False)
    filters: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    results_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="search_history")


class UserInteraction(Base):
    __tablename__ = "user_interactions"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    interaction_type: Mapped[str] = mapped_column(String(20), nullable=False)
    interaction_weight: Mapped[float] = mapped_column(Numeric(3, 2), default=1.00)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="interactions")
    book: Mapped["Book"] = relationship("Book", back_populates="interactions")
    
    __table_args__ = (
        CheckConstraint("interaction_type IN ('view', 'click', 'read_more', 'share')", name="check_interaction_type"),
    )
