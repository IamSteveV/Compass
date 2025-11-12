"""Base classes and registry for validation rules"""

from abc import ABC, abstractmethod
from typing import List, Any, Dict, Optional
from ..models import ValidationResult, Severity, RuleCategory, ValidationStatus


class ArchitecturalRule(ABC):
    """Base class for all architectural validation rules"""

    def __init__(self):
        self.id: str = ""
        self.name: str = ""
        self.severity: Severity = Severity.MEDIUM
        self.category: RuleCategory = RuleCategory.COMPLIANCE
        self.description: str = ""

    @abstractmethod
    def validate(self, resource: Any, context: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """
        Validate a resource against this rule.

        Args:
            resource: The resource to validate (can be CMDB CI, Terraform resource, etc.)
            context: Additional context for validation (topology, related resources, etc.)

        Returns:
            ValidationResult with the outcome of the validation
        """
        pass

    def create_result(
        self,
        status: ValidationStatus,
        message: str,
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """Helper method to create a ValidationResult"""
        return ValidationResult(
            rule_id=self.id,
            rule_name=self.name,
            severity=self.severity,
            category=self.category,
            status=status,
            message=message,
            resource_id=resource_id,
            resource_type=resource_type,
            details=details or {}
        )


class RuleRegistry:
    """Registry for all validation rules"""

    def __init__(self):
        self._rules: Dict[str, ArchitecturalRule] = {}

    def register(self, rule: ArchitecturalRule) -> None:
        """Register a new validation rule"""
        if rule.id in self._rules:
            raise ValueError(f"Rule with ID '{rule.id}' is already registered")
        self._rules[rule.id] = rule

    def get_rule(self, rule_id: str) -> Optional[ArchitecturalRule]:
        """Get a rule by ID"""
        return self._rules.get(rule_id)

    def get_all_rules(self) -> List[ArchitecturalRule]:
        """Get all registered rules"""
        return list(self._rules.values())

    def get_rules_by_category(self, category: RuleCategory) -> List[ArchitecturalRule]:
        """Get all rules in a specific category"""
        return [rule for rule in self._rules.values() if rule.category == category]

    def get_rules_by_severity(self, severity: Severity) -> List[ArchitecturalRule]:
        """Get all rules with a specific severity"""
        return [rule for rule in self._rules.values() if rule.severity == severity]

    def unregister(self, rule_id: str) -> None:
        """Unregister a rule"""
        if rule_id in self._rules:
            del self._rules[rule_id]

    def clear(self) -> None:
        """Clear all registered rules"""
        self._rules.clear()

    def __len__(self) -> int:
        return len(self._rules)

    def __contains__(self, rule_id: str) -> bool:
        return rule_id in self._rules


# Global rule registry instance
_global_registry: Optional[RuleRegistry] = None


def get_rule_registry() -> RuleRegistry:
    """Get the global rule registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = RuleRegistry()
    return _global_registry


def register_rule(rule: ArchitecturalRule) -> None:
    """Convenience function to register a rule in the global registry"""
    get_rule_registry().register(rule)
