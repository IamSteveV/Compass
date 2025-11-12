"""Repository layer for database operations"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from .models import ValidationHistory, PatternUsage, RuleViolation, ComplianceTrend
from ..models import ValidationReport


class ValidationHistoryRepository:
    """Repository for validation history operations"""

    @staticmethod
    def save_validation(db: Session, report: ValidationReport,
                       user_id: Optional[str] = None,
                       environment: Optional[str] = None,
                       application_name: Optional[str] = None) -> ValidationHistory:
        """Save validation report to database"""

        # Extract pattern info
        pattern_id = None
        pattern_name = None
        similarity_score = None
        if report.pattern_match:
            pattern_id = report.pattern_match.pattern_id
            pattern_name = report.pattern_match.pattern_name
            similarity_score = report.pattern_match.similarity_score

        # Create history record
        history = ValidationHistory(
            id=report.id,
            timestamp=report.timestamp,
            source_type=report.source_type,
            source_identifier=report.source_identifier,
            pattern_id=pattern_id,
            pattern_name=pattern_name,
            similarity_score=similarity_score,
            approval_track=report.approval_track.value if report.approval_track else None,
            overall_status=report.overall_status.value,
            total_rules=report.summary.total_rules,
            passed=report.summary.passed,
            failed=report.summary.failed,
            warnings=report.summary.warnings,
            skipped=report.summary.skipped,
            compliance_score=report.summary.compliance_score,
            critical_violations=report.summary.critical_violations,
            high_violations=report.summary.high_violations,
            medium_violations=report.summary.medium_violations,
            low_violations=report.summary.low_violations,
            report_json=report.model_dump(mode='json'),
            user_id=user_id,
            environment=environment,
            application_name=application_name
        )

        db.add(history)
        db.commit()
        db.refresh(history)

        return history

    @staticmethod
    def get_by_id(db: Session, validation_id: str) -> Optional[ValidationHistory]:
        """Get validation by ID"""
        return db.query(ValidationHistory).filter(ValidationHistory.id == validation_id).first()

    @staticmethod
    def get_recent(db: Session, limit: int = 50) -> List[ValidationHistory]:
        """Get recent validations"""
        return db.query(ValidationHistory)\
            .order_by(desc(ValidationHistory.timestamp))\
            .limit(limit)\
            .all()

    @staticmethod
    def get_by_application(db: Session, application_name: str,
                          limit: int = 50) -> List[ValidationHistory]:
        """Get validations for a specific application"""
        return db.query(ValidationHistory)\
            .filter(ValidationHistory.application_name == application_name)\
            .order_by(desc(ValidationHistory.timestamp))\
            .limit(limit)\
            .all()

    @staticmethod
    def get_by_environment(db: Session, environment: str,
                          limit: int = 50) -> List[ValidationHistory]:
        """Get validations for a specific environment"""
        return db.query(ValidationHistory)\
            .filter(ValidationHistory.environment == environment)\
            .order_by(desc(ValidationHistory.timestamp))\
            .limit(limit)\
            .all()

    @staticmethod
    def get_compliance_stats(db: Session, days: int = 30) -> Dict[str, Any]:
        """Get compliance statistics for last N days"""
        start_date = datetime.utcnow() - timedelta(days=days)

        validations = db.query(ValidationHistory)\
            .filter(ValidationHistory.timestamp >= start_date)\
            .all()

        if not validations:
            return {
                "total_validations": 0,
                "avg_compliance_score": 0.0,
                "total_violations": 0,
                "pass_rate": 0.0
            }

        total = len(validations)
        passed = sum(1 for v in validations if v.overall_status == "passed")
        total_violations = sum(v.failed for v in validations)
        avg_compliance = sum(v.compliance_score for v in validations) / total

        return {
            "total_validations": total,
            "avg_compliance_score": avg_compliance,
            "total_violations": total_violations,
            "pass_rate": passed / total if total > 0 else 0.0
        }


class PatternUsageRepository:
    """Repository for pattern usage operations"""

    @staticmethod
    def track_usage(db: Session, pattern_id: str, pattern_name: str,
                   pattern_version: str, matched: bool = False,
                   similarity_score: Optional[float] = None,
                   validation_id: Optional[str] = None,
                   application_name: Optional[str] = None,
                   environment: Optional[str] = None,
                   team: Optional[str] = None) -> PatternUsage:
        """Track pattern usage"""

        usage = PatternUsage(
            pattern_id=pattern_id,
            pattern_name=pattern_name,
            pattern_version=pattern_version,
            matched=matched,
            similarity_score=similarity_score,
            validation_id=validation_id,
            application_name=application_name,
            environment=environment,
            team=team
        )

        db.add(usage)
        db.commit()
        db.refresh(usage)

        return usage

    @staticmethod
    def get_popular_patterns(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most used patterns"""
        results = db.query(
            PatternUsage.pattern_id,
            PatternUsage.pattern_name,
            func.count(PatternUsage.id).label('usage_count')
        )\
        .group_by(PatternUsage.pattern_id, PatternUsage.pattern_name)\
        .order_by(desc('usage_count'))\
        .limit(limit)\
        .all()

        return [
            {
                "pattern_id": r.pattern_id,
                "pattern_name": r.pattern_name,
                "usage_count": r.usage_count
            }
            for r in results
        ]

    @staticmethod
    def get_adoption_rate(db: Session, days: int = 30) -> Dict[str, Any]:
        """Get pattern adoption metrics"""
        start_date = datetime.utcnow() - timedelta(days=days)

        total_usage = db.query(func.count(PatternUsage.id))\
            .filter(PatternUsage.timestamp >= start_date)\
            .scalar()

        matched_usage = db.query(func.count(PatternUsage.id))\
            .filter(PatternUsage.timestamp >= start_date)\
            .filter(PatternUsage.matched == True)\
            .scalar()

        return {
            "total_usage": total_usage or 0,
            "matched_usage": matched_usage or 0,
            "adoption_rate": (matched_usage / total_usage) if total_usage > 0 else 0.0
        }


