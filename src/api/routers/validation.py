"""Validation endpoints"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from typing import Optional
import tempfile
import json
from pathlib import Path

from ...validation.engine import ValidationEngine
from ...validation.rule import get_rule_registry
from ...terraform_parser.parser import TerraformParser
from ...patterns.matcher import PatternMatcher
from ...models import ValidationReport

router = APIRouter()

# Initialize components
engine = ValidationEngine()
pattern_matcher = PatternMatcher()


def register_all_rules():
    """Register all validation rules"""
    from ...validation.rules.security_rules import (
        NoDirectWebToDatabaseRule,
        ProductionDatabaseEncryptionRule,
        DMZIsolationRule,
        ProductionBackupRule
    )
    from ...validation.rules.metadata_rules import (
        RequiredMetadataRule,
        ProductionDRTierRule
    )
    from ...validation.rules.technology_rules import (
        ApprovedDatabaseVersionRule,
        ApprovedInstanceTypeRule
    )
    from ...validation.rules.resilience_rules import (
        ProductionMultiAZRule,
        DatabaseBackupEnabledRule
    )

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


# Register rules on startup
register_all_rules()


@router.post("/terraform", response_model=ValidationReport)
async def validate_terraform_plan(
    file: UploadFile = File(..., description="Terraform plan JSON file")
):
    """
    Validate a Terraform plan against architectural standards.

    Args:
        file: Terraform plan JSON file (from terraform show -json)

    Returns:
        Validation report with results and pattern match
    """
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="File must be a JSON file")

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        # Parse Terraform plan
        parser = TerraformParser()
        plan = parser.parse_plan_file(tmp_path)
        validation_data = parser.get_resources_for_validation(plan)

        # Clean up temp file
        Path(tmp_path).unlink()

        # Match pattern
        resources = validation_data['resources']
        topology = validation_data.get('topology', [])

        pattern_match = pattern_matcher.match_pattern(resources, topology)

        # Run validation
        context = {
            **validation_data,
            'pattern_match': pattern_match
        }

        report = engine.validate(resources, context)

        return report

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.post("/cmdb", response_model=ValidationReport)
async def validate_cmdb_application(
    app_id: str = Body(..., description="Application name or sys_id", embed=True)
):
    """
    Validate a CMDB application against architectural standards.

    Args:
        app_id: Application name or sys_id from ServiceNow CMDB

    Returns:
        Validation report with results and pattern match
    """
    try:
        from ...cmdb.client import CMDBClient

        # Get application topology
        cmdb_client = CMDBClient()
        validation_data = cmdb_client.get_topology_for_validation(app_id)

        # Match pattern
        resources = validation_data['resources']
        topology = validation_data.get('topology', [])

        pattern_match = pattern_matcher.match_pattern(resources, topology)

        # Run validation
        context = {
            **validation_data,
            'pattern_match': pattern_match
        }

        report = engine.validate(resources, context)

        return report

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/rules")
async def list_validation_rules():
    """
    Get list of all validation rules.

    Returns:
        List of rules with metadata
    """
    registry = get_rule_registry()
    rules = registry.get_all_rules()

    return [
        {
            "id": rule.id,
            "name": rule.name,
            "severity": rule.severity.value,
            "category": rule.category.value,
            "description": rule.description
        }
        for rule in rules
    ]
