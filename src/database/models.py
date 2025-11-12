"""Database models for persistence"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class ValidationHistory(Base):
    """Store validation history for tracking and analytics"""

    __tablename__ = "validation_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Source information
    source_type = Column(String(20), nullable=False, index=True)  # terraform, cmdb
    source_identifier = Column(String(255), nullable=False)

    # Pattern matching
    pattern_id = Column(String(50), index=True)
    pattern_name = Column(String(255))
    similarity_score = Column(Float)
    approval_track = Column(String(20), index=True)

    # Validation results
    overall_status = Column(String(20), nullable=False, index=True)
    total_rules = Column(Integer, default=0)
    passed = Column(Integer, default=0)
    failed = Column(Integer, default=0)
    warnings = Column(Integer, default=0)
    skipped = Column(Integer, default=0)
    compliance_score = Column(Float, default=0.0, index=True)

    # Violations by severity
    critical_violations = Column(Integer, default=0)
    high_violations = Column(Integer, default=0)
    medium_violations = Column(Integer, default=0)
    low_violations = Column(Integer, default=0)

    # Full report (JSON)
    report_json = Column(JSON)

    # Metadata
    user_id = Column(String(100))
    environment = Column(String(50), index=True)
    application_name = Column(String(255), index=True)

    def __repr__(self):
        return f"<ValidationHistory(id={self.id}, source={self.source_type}, status={self.overall_status})>"


class PatternUsage(Base):
    """Track pattern usage statistics"""

    __tablename__ = "pattern_usage"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    pattern_id = Column(String(50), nullable=False, index=True)
    pattern_name = Column(String(255))
    pattern_version = Column(String(20))

    # Usage context
    matched = Column(Boolean, default=False)  # Was this pattern matched or manually selected?
    similarity_score = Column(Float)
    validation_id = Column(String(36))  # FK to ValidationHistory

    # Application context
    application_name = Column(String(255))
    environment = Column(String(50))
    team = Column(String(100))

    def __repr__(self):
        return f"<PatternUsage(pattern_id={self.pattern_id}, matched={self.matched})>"


class RuleViolation(Base):
    """Track individual rule violations for analytics"""

    __tablename__ = "rule_violations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    validation_id = Column(String(36), nullable=False, index=True)  # FK to ValidationHistory

    # Rule information
    rule_id = Column(String(50), nullable=False, index=True)
    rule_name = Column(String(255))
    rule_category = Column(String(50), index=True)
    rule_severity = Column(String(20), index=True)

    # Violation details
    status = Column(String(20), nullable=False)  # passed, failed, warning, skipped
    message = Column(Text)
    resource_id = Column(String(255))
    resource_type = Column(String(100))

    # Context
    application_name = Column(String(255), index=True)
    environment = Column(String(50), index=True)

    def __repr__(self):
        return f"<RuleViolation(rule_id={self.rule_id}, status={self.status})>"


class ComplianceTrend(Base):
    """Daily compliance trend aggregates"""

    __tablename__ = "compliance_trends"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(DateTime, nullable=False, index=True)

    # Aggregated metrics
    total_validations = Column(Integer, default=0)
    avg_compliance_score = Column(Float, default=0.0)
    total_violations = Column(Integer, default=0)
    critical_violations = Column(Integer, default=0)

    # By environment
    environment = Column(String(50), index=True)

    # Pattern adoption
    pattern_matches = Column(Integer, default=0)
    fast_track_count = Column(Integer, default=0)
    standard_review_count = Column(Integer, default=0)
    full_review_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<ComplianceTrend(date={self.date}, avg_score={self.avg_compliance_score})>"
