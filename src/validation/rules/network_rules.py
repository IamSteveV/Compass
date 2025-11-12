"""Network and connectivity validation rules"""

from typing import Any, Dict, Optional
from ..rule import ArchitecturalRule
from ...models import ValidationResult, Severity, RuleCategory, ValidationStatus


class PublicSubnetIsolationRule(ArchitecturalRule):
    """Rule: Database tier must not be in public subnet"""

    def __init__(self):
        super().__init__()
        self.id = "NET-001"
        self.name = "Database Tier Public Subnet Isolation"
        self.severity = Severity.CRITICAL
        self.category = RuleCategory.SECURITY
        self.description = "Database tier must not be placed in public subnets"

    def validate(self, resource: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate database is not in public subnet"""
        if isinstance(resource, dict):
            resource_type = resource.get('type', '').lower()
            subnet_type = resource.get('subnet_type', '').lower()
            publicly_accessible = resource.get('publicly_accessible', False)
            resource_id = resource.get('id') or resource.get('name') or 'unknown'
        else:
            resource_type = getattr(resource, 'type', '').lower()
            subnet_type = getattr(resource, 'subnet_type', '').lower()
            publicly_accessible = getattr(resource, 'publicly_accessible', False)
            resource_id = getattr(resource, 'sys_id', None) or getattr(resource, 'name', 'unknown')

        # Check if this is a database
        is_database = any(db in resource_type for db in ['database', 'rds', 'db'])

        if not is_database:
            return self.create_result(
                ValidationStatus.SKIPPED,
                f"Not a database resource (type: {resource_type})",
                resource_id=resource_id
            )

        # Check if in public subnet or publicly accessible
        if subnet_type == 'public' or publicly_accessible:
            return self.create_result(
                ValidationStatus.FAILED,
                f"Database {resource_id} is in public subnet or publicly accessible",
                resource_id=resource_id,
                resource_type=resource_type,
                details={
                    "subnet_type": subnet_type,
                    "publicly_accessible": publicly_accessible
                }
            )

        return self.create_result(
            ValidationStatus.PASSED,
            f"Database {resource_id} is properly isolated in private subnet",
            resource_id=resource_id,
            resource_type=resource_type
        )


class LoadBalancerSSLRule(ArchitecturalRule):
    """Rule: Internet-facing load balancers must use SSL/TLS"""

    def __init__(self):
        super().__init__()
        self.id = "NET-002"
        self.name = "Load Balancer SSL/TLS Requirement"
        self.severity = Severity.HIGH
        self.category = RuleCategory.SECURITY
        self.description = "Internet-facing load balancers must use SSL/TLS"

    def validate(self, resource: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate load balancer SSL configuration"""
        if isinstance(resource, dict):
            resource_type = resource.get('type', '').lower()
            scheme = resource.get('scheme', '').lower()
            ssl_enabled = resource.get('ssl_enabled', False) or resource.get('https_enabled', False)
            listeners = resource.get('listeners', [])
            resource_id = resource.get('id') or resource.get('name') or 'unknown'
        else:
            resource_type = getattr(resource, 'type', '').lower()
            scheme = getattr(resource, 'scheme', '').lower()
            ssl_enabled = (getattr(resource, 'ssl_enabled', False) or
                         getattr(resource, 'https_enabled', False))
            listeners = getattr(resource, 'listeners', [])
            resource_id = getattr(resource, 'sys_id', None) or getattr(resource, 'name', 'unknown')

        # Check if this is a load balancer
        is_lb = any(lb in resource_type for lb in ['load_balancer', 'alb', 'elb', 'lb'])

        if not is_lb:
            return self.create_result(
                ValidationStatus.SKIPPED,
                f"Not a load balancer (type: {resource_type})",
                resource_id=resource_id
            )

        # Only check internet-facing load balancers
        is_internet_facing = scheme in ['internet-facing', 'public', 'external']

        if not is_internet_facing:
            return self.create_result(
                ValidationStatus.SKIPPED,
                f"Load balancer {resource_id} is not internet-facing",
                resource_id=resource_id
            )

        # Check SSL configuration
        has_ssl = ssl_enabled or any(
            listener.get('protocol', '').upper() in ['HTTPS', 'SSL', 'TLS']
            for listener in listeners
        )

        if not has_ssl:
            return self.create_result(
                ValidationStatus.FAILED,
                f"Internet-facing load balancer {resource_id} does not have SSL/TLS enabled",
                resource_id=resource_id,
                resource_type=resource_type
            )

        return self.create_result(
            ValidationStatus.PASSED,
            f"Load balancer {resource_id} has SSL/TLS enabled",
            resource_id=resource_id,
            resource_type=resource_type
        )


class VPCFlowLogsRule(ArchitecturalRule):
    """Rule: Production VPCs must have flow logs enabled"""

    def __init__(self):
        super().__init__()
        self.id = "NET-003"
        self.name = "VPC Flow Logs Requirement"
        self.severity = Severity.MEDIUM
        self.category = RuleCategory.COMPLIANCE
        self.description = "Production VPCs must have flow logs enabled for audit and security"

    def validate(self, resource: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate VPC flow logs are enabled"""
        if isinstance(resource, dict):
            resource_type = resource.get('type', '').lower()
            environment = resource.get('environment', '').lower()
            flow_logs_enabled = resource.get('flow_logs_enabled', False)
            resource_id = resource.get('id') or resource.get('name') or 'unknown'
        else:
            resource_type = getattr(resource, 'type', '').lower()
            environment = getattr(resource, 'environment', '').lower()
            flow_logs_enabled = getattr(resource, 'flow_logs_enabled', False)
            resource_id = getattr(resource, 'sys_id', None) or getattr(resource, 'name', 'unknown')

        # Check if this is a VPC/network
        is_vpc = any(net in resource_type for net in ['vpc', 'network', 'vnet'])

        if not is_vpc:
            return self.create_result(
                ValidationStatus.SKIPPED,
                f"Not a VPC/network resource (type: {resource_type})",
                resource_id=resource_id
            )

        is_production = environment in ['production', 'prod', 'prd']

        if not is_production:
            return self.create_result(
                ValidationStatus.SKIPPED,
                f"Not a production VPC (env: {environment})",
                resource_id=resource_id
            )

        if not flow_logs_enabled:
            return self.create_result(
                ValidationStatus.FAILED,
                f"Production VPC {resource_id} does not have flow logs enabled",
                resource_id=resource_id,
                resource_type=resource_type
            )

        return self.create_result(
            ValidationStatus.PASSED,
            f"VPC {resource_id} has flow logs enabled",
            resource_id=resource_id,
            resource_type=resource_type
        )
