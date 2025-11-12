"""Analytics and reporting endpoints"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ...database.session import get_db_session
from ...database.repository import (
    ValidationHistoryRepository,
    PatternUsageRepository,
    RuleViolationRepository
)

router = APIRouter()


@router.get("/compliance/overview")
async def get_compliance_overview(
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db_session)
):
    """
    Get compliance overview for last N days.

    Returns aggregated compliance metrics.
    """
    stats = ValidationHistoryRepository.get_compliance_stats(db, days)

    return {
        "period_days": days,
        "metrics": stats,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/validations/recent")
async def get_recent_validations(
    limit: int = Query(50, description="Maximum results"),
    db: Session = Depends(get_db_session)
):
    """Get recent validation history"""
    validations = ValidationHistoryRepository.get_recent(db, limit)

    return [
        {
            "id": v.id,
            "timestamp": v.timestamp.isoformat(),
            "source_type": v.source_type,
            "application_name": v.application_name,
            "environment": v.environment,
            "pattern_name": v.pattern_name,
            "compliance_score": v.compliance_score,
            "overall_status": v.overall_status,
            "approval_track": v.approval_track
        }
        for v in validations
    ]


@router.get("/validations/{validation_id}")
async def get_validation_details(
    validation_id: str,
    db: Session = Depends(get_db_session)
):
    """Get detailed validation report by ID"""
    validation = ValidationHistoryRepository.get_by_id(db, validation_id)

    if not validation:
        raise HTTPException(status_code=404, detail="Validation not found")

    return validation.report_json


@router.get("/validations/application/{application_name}")
async def get_application_validations(
    application_name: str,
    limit: int = Query(50, description="Maximum results"),
    db: Session = Depends(get_db_session)
):
    """Get validation history for a specific application"""
    validations = ValidationHistoryRepository.get_by_application(db, application_name, limit)

    return [
        {
            "id": v.id,
            "timestamp": v.timestamp.isoformat(),
            "compliance_score": v.compliance_score,
            "overall_status": v.overall_status,
            "violations": v.failed,
            "pattern_match": v.pattern_name
        }
        for v in validations
    ]


@router.get("/patterns/popular")
async def get_popular_patterns(
    limit: int = Query(10, description="Number of patterns to return"),
    db: Session = Depends(get_db_session)
):
    """Get most popular patterns by usage"""
    patterns = PatternUsageRepository.get_popular_patterns(db, limit)
    return patterns


@router.get("/patterns/adoption")
async def get_pattern_adoption(
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db_session)
):
    """Get pattern adoption metrics"""
    metrics = PatternUsageRepository.get_adoption_rate(db, days)
    return {
        "period_days": days,
        **metrics
    }


@router.get("/violations/top-rules")
async def get_most_violated_rules(
    limit: int = Query(10, description="Number of rules to return"),
    db: Session = Depends(get_db_session)
):
    """Get most frequently violated rules"""
    violations = RuleViolationRepository.get_most_violated_rules(db, limit)
    return violations


@router.get("/violations/application/{application_name}")
async def get_application_violations(
    application_name: str,
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db_session)
):
    """Get violations for a specific application"""
    violations = RuleViolationRepository.get_violations_by_application(
        db, application_name, days
    )

    return [
        {
            "timestamp": v.timestamp.isoformat(),
            "rule_id": v.rule_id,
            "rule_name": v.rule_name,
            "severity": v.rule_severity,
            "category": v.rule_category,
            "message": v.message,
            "resource_id": v.resource_id
        }
        for v in violations
    ]


@router.get("/dashboard/summary")
async def get_dashboard_summary(
    db: Session = Depends(get_db_session)
):
    """
    Get summary data for dashboard.

    Returns key metrics for overview dashboard.
    """
    # Get 30-day stats
    compliance_stats = ValidationHistoryRepository.get_compliance_stats(db, 30)
    popular_patterns = PatternUsageRepository.get_popular_patterns(db, 5)
    adoption = PatternUsageRepository.get_adoption_rate(db, 30)
    top_violations = RuleViolationRepository.get_most_violated_rules(db, 5)

    return {
        "compliance": compliance_stats,
        "popular_patterns": popular_patterns,
        "pattern_adoption": adoption,
        "top_violations": top_violations,
        "generated_at": datetime.utcnow().isoformat()
    }
