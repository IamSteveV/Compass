# Architecture Validation & Pattern Management System

A proof-of-concept system for validating infrastructure against architectural standards, providing a library of pre-approved architecture patterns, and automating architecture review workflows.

## Features

### Core Validation
- **Validation Engine**: Validate infrastructure against 15+ architectural rules covering security, compliance, resilience, network, and cost optimization
- **Pattern Library**: Pre-approved architecture patterns (3-tier web, microservices, HA database)
- **Pattern Matching**: Automatically identify matching patterns with similarity scores
- **Approval Routing**: Fast-track (≥95%), Standard (85-94%), or Full Review (<85%) based on pattern match
- **Multi-Source Support**: Validate Terraform plans or ServiceNow CMDB applications

### User Interfaces
- **Web UI**: Modern web interface for validation, pattern browsing, and analytics dashboard
- **REST API**: FastAPI-based REST API with OpenAPI documentation
- **CLI Tool**: Command-line interface for automation and CI/CD integration
- **Analytics Dashboard**: Real-time metrics, compliance trends, and violation tracking

### Advanced Features (v0.2.0)
- **Database Persistence**: SQLAlchemy-based history tracking and analytics
- **Validation History**: Track all validations with full audit trail
- **Pattern Usage Analytics**: Monitor pattern adoption and popular patterns
- **Violation Tracking**: Detailed tracking of rule violations by severity
- **Compliance Metrics**: Real-time compliance scores and trends
- **Test Data Generators**: Generate sample data for testing and demos
- **Diagram Generation**: Auto-generate architecture diagrams with Graphviz

## Quick Start

### Prerequisites

- Python 3.10+
- (Optional) Docker and Docker Compose
- (Optional) ServiceNow instance with CMDB access

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd Compass

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your ServiceNow credentials
```

### Running the Application

#### Option 1: Using Python Directly

```bash
# Start web server
python app.py

# Or use CLI
python validate.py --help
```

#### Option 2: Using Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

The web UI will be available at: http://localhost:5000
API documentation at: http://localhost:5000/api/docs

## Usage

### Command Line Interface

```bash
# Validate a Terraform plan
python validate.py validate --terraform-plan tfplan.json

# Validate a CMDB application
python validate.py validate --cmdb-app "MyApplication"

# List available patterns
python validate.py patterns

# Show specific pattern details
python validate.py patterns --pattern-id PAT-001

# List all validation rules
python validate.py rules

# Save validation report to JSON
python validate.py validate --terraform-plan tfplan.json --output report.json
```

### Web Interface

1. Open http://localhost:5000
2. Choose validation source:
   - **Terraform Plan**: Upload a JSON plan file
   - **CMDB Query**: Enter application name/ID
3. View validation results with:
   - Pattern match and similarity score
   - Approval track recommendation
   - Rule violations by severity
   - Compliance score
   - Pattern deviations

### REST API

```bash
# List patterns
curl http://localhost:5000/api/patterns/

# Get specific pattern
curl http://localhost:5000/api/patterns/PAT-001

# Validate Terraform plan
curl -X POST http://localhost:5000/api/validate/terraform \
  -F "file=@tfplan.json"

# Validate CMDB application
curl -X POST http://localhost:5000/api/validate/cmdb \
  -H "Content-Type: application/json" \
  -d '{"app_id": "MyApplication"}'

# List validation rules
curl http://localhost:5000/api/validate/rules

# List CMDB applications
curl http://localhost:5000/api/cmdb/applications
```

Full API documentation: http://localhost:5000/api/docs

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Web UI / CLI                      │
├─────────────────────────────────────────────────────┤
│              FastAPI REST API Layer                 │
├──────────────┬──────────────┬──────────────────────┤
│  Validation  │   Pattern    │      CMDB            │
│   Engine     │   Library    │   Connector          │
├──────────────┼──────────────┼──────────────────────┤
│  Rule        │   Pattern    │   Terraform          │
│  Registry    │   Matcher    │   Parser             │
├──────────────┴──────────────┴──────────────────────┤
│              Data Models & Config                   │
└─────────────────────────────────────────────────────┘
```

### Components

- **Validation Engine**: Executes rules against resources (parallel or sequential)
- **Rule Registry**: Manages validation rules with categories and severities
- **Pattern Library**: Loads patterns from YAML files in Git repository
- **Pattern Matcher**: Calculates similarity scores between infrastructure and patterns
- **CMDB Connector**: Integrates with ServiceNow CMDB via REST API
- **Terraform Parser**: Parses Terraform JSON plans
- **Diagram Generator**: Creates Graphviz diagrams from topology data

## Validation Rules

### Security Rules (4)
- **SEC-001**: No direct web-to-database connections (Critical)
- **SEC-002**: Production database encryption required (Critical)
- **SEC-003**: DMZ isolation from internal database (Critical)
- **SEC-004**: Production server backup requirement (High)

### Metadata Rules (2)
- **META-001**: Required metadata fields (High)
- **META-002**: Production DR tier designation (Medium)

### Technology Rules (2)
- **TECH-001**: Approved database versions (Medium)
- **TECH-002**: Approved instance types per tier (Low)

### Resilience Rules (2)
- **RES-001**: Production multi-AZ requirement (High)
- **RES-002**: Database automated backup requirement (High)

### Network Rules (3) - New in v0.2.0
- **NET-001**: Database tier public subnet isolation (Critical)
- **NET-002**: Load balancer SSL/TLS requirement (High)
- **NET-003**: VPC flow logs requirement (Medium)

