"""Technology validation rules"""

from typing import Any, Dict, Optional, List
from ..rule import ArchitecturalRule
from ...models import ValidationResult, Severity, RuleCategory, ValidationStatus


class ApprovedDatabaseVersionRule(ArchitecturalRule):
    """Rule: Only approved database versions"""

    APPROVED_VERSIONS = {
        'postgresql': ['14', '15', '16'],
        'postgres': ['14', '15', '16'],
        'mysql': ['8.0', '8.1'],
        'oracle': ['19c', '21c', '23c'],
        'sqlserver': ['2019', '2022'],
        'mssql': ['2019', '2022']
    }

    def __init__(self):
        super().__init__()
        self.id = "TECH-001"
        self.name = "Approved Database Versions"
        self.severity = Severity.MEDIUM
        self.category = RuleCategory.TECHNOLOGY
        self.description = "Only approved database versions are allowed"

    def validate(self, resource: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate database version against approved list"""
        if isinstance(resource, dict):
            resource_type = resource.get('type', '').lower()
            version = resource.get('version') or resource.get('engine_version')
            resource_id = resource.get('id') or resource.get('name') or 'unknown'
        else:
            resource_type = getattr(resource, 'type', '').lower()
            version = getattr(resource, 'version', None) or getattr(resource, 'engine_version', None)
            resource_id = getattr(resource, 'sys_id', None) or getattr(resource, 'name', 'unknown')

        # Check if this is a database resource
        db_type = None
        for db in self.APPROVED_VERSIONS.keys():
            if db in resource_type:
                db_type = db
                break

        if not db_type:
            return self.create_result(
                ValidationStatus.SKIPPED,
                f"Not a database resource (type: {resource_type})",
                resource_id=resource_id
            )

        if not version:
            return self.create_result(
                ValidationStatus.WARNING,
                f"Database {resource_id} does not specify version",
                resource_id=resource_id,
                resource_type=resource_type
            )

        # Extract major version for comparison
        version_str = str(version)
        approved_versions = self.APPROVED_VERSIONS[db_type]

        # Check if version is approved
        version_approved = any(
            version_str.startswith(approved) for approved in approved_versions
        )

        if not version_approved:
            return self.create_result(
                ValidationStatus.FAILED,
                f"Database {resource_id} uses unapproved version {version}. "
                f"Approved versions: {', '.join(approved_versions)}",
                resource_id=resource_id,
                resource_type=resource_type,
                details={
                    "current_version": version,
                    "approved_versions": approved_versions
                }
            )

        return self.create_result(
            ValidationStatus.PASSED,
            f"Database {resource_id} uses approved version {version}",
            resource_id=resource_id,
            resource_type=resource_type,
            details={"version": version}
        )


class ApprovedInstanceTypeRule(ArchitecturalRule):
    """Rule: Only approved instance types per tier"""

    APPROVED_INSTANCE_TYPES = {
        'web': ['t3.medium', 't3.large', 'c5.large', 'c5.xlarge'],
        'app': ['t3.large', 't3.xlarge', 'c5.xlarge', 'c5.2xlarge', 'm5.xlarge', 'm5.2xlarge'],
        'database': ['r5.large', 'r5.xlarge', 'r5.2xlarge', 'r5.4xlarge'],
        'db': ['r5.large', 'r5.xlarge', 'r5.2xlarge', 'r5.4xlarge']
    }

    def __init__(self):
        super().__init__()
        self.id = "TECH-002"
        self.name = "Approved Instance Types"
        self.severity = Severity.LOW
        self.category = RuleCategory.TECHNOLOGY
        self.description = "Only approved instance types per tier are allowed"

    def validate(self, resource: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate instance type against approved list for tier"""
        if isinstance(resource, dict):
            tier = resource.get('tier', '').lower()
            instance_type = resource.get('instance_type') or resource.get('size')
            resource_id = resource.get('id') or resource.get('name') or 'unknown'
            resource_type = resource.get('type', '')
        else:
            tier = getattr(resource, 'tier', '').lower()
            instance_type = getattr(resource, 'instance_type', None) or getattr(resource, 'size', None)
            resource_id = getattr(resource, 'sys_id', None) or getattr(resource, 'name', 'unknown')
            resource_type = getattr(resource, 'type', '')

        # Check if this is a compute resource
        is_compute = any(comp_type in str(resource_type).lower() for comp_type in
                        ['server', 'instance', 'vm', 'compute'])

        if not is_compute:
            return self.create_result(
                ValidationStatus.SKIPPED,
                f"Not a compute resource (type: {resource_type})",
                resource_id=resource_id
            )

        if not tier:
            return self.create_result(
                ValidationStatus.WARNING,
                f"Resource {resource_id} does not specify tier",
                resource_id=resource_id,
                resource_type=resource_type
            )

        if tier not in self.APPROVED_INSTANCE_TYPES:
            return self.create_result(
                ValidationStatus.SKIPPED,
                f"No approved instance types defined for tier: {tier}",
                resource_id=resource_id
            )

        if not instance_type:
            return self.create_result(
                ValidationStatus.WARNING,
                f"Resource {resource_id} does not specify instance type",
                resource_id=resource_id,
                resource_type=resource_type
            )

        approved_types = self.APPROVED_INSTANCE_TYPES[tier]

        if instance_type not in approved_types:
            return self.create_result(
                ValidationStatus.FAILED,
                f"Instance {resource_id} uses unapproved type {instance_type} for {tier} tier. "
                f"Approved types: {', '.join(approved_types)}",
                resource_id=resource_id,
                resource_type=resource_type,
                details={
                    "current_type": instance_type,
                    "tier": tier,
                    "approved_types": approved_types
                }
            )

        return self.create_result(
            ValidationStatus.PASSED,
            f"Instance {resource_id} uses approved type {instance_type} for {tier} tier",
            resource_id=resource_id,
            resource_type=resource_type,
            details={"instance_type": instance_type, "tier": tier}
        )
