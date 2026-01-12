"""Resume database model."""

from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from ..core.database import Base


class Resume(Base):
    """Resume model for storing uploaded resumes."""

    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    original_format = Column(String(10), nullable=False)  # 'pdf', 'docx', 'txt'
    file_path = Column(Text, nullable=False)  # Path to original file in workspace
    extracted_text_path = Column(Text, nullable=False)  # Path to extracted.txt
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    word_count = Column(Integer, nullable=True)

    # Style preference fields
    selected_style = Column(String(50), nullable=True)  # professional, executive, technical, creative, concise
    style_previews_generated = Column(Boolean, default=False, nullable=False)  # Flag for preview generation status

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Resume(id={self.id}, filename={self.filename}, style={self.selected_style})>"