### Cost Optimization Rules (2) - New in v0.2.0
- **COST-001**: Unused resource detection (Low)
- **COST-002**: Oversized instance detection (Low)

**Total: 15 validation rules**

## Architecture Patterns

### PAT-001: Standard 3-Tier Web Application
- **Components**: Web tier (2+ instances), App tier (2+ instances), Database (Multi-AZ)
- **Network**: ALB → Web → App → Database
- **Compliance**: PCI-DSS, SOX, SOC2
- **Status**: Approved

### PAT-002: Microservices Architecture
- **Components**: API Gateway, Service instances (3+), Service databases, Message queue
- **Network**: API Gateway → Services → Databases/Message Queue
- **Compliance**: Cloud-Native, SOC2
- **Status**: Approved

### COMP-001: High Availability Database
- **Components**: Primary database (Multi-AZ), Read replicas (2+)
- **Features**: 30-day backups, encryption, auto-failover
- **Compliance**: HA, DR, Backup
- **Status**: Approved

## Configuration

Configuration is managed via `config/config.yaml` and environment variables (`.env`):

```yaml
servicenow:
  instance_url: "${SNOW_INSTANCE_URL}"
  api_user: "${SNOW_API_USER}"
  api_password: "${SNOW_API_PASSWORD}"

patterns:
  repository: "./patterns"
  auto_reload: true

validation:
  severity_levels: [critical, high, medium, low]
  fail_on_critical: true
  parallel_execution: true
  max_workers: 4

approval:
  routing:
    fast_track_threshold: 0.95
    standard_review_threshold: 0.85
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_validation_engine.py

# Run with verbose output
pytest -v
```

### Adding a New Validation Rule

1. Create a new rule class in `src/validation/rules/`:

```python
from src.validation.rule import ArchitecturalRule
from src.models import ValidationResult, Severity, RuleCategory, ValidationStatus

class MyCustomRule(ArchitecturalRule):
    def __init__(self):
        super().__init__()
        self.id = "CUSTOM-001"
        self.name = "My Custom Rule"
        self.severity = Severity.HIGH
        self.category = RuleCategory.SECURITY

    def validate(self, resource, context=None):
        # Your validation logic
        if condition_met:
            return self.create_result(
                ValidationStatus.PASSED,
                "Resource passes validation"
            )
        else:
            return self.create_result(
                ValidationStatus.FAILED,
                "Resource fails validation"
            )
```

2. Register the rule in `src/validation/rules/__init__.py`
3. Add tests in `tests/unit/test_rules.py`

### Adding a New Pattern

1. Create directory: `patterns/reference-architectures/my-pattern/`
2. Create `pattern.yaml`:

```yaml
pattern:
  id: "PAT-XXX"
  name: "My Pattern"
  version: "1.0"
  status: "approved"
  owner: "Team Name"
  description: "Pattern description"

architecture:
  components:
    - name: "component_name"
      type: "server"
      tier: "web"
      minimum_instances: 2

  network_topology:
    - source: "component_a"
      target: "component_b"
      protocol: "https"

  constraints:
    - description: "Some constraint"
      type: "must"

implementation:
  terraform_module: "git::https://..."
  required_variables: ["var1", "var2"]
```

3. Add README.md with documentation
4. (Optional) Add diagram.png

## Project Structure

```
Compass/
├── src/
│   ├── api/              # FastAPI application
│   │   ├── main.py
│   │   └── routers/      # API endpoints
│   ├── validation/       # Validation engine
│   │   ├── engine.py
│   │   ├── rule.py
│   │   └── rules/        # Rule implementations
│   ├── patterns/         # Pattern library
│   ├── cmdb/            # ServiceNow integration
│   ├── terraform_parser/ # Terraform plan parser
│   ├── diagram/         # Diagram generation
│   ├── models.py        # Data models
│   └── config.py        # Configuration
├── patterns/            # Pattern definitions
│   ├── reference-architectures/
│   └── component-patterns/
├── static/              # Web UI files
│   ├── index.html
│   ├── css/
│   └── js/
├── tests/               # Tests
│   ├── unit/
│   └── integration/
├── config/              # Configuration files
├── docs/                # Documentation
├── app.py               # Web application entry point
├── validate.py          # CLI entry point
├── requirements.txt     # Python dependencies
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Add tests
5. Run tests (`pytest`)
6. Commit your changes (`git commit -am 'Add feature'`)
7. Push to branch (`git push origin feature/my-feature`)
8. Create Pull Request

## License

[Your License Here]

## Support

For questions or issues:
- Create an issue in the repository
- Contact the Enterprise Architecture Team
- See documentation in `/docs`

## Roadmap

### Phase 1 (Current - POC)
- ✅ Core validation engine
- ✅ 10 sample rules
- ✅ Pattern library and matching
- ✅ Terraform and CMDB integration
- ✅ CLI and web UI
- ✅ Basic diagram generation

### Phase 2 (Future)
- Bidirectional CMDB sync
- Pattern generator from existing architectures
- Cost estimation per pattern
- Approval workflow integration
- Policy as Code (OPA/Sentinel)

### Phase 3 (Future)
- Real-time compliance monitoring
- ML-based pattern recommendations
- Advanced diagram generation
- Multi-cloud support
- Integration with CI/CD pipelines

## Acknowledgments

Built with:
- FastAPI - Modern web framework
- Pydantic - Data validation
- Graphviz - Diagram generation
- Bootstrap - UI components
- Click - CLI framework
