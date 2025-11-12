"""Resilience validation rules"""

from typing import Any, Dict, Optional
from ..rule import ArchitecturalRule
from ...models import ValidationResult, Severity, RuleCategory, ValidationStatus


class ProductionMultiAZRule(ArchitecturalRule):
    """Rule: Production must be multi-AZ"""

    def __init__(self):
        super().__init__()
        self.id = "RES-001"
        self.name = "Production Multi-AZ Requirement"
        self.severity = Severity.HIGH
        self.category = RuleCategory.RESILIENCE
        self.description = "Production deployments must be configured across multiple availability zones"

    def validate(self, resource: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate multi-AZ configuration for production resources"""
        if isinstance(resource, dict):
            environment = resource.get('environment', '').lower()
            multi_az = resource.get('multi_az', False)
            availability_zones = resource.get('availability_zones', [])
            resource_id = resource.get('id') or resource.get('name') or 'unknown'
            resource_type = resource.get('type', '')
        else:
            environment = getattr(resource, 'environment', '').lower()
            multi_az = getattr(resource, 'multi_az', False)
            availability_zones = getattr(resource, 'availability_zones', [])
            resource_id = getattr(resource, 'sys_id', None) or getattr(resource, 'name', 'unknown')
            resource_type = getattr(resource, 'type', '')

        is_production = environment in ['production', 'prod', 'prd']

        if not is_production:
            return self.create_result(
                ValidationStatus.SKIPPED,
                f"Not a production resource (env: {environment})",
                resource_id=resource_id
            )

        # Check multi-AZ configuration
        is_multi_az = multi_az or (isinstance(availability_zones, list) and len(availability_zones) > 1)

        if not is_multi_az:
            return self.create_result(
                ValidationStatus.FAILED,
                f"Production resource {resource_id} is not configured for multi-AZ deployment",
                resource_id=resource_id,
                resource_type=resource_type,
                details={
                    "multi_az": multi_az,
                    "availability_zones": availability_zones
                }
            )

        return self.create_result(
            ValidationStatus.PASSED,
            f"Production resource {resource_id} is configured for multi-AZ deployment",
            resource_id=resource_id,
            resource_type=resource_type,
            details={
                "availability_zones": availability_zones if availability_zones else "multi_az_enabled"
            }
        )


class DatabaseBackupEnabledRule(ArchitecturalRule):
    """Rule: Databases must have automated backups enabled"""

    def __init__(self):
        super().__init__()
        self.id = "RES-002"
        self.name = "Database Automated Backup Requirement"
        self.severity = Severity.HIGH
        self.category = RuleCategory.RESILIENCE
        self.description = "All databases must have automated backups enabled"

    def validate(self, resource: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate automated backup configuration for databases"""
        if isinstance(resource, dict):
            resource_type = resource.get('type', '').lower()
            backup_enabled = resource.get('backup_enabled', False)
            backup_retention = resource.get('backup_retention_days', 0)
            resource_id = resource.get('id') or resource.get('name') or 'unknown'
        else:
            resource_type = getattr(resource, 'type', '').lower()
            backup_enabled = getattr(resource, 'backup_enabled', False)
            backup_retention = getattr(resource, 'backup_retention_days', 0)
            resource_id = getattr(resource, 'sys_id', None) or getattr(resource, 'name', 'unknown')

        # Check if this is a database resource
        is_database = any(db_type in resource_type for db_type in
                         ['database', 'rds', 'postgres', 'mysql', 'oracle', 'sqlserver', 'db'])

        if not is_database:
            return self.create_result(
                ValidationStatus.SKIPPED,
                f"Not a database resource (type: {resource_type})",
                resource_id=resource_id
            )

        # Backup is considered enabled if either flag is True or retention > 0
        has_backup = backup_enabled or backup_retention > 0

        if not has_backup:
            return self.create_result(
                ValidationStatus.FAILED,
                f"Database {resource_id} does not have automated backups enabled",
                resource_id=resource_id,
                resource_type=resource_type
            )

        # Warn if retention is too short (less than 7 days)
        if backup_retention > 0 and backup_retention < 7:
            return self.create_result(
                ValidationStatus.WARNING,
                f"Database {resource_id} has backup retention of only {backup_retention} days (recommended: 7+)",
                resource_id=resource_id,
                resource_type=resource_type,
                details={"backup_retention_days": backup_retention}
            )

        return self.create_result(
            ValidationStatus.PASSED,
            f"Database {resource_id} has automated backups enabled",
            resource_id=resource_id,
            resource_type=resource_type,
            details={
                "backup_enabled": backup_enabled,
                "backup_retention_days": backup_retention
            }
        )
