"""Analysis API routes for ATS, job matching, and achievements."""

import logging
from pathlib import Path
from uuid import UUID
import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Enhancement, Resume, Job
from app.models.user import User
from app.schemas.analysis import AnalysisResponse, AchievementSuggestionsResponse
from app.utils.ats_analyzer import ATSAnalyzer
from app.utils.achievement_detector import AchievementDetector
from app.api.dependencies import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()
WORKSPACE_ROOT = Path("workspace")

# Initialize analyzers
ats_analyzer = ATSAnalyzer()
achievement_detector = AchievementDetector()


@router.get("/enhancements/{enhancement_id}/analysis", response_model=AnalysisResponse)
async def get_analysis(
    enhancement_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get ATS and job match analysis for an enhancement.

    This endpoint analyzes the resume against the job description to provide:
    - Keyword extraction from both documents
    - Match score (0-100%)
    - Keywords found vs missing
    - Recommendations for improvement

    Results are cached in the database for performance.

    Args:
        enhancement_id: UUID of the enhancement

    Returns:
        AnalysisResponse with full ATS analysis

    Raises:
        404: Enhancement not found
        400: Analysis was not requested or job description missing
    """

    enhancement = db.query(Enhancement).filter(Enhancement.id == enhancement_id).first()
    if not enhancement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enhancement not found: {enhancement_id}"
        )

    # Verify ownership
    if enhancement.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this enhancement",
        )

    # Return cached analysis if exists
    if enhancement.ats_analysis:
        logger.info(f"Returning cached analysis for enhancement {enhancement_id}")
        return {
            'enhancement_id': str(enhancement_id),
            'ats_analysis': json.loads(enhancement.ats_analysis),
            'job_match_score': enhancement.job_match_score or 0,
            'cached': True
        }

    # Check if analysis was requested
    if not enhancement.run_analysis:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Analysis was not requested for this enhancement. "
                   "Create a new enhancement with run_analysis=true to enable analysis."
        )

    # Get resume and job
    resume = db.query(Resume).filter(Resume.id == enhancement.resume_id).first()
    job = db.query(Job).filter(Job.id == enhancement.job_id).first() if enhancement.job_id else None

    if not job:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description is required for analysis. "
                   "This enhancement does not have an associated job."
        )

    # Read texts from workspace
    # Use enhanced resume if available, otherwise fall back to original
    if enhancement.output_path and Path(enhancement.output_path).exists():
        resume_text_path = Path(enhancement.output_path)
        logger.info(f"Using enhanced resume for analysis: {resume_text_path}")
    else:
        resume_text_path = Path(resume.extracted_text_path)
        logger.info(f"Using original resume for analysis: {resume_text_path}")

    job_text_path = Path(job.file_path)

    if not resume_text_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume text file not found: {resume_text_path}"
        )

    if not job_text_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description file not found: {job_text_path}"
        )

    try:
        resume_text = resume_text_path.read_text(encoding='utf-8')
        job_text = job_text_path.read_text(encoding='utf-8')
    except Exception as e:
        logger.error(f"Failed to read text files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read resume or job text: {str(e)}"
        )

    # Run analysis
    logger.info(f"Running ATS analysis for enhancement {enhancement_id}")
    try:
        analysis_result = ats_analyzer.analyze_resume_vs_job(resume_text, job_text)
    except Exception as e:
        logger.error(f"ATS analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

    # Store in database
    try:
        enhancement.ats_analysis = json.dumps(analysis_result)
        enhancement.job_match_score = analysis_result['match_analysis']['match_score']
        db.commit()
        logger.info(f"Analysis cached for enhancement {enhancement_id}, score: {enhancement.job_match_score}")
    except Exception as e:
        logger.error(f"Failed to cache analysis: {e}")
        # Continue even if caching fails

    return {
        'enhancement_id': str(enhancement_id),
        'ats_analysis': analysis_result,
        'job_match_score': analysis_result['match_analysis']['match_score'],
        'cached': False
    }


@router.get("/enhancements/{enhancement_id}/achievements", response_model=AchievementSuggestionsResponse)
async def get_achievement_suggestions(
    enhancement_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get achievement quantification suggestions.

    Analyzes the enhanced resume to find achievements that could be
    strengthened with metrics and quantifiable results.

    Results are cached in the database.

    Args:
        enhancement_id: UUID of the enhancement

    Returns:
        AchievementSuggestionsResponse with suggestions

    Raises:
        404: Enhancement not found or enhanced resume not found
    """

    enhancement = db.query(Enhancement).filter(Enhancement.id == enhancement_id).first()
    if not enhancement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enhancement not found: {enhancement_id}"
        )

    # Verify ownership
    if enhancement.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this enhancement",
        )

    # Return cached suggestions if exist
    if enhancement.achievement_suggestions:
        logger.info(f"Returning cached achievement suggestions for enhancement {enhancement_id}")
        return json.loads(enhancement.achievement_suggestions)

    # Check if enhanced resume exists
    enhanced_md_path = WORKSPACE_ROOT / "resumes" / "enhanced" / str(enhancement_id) / "enhanced.md"
    if not enhanced_md_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enhanced resume not found. Enhancement may not be complete yet."
        )

    # Read enhanced resume
    try:
        enhanced_text = enhanced_md_path.read_text(encoding='utf-8')
    except Exception as e:
        logger.error(f"Failed to read enhanced resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read enhanced resume: {str(e)}"
        )

    # Detect achievements
    logger.info(f"Detecting achievements for enhancement {enhancement_id}")
    try:
        achievements = achievement_detector.detect_achievements(enhanced_text)
        suggestions = achievement_detector.generate_suggestions(achievements)
    except Exception as e:
        logger.error(f"Achievement detection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Achievement detection failed: {str(e)}"
        )

    # Store in database
    try:
        enhancement.achievement_suggestions = json.dumps(suggestions)
        db.commit()
        logger.info(f"Achievement suggestions cached for enhancement {enhancement_id}")
    except Exception as e:
        logger.error(f"Failed to cache suggestions: {e}")
        # Continue even if caching fails

    return suggestions
