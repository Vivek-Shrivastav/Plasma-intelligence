import uuid
from datetime import datetime, date
from sqlalchemy import String, Text, Integer, Date, TIMESTAMP, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database import Base


class OpenProblem(Base):
    __tablename__ = "open_problems"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    paper_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("papers.id"), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    subfields: Mapped[list] = mapped_column(JSONB, default=list)
    specificity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())


class OpenProblemCluster(Base):
    __tablename__ = "open_problem_clusters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    theme: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    subfields: Mapped[list] = mapped_column(JSONB, default=list)
    paper_ids: Mapped[list] = mapped_column(JSONB, default=list)
    urgency: Mapped[str] = mapped_column(String(20), default="medium")
    frequency: Mapped[int] = mapped_column(Integer, default=1)
    first_appeared: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_appeared: Mapped[date | None] = mapped_column(Date, nullable=True)
    synthesized_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
