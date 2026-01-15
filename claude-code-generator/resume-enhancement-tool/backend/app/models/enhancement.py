"""Enhancement database model."""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from ..core.database import Base


class Enhancement(Base):
    """Enhancement model for tracking resume enhancement requests."""

    __tablename__ = "enhancements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=True)
    enhancement_type = Column(
        String(50), nullable=False
    )  # 'job_tailoring', 'industry_revamp'
    industry = Column(String(100), nullable=True)  # For industry_revamp type

    # Content columns for DB-based storage (survives Render redeployments)
    instructions_text = Column(Text, nullable=True)  # INSTRUCTIONS.md content
    enhanced_content = Column(Text, nullable=True)  # enhanced.md content
    cover_letter_content = Column(Text, nullable=True)  # cover_letter.md content

    # File path columns (for local file caching)
    output_path = Column(Text, nullable=True)  # Path to enhanced.md
    pdf_path = Column(Text, nullable=True)  # Path to enhanced.pdf
    docx_path = Column(Text, nullable=True)  # Path to enhanced.docx

    # Cover letter fields
    cover_letter_path = Column(Text, nullable=True)  # Path to cover_letter.md
    cover_letter_pdf_path = Column(Text, nullable=True)  # Path to cover_letter.pdf
    cover_letter_docx_path = Column(Text, nullable=True)  # Path to cover_letter.docx
    cover_letter_status = Column(String(50), nullable=False, default="pending")  # Status tracking
    cover_letter_error = Column(Text, nullable=True)  # Error message if generation fails

    # Analysis fields (JSON stored as Text)
    run_analysis = Column(Boolean, default=False, nullable=False)  # Whether to run ATS analysis
    ats_analysis = Column(Text, nullable=True)  # JSON: {keywords_found, keywords_missing, match_score, etc.}
    job_match_score = Column(Integer, nullable=True)  # 0-100 percentage
    achievement_suggestions = Column(Text, nullable=True)  # JSON: [{achievement, suggested_metric, location}]

    status = Column(String(50), nullable=False, default="pending")  # 'pending', 'completed', 'failed'
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Enhancement(id={self.id}, type={self.enhancement_type}, status={self.status})>"
