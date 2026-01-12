"""Schemas for analysis responses."""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class AnalysisResponse(BaseModel):
    """Response for ATS and job match analysis."""

    enhancement_id: str
    ats_analysis: Dict[str, Any]
    job_match_score: int
    cached: bool

    class Config:
        json_schema_extra = {
            "example": {
                "enhancement_id": "123e4567-e89b-12d3-a456-426614174000",
                "ats_analysis": {
                    "resume_keywords": {
                        "technical_skills": ["python", "django", "postgresql"],
                        "soft_skills": ["leadership", "communication"],
                        "action_verbs": ["developed", "led"],
                        "certifications": ["aws certified"]
                    },
                    "job_keywords": {
                        "technical_skills": ["python", "django", "react"],
                        "soft_skills": ["leadership"],
                        "action_verbs": ["develop", "manage"],
                        "certifications": []
                    },
                    "match_analysis": {
                        "match_score": 66,
                        "keywords_found": ["python", "django", "leadership"],
                        "keywords_missing": ["react"],
                        "resume_keyword_count": 4,
                        "job_keyword_count": 3,
                        "match_count": 3
                    },
                    "recommendations": [
                        "Moderate match - add key missing skills",
                        "Add these technical skills if applicable: react"
                    ]
                },
                "job_match_score": 66,
                "cached": False
            }
        }


class AchievementSuggestion(BaseModel):
    """Individual achievement with quantification suggestions."""

    achievement: str
    verb: str
    location: str
    suggested_metrics: List[str]
    already_quantified: bool
    achievement_type: str

    class Config:
        json_schema_extra = {
            "example": {
                "achievement": "Improved system performance",
                "verb": "improved",
                "location": "line 42",
                "suggested_metrics": ["by X%", "resulting in X improvement"],
                "already_quantified": False,
                "achievement_type": "improvement"
            }
        }


class AchievementSuggestionsResponse(BaseModel):
    """Response for achievement quantification suggestions."""

    total_achievements: int
    unquantified_count: int
    suggestions: List[AchievementSuggestion]
    summary: str
    breakdown_by_type: Optional[Dict[str, int]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "total_achievements": 15,
                "unquantified_count": 8,
                "suggestions": [
                    {
                        "achievement": "Improved system performance",
                        "verb": "improved",
                        "location": "line 42",
                        "suggested_metrics": ["by X%", "resulting in X improvement"],
                        "already_quantified": False,
                        "achievement_type": "improvement"
                    }
                ],
                "summary": "Found 8 achievements that could be enhanced with specific metrics.",
                "breakdown_by_type": {
                    "improvement": 3,
                    "leadership": 2,
                    "creation": 3
                }
            }
        }
