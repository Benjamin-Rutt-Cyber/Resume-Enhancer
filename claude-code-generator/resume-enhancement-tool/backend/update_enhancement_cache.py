#!/usr/bin/env python3
"""Update enhancement cache to clear old DOCX files"""
import sys
sys.path.insert(0, '.')

from app.core.database import SessionLocal
from app.models.enhancement import Enhancement
from datetime import datetime
from sqlalchemy import text
import uuid

db = SessionLocal()
try:
    # Use UUID object for the filter
    enhancement_id = '0c94a9bb-c0cd-4431-af46-511ea06e7a6a'

    # Query using string comparison (SQLite stores as text)
    result = db.execute(
        text("""
        UPDATE enhancements
        SET docx_path = NULL,
            cover_letter_docx_path = NULL,
            updated_at = :updated_at
        WHERE id = :id
        """),
        {"id": enhancement_id, "updated_at": datetime.utcnow()}
    )
    db.commit()

    print(f'SUCCESS: Database updated - Cleared DOCX cache for enhancement {enhancement_id}')
    print(f'Rows affected: {result.rowcount}')

finally:
    db.close()
