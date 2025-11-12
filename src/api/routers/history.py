"""Validation history endpoints"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional

from ...database.session import get_db_session
from ...database.repository import (
    ValidationHistoryRepository,
    PatternUsageRepository,
    RuleViolationRepository
)
from ...models import ValidationReport

router = APIRouter()


@router.post("/save")
async def save_validation_history(
    report: ValidationReport,
    application_name: Optional[str] = None,
    environment: Optional[str] = None,
    user_id: Optional[str] = None,
    db: Session = Depends(get_db_session)
):
    """
    Save validation report to history.

    This is called internally after validation completes.
    """
    try:
        # Save validation history
        history = ValidationHistoryRepository.save_validation(
            db, report, user_id, environment, application_name
        )

        # Save rule violations
        RuleViolationRepository.save_violations(
            db, history.id, report, application_name, environment
        )

        # Track pattern usage if matched
        if report.pattern_match:
            PatternUsageRepository.track_usage(
                db,
                pattern_id=report.pattern_match.pattern_id,
                pattern_name=report.pattern_match.pattern_name,
                pattern_version="1.0",  # TODO: Get from pattern
                matched=True,
                similarity_score=report.pattern_match.similarity_score,
                validation_id=history.id,
                application_name=application_name,
                environment=environment
            )

        return {
            "status": "success",
            "validation_id": history.id,
            "message": "Validation saved to history"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save validation: {str(e)}")
