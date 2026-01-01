"""
Health check endpoints.
"""

import shutil
import os
from pathlib import Path
from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Comprehensive health check endpoint.

    Checks:
    - Database connectivity
    - Workspace directory (exists, writable)
    - Disk space (warns if < 1GB, unhealthy if < 0.5GB)

    Returns:
        dict: Comprehensive health status with individual check results
    """
    checks = {}
    overall_healthy = True

    # 1. Database connectivity check
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        checks["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        overall_healthy = False

    # 2. Workspace directory check
    workspace_path = Path(settings.WORKSPACE_ROOT)
    try:
        # Check if directory exists
        if not workspace_path.exists():
            checks["workspace"] = {
                "status": "unhealthy",
                "message": f"Workspace directory does not exist: {workspace_path}"
            }
            overall_healthy = False
        else:
            # Check if directory is writable
            test_file = workspace_path / ".health_check_test"
            try:
                test_file.write_text("test")
                test_file.unlink()
                checks["workspace"] = {
                    "status": "healthy",
                    "message": f"Workspace directory accessible and writable: {workspace_path}"
                }
            except Exception as e:
                checks["workspace"] = {
                    "status": "unhealthy",
                    "message": f"Workspace directory not writable: {str(e)}"
                }
                overall_healthy = False
    except Exception as e:
        checks["workspace"] = {
            "status": "unhealthy",
            "message": f"Workspace check failed: {str(e)}"
        }
        overall_healthy = False

    # 3. Disk space check
    try:
        disk_usage = shutil.disk_usage(workspace_path if workspace_path.exists() else os.getcwd())
        free_gb = disk_usage.free / (1024 ** 3)  # Convert to GB

        if free_gb < 0.5:
            checks["disk_space"] = {
                "status": "unhealthy",
                "message": f"Critical: Only {free_gb:.2f} GB free disk space (minimum 0.5 GB required)",
                "free_gb": round(free_gb, 2)
            }
            overall_healthy = False
        elif free_gb < 1.0:
            checks["disk_space"] = {
                "status": "warning",
                "message": f"Low disk space: {free_gb:.2f} GB free (recommended minimum 1 GB)",
                "free_gb": round(free_gb, 2)
            }
        else:
            checks["disk_space"] = {
                "status": "healthy",
                "message": f"Sufficient disk space: {free_gb:.2f} GB free",
                "free_gb": round(free_gb, 2)
            }
    except Exception as e:
        checks["disk_space"] = {
            "status": "unknown",
            "message": f"Could not check disk space: {str(e)}"
        }

    return {
        "status": "healthy" if overall_healthy else "unhealthy",
        "checks": checks,
        "version": settings.APP_VERSION
    }