class RuleViolationRepository:
    """Repository for rule violation operations"""

    @staticmethod
    def save_violations(db: Session, validation_id: str, report: ValidationReport,
                       application_name: Optional[str] = None,
                       environment: Optional[str] = None) -> List[RuleViolation]:
        """Save rule violations from validation report"""

        violations = []

        for result in report.results:
            violation = RuleViolation(
                validation_id=validation_id,
                rule_id=result.rule_id,
                rule_name=result.rule_name,
                rule_category=result.category.value,
                rule_severity=result.severity.value,
                status=result.status.value,
                message=result.message,
                resource_id=result.resource_id,
                resource_type=result.resource_type,
                application_name=application_name,
                environment=environment
            )

            db.add(violation)
            violations.append(violation)

        db.commit()

        return violations

    @staticmethod
    def get_most_violated_rules(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequently violated rules"""
        results = db.query(
            RuleViolation.rule_id,
            RuleViolation.rule_name,
            RuleViolation.rule_category,
            RuleViolation.rule_severity,
            func.count(RuleViolation.id).label('violation_count')
        )\
        .filter(RuleViolation.status == 'failed')\
        .group_by(
            RuleViolation.rule_id,
            RuleViolation.rule_name,
            RuleViolation.rule_category,
            RuleViolation.rule_severity
        )\
        .order_by(desc('violation_count'))\
        .limit(limit)\
        .all()

        return [
            {
                "rule_id": r.rule_id,
                "rule_name": r.rule_name,
                "category": r.rule_category,
                "severity": r.rule_severity,
                "violation_count": r.violation_count
            }
            for r in results
        ]

    @staticmethod
    def get_violations_by_application(db: Session, application_name: str,
                                     days: int = 30) -> List[RuleViolation]:
        """Get violations for a specific application"""
        start_date = datetime.utcnow() - timedelta(days=days)

        return db.query(RuleViolation)\
            .filter(RuleViolation.application_name == application_name)\
            .filter(RuleViolation.timestamp >= start_date)\
            .filter(RuleViolation.status == 'failed')\
            .order_by(desc(RuleViolation.timestamp))\
            .all()
