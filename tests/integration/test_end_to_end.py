"""End-to-end integration tests"""

import pytest
import json
from pathlib import Path

from src.test_data.generators import (
    generate_sample_terraform_plan,
    generate_sample_resources,
    generate_sample_topology
)
from src.terraform_parser.parser import TerraformParser
from src.validation.engine import ValidationEngine
from src.validation.rule import get_rule_registry
from src.patterns.matcher import PatternMatcher
from src.patterns.library import PatternLibrary

# Import all validation rules at module level
from src.validation.rules.security_rules import (
    NoDirectWebToDatabaseRule,
    ProductionDatabaseEncryptionRule,
    DMZIsolationRule,
    ProductionBackupRule
)
from src.validation.rules.metadata_rules import (
    RequiredMetadataRule,
    ProductionDRTierRule
)
from src.validation.rules.technology_rules import (
    ApprovedDatabaseVersionRule,
    ApprovedInstanceTypeRule
)
from src.validation.rules.resilience_rules import (
    ProductionMultiAZRule,
    DatabaseBackupEnabledRule
)
from src.validation.rules.network_rules import (
    PublicSubnetIsolationRule,
    LoadBalancerSSLRule,
    VPCFlowLogsRule
)
from src.validation.rules.cost_rules import (
    UnusedResourceRule,
    OversizedInstanceRule
)


def register_test_rules():
    """Register all validation rules for testing"""
    registry = get_rule_registry()
    registry.clear()

    # Register all rules
    registry.register(NoDirectWebToDatabaseRule())
    registry.register(ProductionDatabaseEncryptionRule())
    registry.register(DMZIsolationRule())
    registry.register(ProductionBackupRule())
    registry.register(RequiredMetadataRule())
    registry.register(ProductionDRTierRule())
    registry.register(ApprovedDatabaseVersionRule())
    registry.register(ApprovedInstanceTypeRule())
    registry.register(ProductionMultiAZRule())
    registry.register(DatabaseBackupEnabledRule())
    registry.register(PublicSubnetIsolationRule())
    registry.register(LoadBalancerSSLRule())
    registry.register(VPCFlowLogsRule())
    registry.register(UnusedResourceRule())
    registry.register(OversizedInstanceRule())


@pytest.mark.integration
def test_full_terraform_validation_workflow(tmp_path):
    """Test complete workflow from Terraform plan to validation report"""
    # Generate sample Terraform plan
    plan_data = generate_sample_terraform_plan("3-tier")

    # Save to file
    plan_file = tmp_path / "test_plan.json"
    with open(plan_file, 'w') as f:
        json.dump(plan_data, f)

    # Parse Terraform plan
    parser = TerraformParser()
    plan = parser.parse_plan_file(str(plan_file))

    assert plan is not None
    assert len(plan.resources) > 0

    # Get validation data
    validation_data = parser.get_resources_for_validation(plan)
    resources = validation_data['resources']
    topology = validation_data.get('topology', [])

    assert len(resources) > 0

    # Register rules
    register_test_rules()

    # Run validation
    engine = ValidationEngine()
    report = engine.validate(resources, validation_data)

    assert report is not None
    assert report.summary.total_rules > 0
    assert report.overall_status in ["passed", "failed", "warning"]


@pytest.mark.integration
def test_pattern_matching_workflow(patterns_dir):
    """Test pattern matching workflow"""
    # Generate sample resources
    resources = generate_sample_resources("3-tier")
    topology = generate_sample_topology(resources)

    # Load patterns
    library = PatternLibrary(repository_path=str(patterns_dir))
    matcher = PatternMatcher(library)

    # Match pattern
    pattern_match = matcher.match_pattern(resources, topology)

    assert pattern_match is not None
    assert pattern_match.pattern_id is not None
    assert pattern_match.similarity_score >= 0.0
    assert pattern_match.similarity_score <= 1.0


@pytest.mark.integration
def test_validation_with_pattern_matching(patterns_dir):
    """Test validation workflow with pattern matching"""
    # Generate sample resources
    resources = generate_sample_resources("3-tier")
    topology = generate_sample_topology(resources)

    # Load patterns and match
    library = PatternLibrary(repository_path=str(patterns_dir))
    matcher = PatternMatcher(library)
    pattern_match = matcher.match_pattern(resources, topology)

    # Register rules and validate
    register_test_rules()
    engine = ValidationEngine()

    context = {
        'resources': resources,
        'topology': topology,
        'pattern_match': pattern_match,
        'source_type': 'test',
        'source_identifier': 'integration_test'
    }

    report = engine.validate(resources, context)

    assert report is not None
    assert report.pattern_match is not None
    assert report.approval_track is not None


@pytest.mark.integration
def test_multiple_pattern_types():
    """Test validation for different pattern types"""
    pattern_types = ["3-tier", "microservices", "ha-database"]

    register_test_rules()
    engine = ValidationEngine()

    for pattern_type in pattern_types:
        resources = generate_sample_resources(pattern_type)
        topology = generate_sample_topology(resources)

        context = {
            'resources': resources,
            'topology': topology,
            'source_type': 'test',
            'source_identifier': f'test_{pattern_type}'
        }

        report = engine.validate(resources, context)

        assert report is not None
        assert report.summary.total_rules > 0
        # Different patterns may have different compliance scores
        assert 0.0 <= report.summary.compliance_score <= 1.0
