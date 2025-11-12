"""Security validation rules"""

from typing import Any, Dict, Optional
from ..rule import ArchitecturalRule
from ...models import ValidationResult, Severity, RuleCategory, ValidationStatus


class NoDirectWebToDatabaseRule(ArchitecturalRule):
    """Rule: No direct web-to-database connections"""

    def __init__(self):
        super().__init__()
        self.id = "SEC-001"
        self.name = "No Direct Web-to-Database Connections"
        self.severity = Severity.CRITICAL
        self.category = RuleCategory.SECURITY
        self.description = "Web tier must not directly connect to database tier"

    def validate(self, resource: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate that web tier doesn't connect directly to database tier.
        Expects context to contain 'topology' with network connections.
        """
        if not context or 'topology' not in context:
            return self.create_result(
                ValidationStatus.SKIPPED,
                "No topology information available for validation"
            )

        topology = context['topology']
        violations = []

        # Check each connection
        for connection in topology:
            source_tier = connection.get('source_tier', '').lower()
            target_tier = connection.get('target_tier', '').lower()

            if source_tier == 'web' and target_tier in ['database', 'db', 'data']:
                violations.append(
                    f"Direct connection from {connection.get('source')} (web) to "
                    f"{connection.get('target')} (database)"
                )

        if violations:
            return self.create_result(
                ValidationStatus.FAILED,
                f"Found {len(violations)} direct web-to-database connection(s)",
                details={"violations": violations}
            )

        return self.create_result(
            ValidationStatus.PASSED,
            "No direct web-to-database connections found"
        )


class ProductionDatabaseEncryptionRule(ArchitecturalRule):
    """Rule: Production databases must be encrypted"""

    def __init__(self):
        super().__init__()
        self.id = "SEC-002"
        self.name = "Production Database Encryption Required"
        self.severity = Severity.CRITICAL
        self.category = RuleCategory.SECURITY
        self.description = "All production databases must have encryption enabled"

    def validate(self, resource: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate database encryption for production resources"""
        # Handle different resource types
        if isinstance(resource, dict):
            resource_type = resource.get('type', '').lower()
            environment = resource.get('environment', '').lower()
            encrypted = resource.get('encrypted', False)
            resource_id = resource.get('id') or resource.get('name') or 'unknown'
        else:
            # Handle object-based resources
            resource_type = getattr(resource, 'type', '').lower()
            environment = getattr(resource, 'environment', '').lower()
            encrypted = getattr(resource, 'encrypted', False)
            resource_id = getattr(resource, 'sys_id', None) or getattr(resource, 'name', 'unknown')

        # Check if this is a production database
        is_database = any(db_type in resource_type for db_type in
                         ['database', 'rds', 'postgres', 'mysql', 'oracle', 'sqlserver', 'db'])
        is_production = environment in ['production', 'prod', 'prd']

        if not is_database or not is_production:
            return self.create_result(
                ValidationStatus.SKIPPED,
                f"Not a production database (type: {resource_type}, env: {environment})",
                resource_id=resource_id
            )

        if not encrypted:
            return self.create_result(
                ValidationStatus.FAILED,
                f"Production database {resource_id} is not encrypted",
                resource_id=resource_id,
                resource_type=resource_type
            )

        return self.create_result(
            ValidationStatus.PASSED,
            f"Production database {resource_id} is encrypted",
            resource_id=resource_id,
            resource_type=resource_type
        )


class DMZIsolationRule(ArchitecturalRule):
    """Rule: DMZ servers cannot connect to internal database"""

    def __init__(self):
        super().__init__()
        self.id = "SEC-003"
        self.name = "DMZ Isolation from Internal Database"
        self.severity = Severity.CRITICAL
        self.category = RuleCategory.SECURITY
        self.description = "DMZ servers must not have direct access to internal database tier"

    def validate(self, resource: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate DMZ isolation"""
        if not context or 'topology' not in context:
            return self.create_result(
                ValidationStatus.SKIPPED,
                "No topology information available for validation"
            )

        topology = context['topology']
        violations = []

        # Check each connection
        for connection in topology:
            source_zone = connection.get('source_zone', '').lower()
            target_zone = connection.get('target_zone', '').lower()
            target_tier = connection.get('target_tier', '').lower()

            # DMZ should not connect to internal database
            if source_zone == 'dmz' and target_zone == 'internal' and target_tier in ['database', 'db']:
                violations.append(
                    f"DMZ server {connection.get('source')} connects to "
                    f"internal database {connection.get('target')}"
                )

        if violations:
            return self.create_result(
                ValidationStatus.FAILED,
                f"Found {len(violations)} DMZ to internal database connection(s)",
                details={"violations": violations}
            )

        return self.create_result(
            ValidationStatus.PASSED,
            "DMZ properly isolated from internal database tier"
        )


class ProductionBackupRule(ArchitecturalRule):
    """Rule: All production servers must have backup relationships"""

    def __init__(self):
        super().__init__()
        self.id = "SEC-004"
        self.name = "Production Server Backup Requirement"
        self.severity = Severity.HIGH
        self.category = RuleCategory.RESILIENCE
        self.description = "All production servers must have backup configured"

    def validate(self, resource: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate backup configuration for production servers"""
        if isinstance(resource, dict):
            environment = resource.get('environment', '').lower()
            resource_type = resource.get('type', '').lower()
            has_backup = resource.get('backup_enabled', False)
            resource_id = resource.get('id') or resource.get('name') or 'unknown'
        else:
            environment = getattr(resource, 'environment', '').lower()
            resource_type = getattr(resource, 'type', '').lower()
            has_backup = getattr(resource, 'backup_enabled', False)
            resource_id = getattr(resource, 'sys_id', None) or getattr(resource, 'name', 'unknown')

        is_production = environment in ['production', 'prod', 'prd']
        is_server = any(srv_type in resource_type for srv_type in
                       ['server', 'instance', 'vm', 'compute', 'database'])

        if not is_production or not is_server:
            return self.create_result(
                ValidationStatus.SKIPPED,
                f"Not a production server (type: {resource_type}, env: {environment})",
                resource_id=resource_id
            )

        # Check for backup relationships in context
        if context and 'relationships' in context:
            relationships = context['relationships']
            has_backup_rel = any(
                rel.get('relationship_type') == 'backed_up_by' and
                rel.get('parent_id') == resource_id
                for rel in relationships
            )
            has_backup = has_backup or has_backup_rel

        if not has_backup:
            return self.create_result(
                ValidationStatus.FAILED,
                f"Production server {resource_id} does not have backup configured",
                resource_id=resource_id,
                resource_type=resource_type
            )

        return self.create_result(
            ValidationStatus.PASSED,
            f"Production server {resource_id} has backup configured",
            resource_id=resource_id,
            resource_type=resource_type
        )
