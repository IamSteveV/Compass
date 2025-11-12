"""Tests for validation rules"""

import pytest
from src.validation.rules.security_rules import ProductionDatabaseEncryptionRule
from src.validation.rules.metadata_rules import RequiredMetadataRule
from src.validation.rules.resilience_rules import ProductionMultiAZRule
from src.models import ValidationStatus


def test_database_encryption_rule_pass():
    """Test database encryption rule with encrypted database"""
    rule = ProductionDatabaseEncryptionRule()

    resource = {
        'id': 'db-1',
        'type': 'database',
        'environment': 'production',
        'encrypted': True
    }

    result = rule.validate(resource)

    assert result.status == ValidationStatus.PASSED


def test_database_encryption_rule_fail():
    """Test database encryption rule with unencrypted database"""
    rule = ProductionDatabaseEncryptionRule()

    resource = {
        'id': 'db-1',
        'type': 'database',
        'environment': 'production',
        'encrypted': False
    }

    result = rule.validate(resource)

    assert result.status == ValidationStatus.FAILED


def test_required_metadata_rule_pass():
    """Test required metadata rule with complete metadata"""
    rule = RequiredMetadataRule()

    resource = {
        'id': 'server-1',
        'business_owner': 'team-a',
        'technical_owner': 'ops',
        'data_classification': 'internal'
    }

    result = rule.validate(resource)

    assert result.status == ValidationStatus.PASSED


def test_required_metadata_rule_fail():
    """Test required metadata rule with missing metadata"""
    rule = RequiredMetadataRule()

    resource = {
        'id': 'server-1',
        'business_owner': 'team-a'
        # Missing technical_owner and data_classification
    }

    result = rule.validate(resource)

    assert result.status == ValidationStatus.FAILED
    assert 'technical_owner' in result.details['missing_fields']
    assert 'data_classification' in result.details['missing_fields']


def test_multi_az_rule_pass():
    """Test multi-AZ rule with compliant resource"""
    rule = ProductionMultiAZRule()

    resource = {
        'id': 'db-1',
        'environment': 'production',
        'multi_az': True
    }

    result = rule.validate(resource)

    assert result.status == ValidationStatus.PASSED


def test_multi_az_rule_skip_non_production():
    """Test multi-AZ rule skips non-production resources"""
    rule = ProductionMultiAZRule()

    resource = {
        'id': 'db-1',
        'environment': 'development',
        'multi_az': False
    }

    result = rule.validate(resource)

    assert result.status == ValidationStatus.SKIPPED
