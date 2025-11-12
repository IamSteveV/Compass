# API Documentation

## Base URL

```
http://localhost:5000/api
```

## Interactive Documentation

OpenAPI/Swagger UI: http://localhost:5000/api/docs
ReDoc: http://localhost:5000/api/redoc

## Authentication

Currently no authentication required (POC). In production, implement API keys or OAuth2.

## Endpoints

### Pattern Management

#### List All Patterns

```http
GET /api/patterns/
```

**Query Parameters**:
- `status` (optional): Filter by status (approved, draft, deprecated)

**Response**:
```json
[
  {
    "metadata": {
      "id": "PAT-001",
      "name": "Standard 3-Tier Web Application",
      "version": "1.0",
      "status": "approved",
      "owner": "Enterprise Architecture Team",
      "description": "..."
    },
    "architecture": {
      "components": [...],
      "network_topology": [...],
      "constraints": [...]
    },
    "implementation": {...}
  }
]
```

#### Get Pattern by ID

```http
GET /api/patterns/{pattern_id}
```

**Path Parameters**:
- `pattern_id`: Pattern identifier (e.g., PAT-001)

**Response**: Single pattern object (same structure as above)

**Error Responses**:
- `404 Not Found`: Pattern doesn't exist

#### Get Pattern Diagram

```http
GET /api/patterns/{pattern_id}/diagram
```

**Response**: Image file (PNG/SVG)

**Error Responses**:
- `404 Not Found`: Diagram not found

#### Search Patterns

```http
GET /api/patterns/search/{query}
```

**Path Parameters**:
- `query`: Search string

**Response**: Array of matching patterns

#### Reload Patterns

```http
POST /api/patterns/reload
```

**Response**:
```json
{
  "status": "success",
  "patterns_loaded": 3
}
```

---

### Validation

#### Validate Terraform Plan

```http
POST /api/validate/terraform
```

**Request**:
- Content-Type: `multipart/form-data`
- Body: Form data with `file` field containing JSON plan

