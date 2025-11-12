"""Metadata validation rules"""

from typing import Any, Dict, Optional, List
from ..rule import ArchitecturalRule
from ...models import ValidationResult, Severity, RuleCategory, ValidationStatus


class RequiredMetadataRule(ArchitecturalRule):
    """Rule: All CIs must have required metadata fields"""

    REQUIRED_FIELDS = ['business_owner', 'technical_owner', 'data_classification']

    def __init__(self):
        super().__init__()
        self.id = "META-001"
        self.name = "Required Metadata Fields"
        self.severity = Severity.HIGH
        self.category = RuleCategory.METADATA
        self.description = f"All CIs must have: {', '.join(self.REQUIRED_FIELDS)}"

    def validate(self, resource: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate required metadata fields"""
        # Extract fields from resource
        if isinstance(resource, dict):
            resource_id = resource.get('id') or resource.get('name') or resource.get('sys_id') or 'unknown'
            fields = resource
        else:
            resource_id = getattr(resource, 'sys_id', None) or getattr(resource, 'name', 'unknown')
            fields = resource.__dict__ if hasattr(resource, '__dict__') else {}

        # Check for missing required fields
        missing_fields = []
        for field in self.REQUIRED_FIELDS:
            value = fields.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                missing_fields.append(field)

        if missing_fields:
            return self.create_result(
                ValidationStatus.FAILED,
                f"Resource {resource_id} is missing required metadata: {', '.join(missing_fields)}",
                resource_id=resource_id,
                details={"missing_fields": missing_fields}
            )

        return self.create_result(
            ValidationStatus.PASSED,
            f"Resource {resource_id} has all required metadata fields",
            resource_id=resource_id
        )


class ProductionDRTierRule(ArchitecturalRule):
    """Rule: Production CIs require DR tier designation"""

    def __init__(self):
        super().__init__()
        self.id = "META-002"
        self.name = "Production DR Tier Designation"
        self.severity = Severity.MEDIUM
        self.category = RuleCategory.METADATA
        self.description = "Production CIs must have DR (Disaster Recovery) tier designation"

    def validate(self, resource: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate DR tier for production resources"""
        if isinstance(resource, dict):
            environment = resource.get('environment', '').lower()
            dr_tier = resource.get('dr_tier') or resource.get('disaster_recovery_tier')
            resource_id = resource.get('id') or resource.get('name') or resource.get('sys_id') or 'unknown'
        else:
            environment = getattr(resource, 'environment', '').lower()
            dr_tier = (getattr(resource, 'dr_tier', None) or
                      getattr(resource, 'disaster_recovery_tier', None))
            resource_id = getattr(resource, 'sys_id', None) or getattr(resource, 'name', 'unknown')

        is_production = environment in ['production', 'prod', 'prd']

        if not is_production:
            return self.create_result(
                ValidationStatus.SKIPPED,
                f"Not a production resource (env: {environment})",
                resource_id=resource_id
            )

        if not dr_tier or (isinstance(dr_tier, str) and not dr_tier.strip()):
            return self.create_result(
                ValidationStatus.FAILED,
                f"Production resource {resource_id} does not have DR tier designation",
                resource_id=resource_id
            )

        return self.create_result(
            ValidationStatus.PASSED,
            f"Production resource {resource_id} has DR tier: {dr_tier}",
            resource_id=resource_id,
            details={"dr_tier": dr_tier}
        )
