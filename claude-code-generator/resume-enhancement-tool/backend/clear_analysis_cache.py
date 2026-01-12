#!/usr/bin/env python3
"""Clear cached ATS analysis to force re-analysis."""

import sys
from uuid import UUID
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.enhancement import Enhancement

def main():
    db = SessionLocal()
    try:
        enhancement_id = UUID("ce7929c1-bd69-4150-b2a5-c0b2c00575d4")
        enhancement = db.query(Enhancement).filter(Enhancement.id == enhancement_id).first()

        if not enhancement:
            print(f"Enhancement {enhancement_id} not found")
            return

        # Clear cached analysis
        enhancement.ats_analysis = None
        enhancement.job_match_score = None
        db.commit()

        print(f"Cleared cached analysis for enhancement {enhancement_id}")

    finally:
        db.close()

if __name__ == "__main__":
    main()