**Example**:
```bash
curl -X POST http://localhost:5000/api/validate/terraform \
  -F "file=@tfplan.json"
```

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:00Z",
  "source_type": "terraform",
  "source_identifier": "Terraform Plan v1.5.0",
  "results": [
    {
      "rule_id": "SEC-001",
      "rule_name": "No Direct Web-to-Database Connections",
      "severity": "critical",
      "category": "security",
      "status": "passed",
      "message": "No direct web-to-database connections found",
      "timestamp": "2024-01-15T10:30:05Z"
    }
  ],
  "pattern_match": {
    "pattern_id": "PAT-001",
    "pattern_name": "Standard 3-Tier Web Application",
    "similarity_score": 0.92,
    "deviations": [
      "Missing component: load_balancer",
      "Single-AZ deployment (pattern requires multi-AZ)"
    ],
    "matched_components": ["web_tier", "app_tier", "database"],
    "missing_components": ["load_balancer"],
    "extra_components": []
  },
  "approval_track": "standard_review",
  "overall_status": "passed",
  "summary": {
    "total_rules": 10,
    "passed": 8,
    "failed": 0,
    "warnings": 2,
    "skipped": 0,
    "critical_violations": 0,
    "high_violations": 0,
    "medium_violations": 0,
    "low_violations": 0,
    "compliance_score": 0.8
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid JSON or file format
- `500 Internal Server Error`: Validation failed

#### Validate CMDB Application

```http
POST /api/validate/cmdb
```

**Request**:
- Content-Type: `application/json`
- Body:
```json
{
  "app_id": "MyApplication"
}
```

**Response**: Same structure as Terraform validation

**Error Responses**:
- `404 Not Found`: Application not found in CMDB
- `500 Internal Server Error`: CMDB connection or validation failed

#### List Validation Rules

```http
GET /api/validate/rules
```

**Response**:
```json
[
  {
    "id": "SEC-001",
    "name": "No Direct Web-to-Database Connections",
    "severity": "critical",
    "category": "security",
    "description": "Web tier must not directly connect to database tier"
  },
  {
    "id": "SEC-002",
    "name": "Production Database Encryption Required",
    "severity": "critical",
    "category": "security",
    "description": "All production databases must have encryption enabled"
  }
]
```

---

### CMDB Integration

#### List Applications

```http
GET /api/cmdb/applications
```

**Query Parameters**:
- `name` (optional): Filter by name (contains)
- `limit` (optional): Max results (default: 100)

**Response**:
```json
[
  {
    "sys_id": "abc123...",
    "name": "My Application",
    "description": "Application description"
  }
]
```

#### Get Application Details

```http
GET /api/cmdb/applications/{app_id}
```

**Path Parameters**:
- `app_id`: Application sys_id or name

**Response**:
```json
{
  "sys_id": "abc123...",
  "name": "My Application",
  "description": "Application description",
  "configuration_items": [
    {
      "sys_id": "ci123...",
      "name": "web-server-1",
      "type": "server",
      "environment": "production",
      "tier": "web",
      "business_owner": "team-a",
      "technical_owner": "ops-team",
      "data_classification": "internal",
      "properties": {
        "instance_type": "t3.medium",
        "multi_az": true
      }
    }
  ],
  "relationships": [
    {
      "parent_id": "ci123...",
      "child_id": "ci456...",
      "relationship_type": "connects_to"
    }
  ]
}
```

#### Get Application Topology

```http
GET /api/cmdb/applications/{app_id}/topology
```

**Response**:
```json
{
  "resources": [...],
  "relationships": [...],
  "topology": [
    {
      "source": "web-server-1",
      "source_tier": "web",
      "target": "app-server-1",
      "target_tier": "app",
      "relationship_type": "connects_to"
    }
  ],
  "source_type": "cmdb",
  "source_identifier": "My Application"
}
```

---

## Data Models

### Pattern

```typescript
{
  metadata: {
    id: string
    name: string
    version: string
    status: "approved" | "draft" | "deprecated" | "archived"
    owner: string
    approval_date?: string
    compliance_tags: string[]
    description: string
  }
  architecture: {
    components: Component[]
    network_topology: NetworkConnection[]
    constraints: Constraint[]
  }
  implementation: {
    terraform_module: string
    required_variables: string[]
    optional_variables: string[]
    example_usage?: string
  }
  documentation?: {
    diagram?: string
    adr?: string
    runbook?: string
  }
}
```

### ValidationReport

```typescript
{
  id: string
  timestamp: string
  source_type: "terraform" | "cmdb"
  source_identifier: string
  results: ValidationResult[]
  pattern_match?: PatternMatch
  approval_track?: "fast_track" | "standard_review" | "full_review"
  overall_status: "passed" | "failed" | "warning" | "skipped"
  summary: ValidationSummary
}
```

### ValidationResult

```typescript
{
  rule_id: string
  rule_name: string
  severity: "critical" | "high" | "medium" | "low"
  category: "security" | "resilience" | "compliance" | "technology" | "metadata"
  status: "passed" | "failed" | "warning" | "skipped"
  message: string
  details?: object
  resource_id?: string
  resource_type?: string
  timestamp: string
}
```

---

## Error Responses

All endpoints may return these errors:

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters or body"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error: <error message>"
}
```

---

## Rate Limiting

Currently no rate limiting (POC). In production, implement:
- 100 requests/minute per IP
- 1000 requests/hour per API key

---

## Examples

### Complete Validation Workflow

```bash
# 1. Generate Terraform plan
terraform plan -out=tfplan.binary
terraform show -json tfplan.binary > tfplan.json

# 2. Validate
REPORT=$(curl -s -X POST http://localhost:5000/api/validate/terraform \
  -F "file=@tfplan.json")

# 3. Extract results
SCORE=$(echo $REPORT | jq -r '.summary.compliance_score')
STATUS=$(echo $REPORT | jq -r '.overall_status')

echo "Compliance Score: $SCORE"
echo "Status: $STATUS"

# 4. Make decision
if [ "$STATUS" = "passed" ]; then
  terraform apply tfplan.binary
else
  echo "Validation failed, review required"
  echo $REPORT | jq '.results[] | select(.status == "failed")'
fi
```

### Integration with CI/CD

```python
import requests
import sys

# Upload Terraform plan
with open('tfplan.json', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/api/validate/terraform',
        files={'file': f}
    )

report = response.json()

# Check compliance
if report['summary']['compliance_score'] < 0.8:
    print(f"❌ Compliance too low: {report['summary']['compliance_score']:.0%}")
    sys.exit(1)

if report['summary']['critical_violations'] > 0:
    print(f"❌ {report['summary']['critical_violations']} critical violations")
    sys.exit(1)

print(f"✅ Validation passed: {report['summary']['compliance_score']:.0%}")
```

---

## Versioning

API version: v0.1.0 (POC)

Future versions will use URL versioning: `/api/v2/patterns/`

---

## Support

- Documentation: http://localhost:5000/api/docs
- Issues: Create issue in repository
- Email: architecture-team@company.com
