"""Cost optimization validation rules"""

from typing import Any, Dict, Optional
from ..rule import ArchitecturalRule
from ...models import ValidationResult, Severity, RuleCategory, ValidationStatus


class UnusedResourceRule(ArchitecturalRule):
    """Rule: Warn about potentially unused resources"""

    def __init__(self):
        super().__init__()
        self.id = "COST-001"
        self.name = "Unused Resource Detection"
        self.severity = Severity.LOW
        self.category = RuleCategory.COMPLIANCE
        self.description = "Detect potentially unused resources to optimize costs"

    def validate(self, resource: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Check for unused resources based on various indicators"""
        if isinstance(resource, dict):
            resource_id = resource.get('id') or resource.get('name') or 'unknown'
            resource_type = resource.get('type', '')

            # Check various unused indicators
            is_unused = (
                resource.get('status') in ['stopped', 'terminated', 'unused'] or
                resource.get('attached', True) == False or
                resource.get('connections', 0) == 0
            )

            last_used = resource.get('last_used')
            cpu_utilization = resource.get('cpu_utilization', 100)
        else:
            resource_id = getattr(resource, 'sys_id', None) or getattr(resource, 'name', 'unknown')
            resource_type = getattr(resource, 'type', '')
            is_unused = getattr(resource, 'status', '') in ['stopped', 'terminated', 'unused']
            last_used = getattr(resource, 'last_used', None)
            cpu_utilization = getattr(resource, 'cpu_utilization', 100)

        warnings = []

        if is_unused:
            warnings.append("Resource appears to be unused or unattached")

        if cpu_utilization < 5:
            warnings.append(f"Very low CPU utilization ({cpu_utilization}%)")

        if warnings:
            return self.create_result(
                ValidationStatus.WARNING,
                f"Resource {resource_id} may be unused: {'; '.join(warnings)}",
                resource_id=resource_id,
                resource_type=resource_type,
                details={"warnings": warnings}
            )

        return self.create_result(
            ValidationStatus.PASSED,
            f"Resource {resource_id} appears to be in use",
            resource_id=resource_id,
            resource_type=resource_type
        )


class OversizedInstanceRule(ArchitecturalRule):
    """Rule: Warn about potentially oversized instances"""

    def __init__(self):
        super().__init__()
        self.id = "COST-002"
        self.name = "Oversized Instance Detection"
        self.severity = Severity.LOW
        self.category = RuleCategory.COMPLIANCE
        self.description = "Detect instances that may be oversized for their workload"

    def validate(self, resource: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Check if instance is oversized based on utilization"""
        if isinstance(resource, dict):
            resource_type = resource.get('type', '').lower()
            resource_id = resource.get('id') or resource.get('name') or 'unknown'
            instance_type = resource.get('instance_type', '')
            cpu_utilization = resource.get('cpu_utilization', 100)
            memory_utilization = resource.get('memory_utilization', 100)
        else:
            resource_type = getattr(resource, 'type', '').lower()
            resource_id = getattr(resource, 'sys_id', None) or getattr(resource, 'name', 'unknown')
            instance_type = getattr(resource, 'instance_type', '')
            cpu_utilization = getattr(resource, 'cpu_utilization', 100)
            memory_utilization = getattr(resource, 'memory_utilization', 100)

        # Only check compute resources
        is_compute = any(comp in resource_type for comp in ['server', 'instance', 'vm', 'compute'])

        if not is_compute:
            return self.create_result(
                ValidationStatus.SKIPPED,
                f"Not a compute resource (type: {resource_type})",
                resource_id=resource_id
            )

        # Check if instance is oversized (low utilization)
        if cpu_utilization < 20 and memory_utilization < 30:
            # Check if it's a large instance
            is_large = any(size in instance_type.lower() for size in ['xlarge', '2xlarge', '4xlarge'])

            if is_large:
                return self.create_result(
                    ValidationStatus.WARNING,
                    f"Instance {resource_id} ({instance_type}) may be oversized - "
                    f"CPU: {cpu_utilization}%, Memory: {memory_utilization}%",
                    resource_id=resource_id,
                    resource_type=resource_type,
                    details={
                        "instance_type": instance_type,
                        "cpu_utilization": cpu_utilization,
                        "memory_utilization": memory_utilization,
                        "recommendation": "Consider downsizing to reduce costs"
                    }
                )

        return self.create_result(
            ValidationStatus.PASSED,
            f"Instance {resource_id} appears appropriately sized",
            resource_id=resource_id,
            resource_type=resource_type
        )
