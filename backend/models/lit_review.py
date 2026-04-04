import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database import Base


class LiteratureReview(Base):
    __tablename__ = "literature_reviews"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subfield: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    content_markdown: Mapped[str] = mapped_column(Text, nullable=False, default="")
    last_updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    paper_count: Mapped[int] = mapped_column(Integer, default=0)
    earliest_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_seeded: Mapped[bool] = mapped_column(default=False)
