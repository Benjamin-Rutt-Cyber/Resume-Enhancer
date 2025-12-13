"""Pydantic schemas for request/response validation."""

from .resume import ResumeCreate, ResumeResponse, ResumeListResponse
from .job import JobCreate, JobResponse, JobListResponse
from .enhancement import (
    EnhancementTailorCreate,
    EnhancementRevampCreate,
    EnhancementResponse,
    EnhancementListResponse,
)

__all__ = [
    "ResumeCreate",
    "ResumeResponse",
    "ResumeListResponse",
    "JobCreate",
    "JobResponse",
    "JobListResponse",
    "EnhancementTailorCreate",
    "EnhancementRevampCreate",
    "EnhancementResponse",
    "EnhancementListResponse",
]
