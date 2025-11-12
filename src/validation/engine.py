"""Validation engine for executing rules against infrastructure"""

import asyncio
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import uuid
from datetime import datetime

from .rule import ArchitecturalRule, RuleRegistry, get_rule_registry
from ..models import (
    ValidationResult,
    ValidationReport,
    ValidationSummary,
    ValidationStatus,
    Severity,
    ApprovalTrack,
    PatternMatch
)
from ..config import get_settings


class ValidationEngine:
    """Engine for executing validation rules against infrastructure"""

    def __init__(self, registry: Optional[RuleRegistry] = None):
        """
        Initialize validation engine.

        Args:
            registry: Rule registry to use (defaults to global registry)
        """
        self.registry = registry or get_rule_registry()
        self.settings = get_settings()

    def validate(
        self,
        resources: List[Any],
        context: Optional[Dict[str, Any]] = None,
        rule_ids: Optional[List[str]] = None
    ) -> ValidationReport:
        """
        Execute validation rules against resources.

        Args:
            resources: List of resources to validate
            context: Additional context (topology, relationships, etc.)
            rule_ids: Specific rule IDs to execute (None = all rules)

        Returns:
            ValidationReport with results
        """
        # Get rules to execute
        if rule_ids:
            rules = [self.registry.get_rule(rid) for rid in rule_ids if self.registry.get_rule(rid)]
        else:
            rules = self.registry.get_all_rules()

        # Execute rules
        if self.settings.validation.parallel_execution:
            results = self._validate_parallel(resources, rules, context)
        else:
            results = self._validate_sequential(resources, rules, context)

        # Create report
        return self._create_report(results, context)

    def _validate_sequential(
        self,
        resources: List[Any],
        rules: List[ArchitecturalRule],
        context: Optional[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """Execute rules sequentially"""
        results = []

        for rule in rules:
            for resource in resources:
                try:
                    result = rule.validate(resource, context)
                    results.append(result)
                except Exception as e:
                    # Log error and create failed result
                    results.append(ValidationResult(
                        rule_id=rule.id,
                        rule_name=rule.name,
                        severity=rule.severity,
                        category=rule.category,
                        status=ValidationStatus.FAILED,
                        message=f"Rule execution failed: {str(e)}",
                        details={"error": str(e)}
                    ))

        return results

    def _validate_parallel(
        self,
        resources: List[Any],
        rules: List[ArchitecturalRule],
        context: Optional[Dict[str, Any]]
    ) -> List[ValidationResult]:
        """Execute rules in parallel using thread pool"""
        results = []

        def validate_rule_resource(rule: ArchitecturalRule, resource: Any) -> ValidationResult:
            try:
                return rule.validate(resource, context)
            except Exception as e:
                return ValidationResult(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    severity=rule.severity,
                    category=rule.category,
                    status=ValidationStatus.FAILED,
                    message=f"Rule execution failed: {str(e)}",
                    details={"error": str(e)}
                )

        with ThreadPoolExecutor(max_workers=self.settings.validation.max_workers) as executor:
            futures = []
            for rule in rules:
                for resource in resources:
                    future = executor.submit(validate_rule_resource, rule, resource)
                    futures.append(future)

            for future in futures:
                results.append(future.result())

        return results

    def _create_report(
        self,
        results: List[ValidationResult],
        context: Optional[Dict[str, Any]]
    ) -> ValidationReport:
        """Create validation report from results"""
        # Calculate summary statistics
        summary = self._calculate_summary(results)

        # Determine overall status
        if summary.critical_violations > 0 and self.settings.validation.fail_on_critical:
            overall_status = ValidationStatus.FAILED
        elif summary.failed > 0:
            overall_status = ValidationStatus.FAILED
        elif summary.warnings > 0:
            overall_status = ValidationStatus.WARNING
        else:
            overall_status = ValidationStatus.PASSED

        # Get pattern match and approval track from context if available
        pattern_match = context.get("pattern_match") if context else None
        approval_track = self._determine_approval_track(pattern_match)

        # Get source information from context
        source_type = context.get("source_type", "unknown") if context else "unknown"
        source_identifier = context.get("source_identifier", "unknown") if context else "unknown"

        return ValidationReport(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            source_type=source_type,
            source_identifier=source_identifier,
            results=results,
            pattern_match=pattern_match,
            approval_track=approval_track,
            overall_status=overall_status,
            summary=summary
        )

    def _calculate_summary(self, results: List[ValidationResult]) -> ValidationSummary:
        """Calculate summary statistics from validation results"""
        total = len(results)
        passed = sum(1 for r in results if r.status == ValidationStatus.PASSED)
        failed = sum(1 for r in results if r.status == ValidationStatus.FAILED)
        warnings = sum(1 for r in results if r.status == ValidationStatus.WARNING)
        skipped = sum(1 for r in results if r.status == ValidationStatus.SKIPPED)

        # Count by severity
        critical = sum(1 for r in results
                      if r.status == ValidationStatus.FAILED and r.severity == Severity.CRITICAL)
        high = sum(1 for r in results
                  if r.status == ValidationStatus.FAILED and r.severity == Severity.HIGH)
        medium = sum(1 for r in results
                    if r.status == ValidationStatus.FAILED and r.severity == Severity.MEDIUM)
        low = sum(1 for r in results
                 if r.status == ValidationStatus.FAILED and r.severity == Severity.LOW)

        # Calculate compliance score (excluding skipped)
        evaluable = total - skipped
        compliance_score = passed / evaluable if evaluable > 0 else 0.0

        return ValidationSummary(
            total_rules=total,
            passed=passed,
            failed=failed,
            warnings=warnings,
            skipped=skipped,
            critical_violations=critical,
            high_violations=high,
            medium_violations=medium,
            low_violations=low,
            compliance_score=compliance_score
        )

    def _determine_approval_track(self, pattern_match: Optional[PatternMatch]) -> Optional[ApprovalTrack]:
        """Determine approval track based on pattern match score"""
        if not pattern_match:
            return ApprovalTrack.FULL_REVIEW

        score = pattern_match.similarity_score
        approval_config = self.settings.approval

        if score >= approval_config.fast_track_threshold:
            return ApprovalTrack.FAST_TRACK
        elif score >= approval_config.standard_review_threshold:
            return ApprovalTrack.STANDARD_REVIEW
        else:
            return ApprovalTrack.FULL_REVIEW
