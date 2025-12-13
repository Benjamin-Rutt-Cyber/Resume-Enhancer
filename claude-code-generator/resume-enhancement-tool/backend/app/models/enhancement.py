"""Enhancement database model."""

from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from ..core.database import Base


class Enhancement(Base):
    """Enhancement model for tracking resume enhancement requests."""

    __tablename__ = "enhancements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=True)
    enhancement_type = Column(
        String(50), nullable=False
    )  # 'job_tailoring', 'industry_revamp'
    industry = Column(String(100), nullable=True)  # For industry_revamp type
    output_path = Column(Text, nullable=True)  # Path to enhanced.md
    pdf_path = Column(Text, nullable=True)  # Path to enhanced.pdf
    status = Column(String(50), nullable=False, default="pending")  # 'pending', 'completed', 'failed'
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Enhancement(id={self.id}, type={self.enhancement_type}, status={self.status})>"
