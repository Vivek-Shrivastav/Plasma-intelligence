import uuid
from datetime import datetime, date
from sqlalchemy import String, Text, Integer, Date, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database import Base


class Paper(Base):
    __tablename__ = "papers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    arxiv_id: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True, index=True)
    doi: Mapped[str | None] = mapped_column(String(300), nullable=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    authors: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    abstract: Mapped[str] = mapped_column(Text, nullable=False)
    journal: Mapped[str | None] = mapped_column(String(300), nullable=True)
    published_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    fetched_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )

    # Full Claude analysis (raw JSON blob)
    analysis: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Derived/indexed fields for fast queries
    field: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    subfields: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    importance_score: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    technical_depth: Mapped[str | None] = mapped_column(String(50), nullable=True)
    headline: Mapped[str | None] = mapped_column(Text, nullable=True)
    short_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    keywords: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    concepts_detected: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Figures stored in object storage; this holds their public URLs + descriptions
    figures: Mapped[list] = mapped_column(JSONB, default=list)

    # Source URLs
    pdf_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    paper_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Processing state
    analysis_failed: Mapped[bool] = mapped_column(default=False)
    analysis_error: Mapped[str | None] = mapped_column(Text, nullable=True)
