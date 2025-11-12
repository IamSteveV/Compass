"""Data models for the architecture validation system"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Validation rule severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RuleCategory(str, Enum):
    """Categories of validation rules"""
    SECURITY = "security"
    RESILIENCE = "resilience"
    COMPLIANCE = "compliance"
    TECHNOLOGY = "technology"
    METADATA = "metadata"
    NETWORK = "network"


class ValidationStatus(str, Enum):
    """Status of a validation check"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class PatternStatus(str, Enum):
    """Approval status of patterns"""
    DRAFT = "draft"
    APPROVED = "approved"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class ApprovalTrack(str, Enum):
    """Approval routing tracks based on pattern match"""
    FAST_TRACK = "fast_track"
    STANDARD_REVIEW = "standard_review"
    FULL_REVIEW = "full_review"


class ValidationResult(BaseModel):
    """Result of a single validation rule check"""
    rule_id: str
    rule_name: str
    severity: Severity
    category: RuleCategory
    status: ValidationStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    resource_id: Optional[str] = None
    resource_type: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationReport(BaseModel):
    """Complete validation report for an infrastructure"""
    id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_type: str  # "terraform" or "cmdb"
    source_identifier: str  # plan file name or CMDB app ID
    results: List[ValidationResult]
    pattern_match: Optional['PatternMatch'] = None
    approval_track: Optional[ApprovalTrack] = None
    overall_status: ValidationStatus
    summary: 'ValidationSummary'


class ValidationSummary(BaseModel):
    """Summary statistics for a validation report"""
    total_rules: int
    passed: int
    failed: int
    warnings: int
    skipped: int
    critical_violations: int
    high_violations: int
    medium_violations: int
    low_violations: int
    compliance_score: float  # 0.0 to 1.0


class Component(BaseModel):
    """Infrastructure component definition"""
    name: str
    type: str  # compute, database, network, storage, etc.
    tier: Optional[str] = None  # web, app, database, etc.
    properties: Dict[str, Any] = Field(default_factory=dict)
    minimum_instances: Optional[int] = None
    load_balanced: Optional[bool] = None


class NetworkConnection(BaseModel):
    """Network connection between components"""
    source: str  # component name
    target: str  # component name
    protocol: Optional[str] = None
    port: Optional[int] = None
    encrypted: Optional[bool] = None


class ArchitectureConstraint(BaseModel):
    """Architectural constraint or rule"""
    description: str
    type: str  # "must", "must_not", "should", "should_not"


class ArchitectureSpec(BaseModel):
    """Architecture specification within a pattern"""
    components: List[Component]
    network_topology: List[NetworkConnection]
    constraints: List[ArchitectureConstraint] = Field(default_factory=list)


class TerraformImplementation(BaseModel):
    """Terraform implementation details for a pattern"""
    terraform_module: str
    required_variables: List[str]
    optional_variables: List[str] = Field(default_factory=list)
    example_usage: Optional[str] = None


class PatternMetadata(BaseModel):
    """Metadata for an architecture pattern"""
    id: str
    name: str
    version: str
    status: PatternStatus
    owner: str
    approval_date: Optional[datetime] = None
    compliance_tags: List[str] = Field(default_factory=list)
    description: str


class Pattern(BaseModel):
    """Complete architecture pattern definition"""
    metadata: PatternMetadata
    architecture: ArchitectureSpec
    implementation: TerraformImplementation
    documentation: Optional[Dict[str, str]] = None  # URLs to diagrams, ADRs, etc.


class PatternMatch(BaseModel):
    """Result of pattern matching analysis"""
    pattern_id: str
    pattern_name: str
    similarity_score: float  # 0.0 to 1.0
    deviations: List[str] = Field(default_factory=list)
    matched_components: List[str] = Field(default_factory=list)
    missing_components: List[str] = Field(default_factory=list)
    extra_components: List[str] = Field(default_factory=list)


class CMDBConfigurationItem(BaseModel):
    """ServiceNow CMDB Configuration Item"""
    sys_id: str
    name: str
    type: str  # cmdb_ci_server, cmdb_ci_database, etc.
    environment: Optional[str] = None
    tier: Optional[str] = None
    business_owner: Optional[str] = None
    technical_owner: Optional[str] = None
    data_classification: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)


class CMDBRelationship(BaseModel):
    """Relationship between CMDB Configuration Items"""
    parent_id: str
    child_id: str
    relationship_type: str


class CMDBApplication(BaseModel):
    """CMDB Application with related CIs"""
    sys_id: str
    name: str
    description: Optional[str] = None
    configuration_items: List[CMDBConfigurationItem] = Field(default_factory=list)
    relationships: List[CMDBRelationship] = Field(default_factory=list)


class TerraformResource(BaseModel):
    """Terraform resource from plan"""
    address: str
    type: str
    name: str
    provider: str
    values: Dict[str, Any] = Field(default_factory=dict)
    change_action: Optional[str] = None  # create, update, delete, no-op


class TerraformPlan(BaseModel):
    """Parsed Terraform plan"""
    terraform_version: str
    resources: List[TerraformResource]
    variables: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)


# Update forward references
ValidationReport.model_rebuild()
