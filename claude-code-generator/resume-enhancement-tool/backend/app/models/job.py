"""Job description database model."""

from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from ..core.database import Base


class Job(Base):
    """Job model for storing job descriptions."""

    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=True)
    description_text = Column(Text, nullable=False)
    file_path = Column(Text, nullable=False)  # Path to description.txt in workspace
    source = Column(String(50), nullable=False)  # 'upload', 'paste'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Job(id={self.id}, title={self.title}, company={self.company})>"
