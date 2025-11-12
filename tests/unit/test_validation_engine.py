"""Tests for validation engine"""

import pytest
from src.validation.engine import ValidationEngine
from src.validation.rule import ArchitecturalRule, RuleRegistry
from src.models import ValidationResult, ValidationStatus, Severity, RuleCategory


class TestRule(ArchitecturalRule):
    """Test rule that always passes"""

    def __init__(self):
        super().__init__()
        self.id = "TEST-001"
        self.name = "Test Rule"
        self.severity = Severity.LOW
        self.category = RuleCategory.COMPLIANCE

    def validate(self, resource, context=None):
        return self.create_result(
            ValidationStatus.PASSED,
            "Test passed",
            resource_id=resource.get('id', 'unknown')
        )


class TestFailingRule(ArchitecturalRule):
    """Test rule that always fails"""

    def __init__(self):
        super().__init__()
        self.id = "TEST-002"
        self.name = "Test Failing Rule"
        self.severity = Severity.CRITICAL
        self.category = RuleCategory.SECURITY

    def validate(self, resource, context=None):
        return self.create_result(
            ValidationStatus.FAILED,
            "Test failed",
            resource_id=resource.get('id', 'unknown')
        )


def test_validation_engine_initialization():
    """Test validation engine can be initialized"""
    engine = ValidationEngine()
    assert engine is not None
    assert engine.registry is not None


def test_validation_with_passing_rule(sample_resources):
    """Test validation with a passing rule"""
    registry = RuleRegistry()
    registry.register(TestRule())

    engine = ValidationEngine(registry)
    report = engine.validate(
        sample_resources,
        context={'source_type': 'test', 'source_identifier': 'test'}
    )

    assert report is not None
    assert report.overall_status == ValidationStatus.PASSED
    assert report.summary.passed == len(sample_resources)
    assert report.summary.failed == 0


def test_validation_with_failing_rule(sample_resources):
    """Test validation with a failing rule"""
    registry = RuleRegistry()
    registry.register(TestFailingRule())

    engine = ValidationEngine(registry)
    report = engine.validate(
        sample_resources,
        context={'source_type': 'test', 'source_identifier': 'test'}
    )

    assert report is not None
    assert report.overall_status == ValidationStatus.FAILED
    assert report.summary.failed == len(sample_resources)
    assert report.summary.critical_violations == len(sample_resources)


def test_validation_summary_calculation(sample_resources):
    """Test that validation summary is calculated correctly"""
    registry = RuleRegistry()
    registry.register(TestRule())
    registry.register(TestFailingRule())

    engine = ValidationEngine(registry)
    report = engine.validate(
        sample_resources,
        context={'source_type': 'test', 'source_identifier': 'test'}
    )

    # Each resource is validated against each rule
    total_expected = len(sample_resources) * 2

    assert report.summary.total_rules == total_expected
    assert report.summary.passed == len(sample_resources)
    assert report.summary.failed == len(sample_resources)


def test_empty_resources_validation():
    """Test validation with no resources"""
    registry = RuleRegistry()
    registry.register(TestRule())

    engine = ValidationEngine(registry)
    report = engine.validate(
        [],
        context={'source_type': 'test', 'source_identifier': 'test'}
    )

    assert report is not None
    assert report.summary.total_rules == 0
    assert report.overall_status == ValidationStatus.PASSED
