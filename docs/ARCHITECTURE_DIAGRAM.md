# Architecture Validation & Pattern Management System
## Complete Application Architecture Diagram

This document provides a comprehensive visual representation of the system architecture, showing all components, their interactions, and data flows.

## System Overview

The Architecture Validation & Pattern Management System is a multi-layered application that validates infrastructure against architectural standards and provides pattern matching capabilities.

---

## Architecture Diagram (Mermaid)

```mermaid
graph TB
    %% Styling
    classDef uiLayer fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef apiLayer fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef coreLayer fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef rulesLayer fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef patternsLayer fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    classDef dataLayer fill:#e0f2f1,stroke:#00796b,stroke-width:2px
    classDef dbLayer fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef externalLayer fill:#efebe9,stroke:#5d4037,stroke-width:2px

    %% User Interfaces Layer
    subgraph UI["🖥️ User Interfaces"]
        CLI["CLI Tool<br/>(validate.py)<br/>Click + Rich"]
        WebUI["Web UI<br/>(index.html)<br/>Bootstrap 5.3"]
        Dashboard["Analytics Dashboard<br/>(dashboard.html)<br/>Chart.js"]
        APIClient["REST API Clients<br/>(External Tools)"]
    end

    %% API Layer
    subgraph API["🌐 REST API Layer - FastAPI v0.2.0"]
        MainAPI["FastAPI Application<br/>(main.py)"]

        subgraph Routers["API Routers"]
            ValidationRouter["Validation Router<br/>POST /validate/*"]
            PatternsRouter["Patterns Router<br/>GET /patterns/*"]
            CMDBRouter["CMDB Router<br/>GET /cmdb/*"]
            AnalyticsRouter["Analytics Router<br/>GET /analytics/*"]
            HistoryRouter["History Router<br/>POST /history/*"]
        end
    end

    %% Core Engine Layer
    subgraph Core["⚙️ Core Validation Engine"]
        ValidationEngine["Validation Engine<br/>(engine.py)<br/>Parallel/Sequential Execution"]
        RuleRegistry["Rule Registry<br/>(rule.py)<br/>15 Rules"]
        PatternMatcher["Pattern Matcher<br/>(matcher.py)<br/>Similarity Scoring 0-100%"]
        ApprovalRouter["Approval Router<br/>Fast Track ≥95%<br/>Standard 85-94%<br/>Full Review <85%"]
    end

    %% Validation Rules Layer
    subgraph Rules["📋 Validation Rules - 15 Total"]
        SecurityRules["Security Rules (4)<br/>SEC-001: No Web-to-DB<br/>SEC-002: DB Encryption<br/>SEC-003: DMZ Isolation<br/>SEC-004: Backup Requirement"]
        MetadataRules["Metadata Rules (2)<br/>META-001: Required Fields<br/>META-002: DR Tier"]
        TechRules["Technology Rules (2)<br/>TECH-001: DB Versions<br/>TECH-002: Instance Types"]
        ResilienceRules["Resilience Rules (2)<br/>RES-001: Multi-AZ<br/>RES-002: Automated Backups"]
        NetworkRules["Network Rules (3)<br/>NET-001: Public Subnet<br/>NET-002: SSL/TLS<br/>NET-003: VPC Flow Logs"]
        CostRules["Cost Rules (2)<br/>COST-001: Unused Resources<br/>COST-002: Oversized Instances"]
    end

    %% Pattern Library Layer
    subgraph Patterns["📐 Pattern Library System"]
        PatternLibrary["Pattern Library<br/>(library.py)<br/>YAML Loader"]

        subgraph PatternTypes["Reference Patterns"]
            Pattern3Tier["PAT-001<br/>3-Tier Web Application<br/>ALB → Web → App → DB"]
            PatternMicro["PAT-002<br/>Microservices Architecture<br/>API Gateway → Services"]
            PatternHA["COMP-001<br/>HA Database<br/>Multi-AZ + Replicas"]
        end
    end

    %% Data Sources Layer
    subgraph DataSources["📥 Data Sources & Integrations"]
        TerraformParser["Terraform Parser<br/>(parser.py)<br/>JSON Plan Loader<br/>Supports TF 1.0-1.6"]
        CMDBConnector["ServiceNow CMDB<br/>(connector.py)<br/>REST API Client<br/>Basic Auth"]
    end

    %% Database Layer
    subgraph Database["💾 Database Layer - SQLAlchemy"]
        DatabaseModels["Database Models<br/>(models.py)"]
        Repositories["Repository Pattern<br/>(repository.py)<br/>Data Access Layer"]

        subgraph Tables["Database Tables"]
            ValidationHistory["validation_history<br/>Audit Trail"]
            PatternUsage["pattern_usage<br/>Adoption Metrics"]
            RuleViolation["rule_violation<br/>Violation Tracking"]
            ComplianceTrend["compliance_trend<br/>Daily Aggregates"]
        end
    end

    %% External Systems Layer
    subgraph External["🔌 External Systems"]
        ServiceNow[("ServiceNow CMDB<br/>Configuration Items<br/>Relationships")]
        Terraform[/"Terraform<br/>Infrastructure Plans<br/>JSON Output"/]
        GitRepo[/"Git Repository<br/>Pattern YAML Files<br/>Version Control"/]
    end

    %% Supporting Services
    subgraph Support["🛠️ Supporting Services"]
        ConfigManager["Configuration<br/>(config.py)<br/>Pydantic Settings"]
        Logger["Logging System<br/>Structured JSON Logs"]
        DiagramGen["Diagram Generator<br/>(diagrams.py)<br/>Graphviz"]
    end

    %% User Interface Connections
    CLI -->|HTTP Request| MainAPI
    WebUI -->|HTTP Request| MainAPI
    Dashboard -->|HTTP Request| MainAPI
    APIClient -->|HTTP Request| MainAPI

    %% API Router Connections
    MainAPI --> ValidationRouter
    MainAPI --> PatternsRouter
    MainAPI --> CMDBRouter
    MainAPI --> AnalyticsRouter
    MainAPI --> HistoryRouter

    %% Validation Flow
    ValidationRouter -->|validate()| ValidationEngine
    ValidationEngine -->|get_rules()| RuleRegistry
    ValidationEngine -->|match_pattern()| PatternMatcher
    ValidationEngine -->|determine_track()| ApprovalRouter

    %% Rule Execution
    RuleRegistry --> SecurityRules
    RuleRegistry --> MetadataRules
    RuleRegistry --> TechRules
    RuleRegistry --> ResilienceRules
    RuleRegistry --> NetworkRules
    RuleRegistry --> CostRules

    %% Pattern Matching
    PatternsRouter -->|get_patterns()| PatternLibrary
    PatternLibrary --> Pattern3Tier
    PatternLibrary --> PatternMicro
    PatternLibrary --> PatternHA
    PatternLibrary -->|load YAML| GitRepo
    PatternMatcher -->|get_all()| PatternLibrary

    %% Data Source Integration
    ValidationRouter -->|parse_plan()| TerraformParser
    CMDBRouter -->|query()| CMDBConnector
    TerraformParser -->|read JSON| Terraform
    CMDBConnector -->|REST API| ServiceNow

    %% Database Operations
    HistoryRouter -->|save/query| Repositories
    AnalyticsRouter -->|get_stats()| Repositories
    Repositories -->|ORM| DatabaseModels
    DatabaseModels --> ValidationHistory
    DatabaseModels --> PatternUsage
    DatabaseModels --> RuleViolation
    DatabaseModels --> ComplianceTrend

    %% Supporting Services
    MainAPI -.->|load config| ConfigManager
    MainAPI -.->|log events| Logger
    PatternsRouter -->|generate diagram| DiagramGen

    %% Apply Styles
    class CLI,WebUI,Dashboard,APIClient uiLayer
    class MainAPI,ValidationRouter,PatternsRouter,CMDBRouter,AnalyticsRouter,HistoryRouter apiLayer
    class ValidationEngine,RuleRegistry,PatternMatcher,ApprovalRouter coreLayer
    class SecurityRules,MetadataRules,TechRules,ResilienceRules,NetworkRules,CostRules rulesLayer
    class PatternLibrary,Pattern3Tier,PatternMicro,PatternHA patternsLayer
    class TerraformParser,CMDBConnector dataLayer
    class DatabaseModels,Repositories,ValidationHistory,PatternUsage,RuleViolation,ComplianceTrend dbLayer
    class ServiceNow,Terraform,GitRepo externalLayer
```

---

## Layer Descriptions

### 1. User Interfaces Layer 🖥️

The system provides multiple interfaces for different use cases:

- **CLI Tool** (`validate.py`): Command-line interface using Click framework with Rich formatting
  - Use case: CI/CD integration, automated validation, scripting
  - Features: Colored output, table formatting, JSON export

- **Web UI** (`static/index.html`): Browser-based interface with Bootstrap 5.3
  - Use case: Interactive validation, pattern browsing
  - Features: File upload, real-time validation, visual results

- **Analytics Dashboard** (`static/dashboard.html`): Metrics and analytics visualization
  - Use case: Compliance monitoring, trend analysis
  - Features: Chart.js graphs, real-time metrics, historical data

- **REST API Clients**: External tools and integrations
  - Use case: Platform integration, custom tooling
  - Features: OpenAPI documentation, JSON responses

### 2. REST API Layer 🌐

FastAPI-based REST API (v0.2.0) with multiple specialized routers:

#### **Validation Router** (`/api/validate/*`)
- `POST /validate/terraform` - Validate Terraform plan
- `POST /validate/cmdb` - Validate CMDB application
- `GET /validate/rules` - List all validation rules

#### **Patterns Router** (`/api/patterns/*`)
- `GET /patterns/` - List all patterns
- `GET /patterns/{id}` - Get pattern details
- `GET /patterns/{id}/diagram` - Get pattern diagram
- `GET /patterns/search/{query}` - Search patterns

#### **CMDB Router** (`/api/cmdb/*`)
- `GET /cmdb/applications` - List CMDB applications
- `GET /cmdb/applications/{id}` - Get application details
- `GET /cmdb/applications/{id}/topology` - Get topology

#### **Analytics Router** (`/api/analytics/*`) - NEW in v0.2.0
- `GET /analytics/compliance/overview` - Compliance metrics
- `GET /analytics/validations/recent` - Recent validations
- `GET /analytics/patterns/popular` - Popular patterns
- `GET /analytics/violations/top-rules` - Most violated rules
- `GET /analytics/dashboard/summary` - Dashboard data

#### **History Router** (`/api/history/*`) - NEW in v0.2.0
- `POST /history/save` - Save validation to history
- `GET /history/{id}` - Get validation details

### 3. Core Validation Engine ⚙️

The heart of the system, responsible for executing validation logic:

#### **Validation Engine** (`src/validation/engine.py`)
- Executes validation rules against resources
- Supports parallel execution (thread pool) or sequential
- Context-aware validation with topology information
- Generates comprehensive validation reports

#### **Rule Registry** (`src/validation/rule.py`)
- Centralized registry for all 15 validation rules
- Dynamic rule loading and registration
- Rule filtering by category and severity
- Abstract base class for rule development

#### **Pattern Matcher** (`src/patterns/matcher.py`)
- Multi-dimensional similarity scoring (0-100%)
  - Component matching: 40% weight
  - Topology matching: 30% weight
  - Configuration alignment: 30% weight
- Deviation detection and reporting
- Best-match selection algorithm

#### **Approval Router**
- Threshold-based track determination:
  - **Fast Track** (≥95%): Auto-approve eligible
  - **Standard Review** (85-94%): 2-3 day review
  - **Full Review** (<85%): Architecture committee

### 4. Validation Rules Layer 📋

15 comprehensive validation rules across 6 categories:

#### **Security Rules (4 rules)**
- **SEC-001**: No Direct Web-to-Database Connections (Critical)
- **SEC-002**: Production Database Encryption (Critical)
- **SEC-003**: DMZ Isolation from Internal Database (Critical)
- **SEC-004**: Production Server Backup Requirement (High)

#### **Metadata Rules (2 rules)**
- **META-001**: Required Metadata Fields (High)
  - business_owner, technical_owner, data_classification
- **META-002**: Production DR Tier Designation (Medium)

#### **Technology Rules (2 rules)**
- **TECH-001**: Approved Database Versions (Medium)
  - PostgreSQL 14+, MySQL 8.0+, Oracle 19c+, SQL Server 2019+
- **TECH-002**: Approved Instance Types per Tier (Low)

#### **Resilience Rules (2 rules)**
- **RES-001**: Production Multi-AZ Requirement (High)
- **RES-002**: Database Automated Backup Requirement (High)

#### **Network Rules (3 rules)** - NEW in v0.2.0
- **NET-001**: Database Tier Public Subnet Isolation (Critical)
- **NET-002**: Load Balancer SSL/TLS Requirement (High)
- **NET-003**: VPC Flow Logs Requirement (Medium)

#### **Cost Optimization Rules (2 rules)** - NEW in v0.2.0
- **COST-001**: Unused Resource Detection (Low)
- **COST-002**: Oversized Instance Detection (Low)

### 5. Pattern Library System 📐

YAML-based pattern management with Git integration:

#### **Pattern Library** (`src/patterns/library.py`)
- Loads patterns from YAML files in Git repository
- Auto-reload on file changes
- Pattern versioning and status tracking
- Pattern metadata and compliance tags

#### **Reference Patterns**

**PAT-001: Standard 3-Tier Web Application**
- Components: ALB, Web tier (2+), App tier (2+), Database (Multi-AZ)
- Network: ALB → Web → App → Database
- Compliance: PCI-DSS, SOX, SOC2
- Use case: Traditional web applications

**PAT-002: Microservices Architecture**
- Components: API Gateway, service instances, databases, message queue
- Network: API Gateway → Services → Databases/Queue
- Compliance: Cloud-Native, SOC2
- Use case: Modern distributed applications

**COMP-001: High Availability Database**
- Components: Primary DB (Multi-AZ), Read replicas (2+)
- Features: 30-day backups, encryption, auto-failover
- Compliance: HA, DR, Backup
- Use case: Mission-critical data storage

### 6. Data Sources & Integrations Layer 📥

Integration with external infrastructure sources:

#### **Terraform Parser** (`src/terraform_parser/parser.py`)
- Parses JSON output from `terraform show -json`
- Supports Terraform versions 1.0 through 1.6
- Extracts resources, dependencies, and metadata
- Builds implicit topology from resource relationships

#### **ServiceNow CMDB Connector** (`src/cmdb/connector.py`)
- REST API client for ServiceNow CMDB
- Queries configuration items (CIs)
- Retrieves CI relationships and dependencies
- Supports HTTP Basic Authentication
- Builds application topology from CMDB data

### 7. Database Layer 💾

SQLAlchemy-based persistence layer (NEW in v0.2.0):

#### **Database Models** (`src/database/models.py`)

**validation_history**
- Complete validation audit trail
- Fields: id, timestamp, pattern_id, similarity_score, compliance_score, violations, report_json

**pattern_usage**
- Pattern adoption and usage metrics
- Tracks which patterns are used, when, and by whom

**rule_violation**
- Detailed violation tracking per rule
- Links to validation history and affected resources

**compliance_trend**
- Daily aggregated compliance metrics
- Enables trend analysis and historical reporting

#### **Repository Pattern** (`src/database/repository.py`)
- Data access layer abstraction
- CRUD operations for all models
- Complex queries for analytics
- Transaction management

### 8. External Systems Layer 🔌

Integration points with external systems:

- **ServiceNow CMDB**: Configuration management database
- **Terraform**: Infrastructure-as-Code tool
- **Git Repository**: Version-controlled pattern storage

### 9. Supporting Services Layer 🛠️

Utility and infrastructure services:

- **Configuration Manager**: Pydantic-based settings management
- **Logging System**: Structured JSON logging
- **Diagram Generator**: Graphviz-based topology visualization

---

## Data Flow Examples

### Example 1: Terraform Validation Flow

```
1. User uploads Terraform plan JSON via Web UI
2. Web UI → POST /api/validate/terraform
3. Validation Router → Terraform Parser
4. Terraform Parser → Validation Engine
5. Validation Engine:
   - Rule Registry → Execute 15 rules in parallel
   - Pattern Matcher → Calculate similarity scores
   - Approval Router → Determine approval track
6. Validation Engine → Validation Report
7. History Router → Save to database
8. Report returned to user with:
   - Pattern match (95% → Fast Track)
   - 2 critical violations
   - 5 warnings
   - Compliance score: 87%
```

### Example 2: CMDB Application Validation Flow

```
1. User enters application ID in Dashboard
2. Dashboard → POST /api/validate/cmdb
3. CMDB Router → ServiceNow CMDB Connector
4. CMDB Connector → Query ServiceNow API
5. CMDB Connector → Retrieve CIs and relationships
6. CMDB Connector → Build topology
7. Validation Engine → Execute rules + pattern matching
8. Report generated and saved to history
9. Analytics updated with new data point
10. Dashboard refreshes with new metrics
```

### Example 3: Analytics Dashboard Update Flow

```
1. Dashboard loads → GET /api/analytics/dashboard/summary
2. Analytics Router → Repositories
3. Repositories → Query database:
   - ValidationHistoryRepository.get_compliance_stats()
   - PatternUsageRepository.get_popular_patterns()
   - RuleViolationRepository.get_most_violated_rules()
4. Aggregated data returned to Dashboard
5. Chart.js renders:
   - Pattern adoption bar chart
   - Top violations bar chart
   - Compliance trend line chart
6. Recent validations table populated
```

---

## Technology Stack

### Backend
- **Python 3.10+**
- **FastAPI 0.104.1** - REST API framework
- **SQLAlchemy 2.0.23** - ORM
- **Pydantic 2.5.0** - Data validation
- **Click 8.1.7** - CLI framework
- **Rich 13.7.0** - Terminal formatting
- **Graphviz 0.20.1** - Diagram generation

### Frontend
- **Bootstrap 5.3** - UI framework
- **Chart.js 4.4.0** - Data visualization
- **Vanilla JavaScript** - No heavy frameworks

### Database
- **SQLite** (development/POC)
- **PostgreSQL** (production-ready)

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **GitHub Actions** - CI/CD pipeline

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Load Balancer                         │
│                         (Optional)                           │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────┴──────────────────────────────┐
│                   Docker Container                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │          FastAPI Application (Port 5000)               │ │
│  │  - Validation Engine                                   │ │
│  │  - REST API Routers                                    │ │
│  │  - Pattern Matcher                                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │               Static Files Server                      │ │
│  │  - HTML/CSS/JavaScript                                 │ │
│  │  - Dashboard                                           │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────┴──────────────────────────────┐
│                    Database Server                           │
│              (SQLite or PostgreSQL)                          │
│  - validation_history                                        │
│  - pattern_usage                                             │
│  - rule_violation                                            │
│  - compliance_trend                                          │
└──────────────────────────────────────────────────────────────┘
```

---

## Performance Characteristics

- **Parallel Rule Execution**: Up to 4x faster than sequential
- **Pattern Matching**: <100ms for typical infrastructure
- **API Response Time**: <500ms for most endpoints
- **Database Queries**: Indexed for optimal performance
- **Concurrent Users**: Supports 50+ simultaneous validations

---

## Security Features

- **Input Validation**: Pydantic models for all inputs
- **SQL Injection Protection**: Parameterized queries (SQLAlchemy)
- **XSS Protection**: Output encoding
- **File Upload Limits**: Max 10MB
- **Rate Limiting**: Configurable (planned)
- **Authentication**: API keys (planned)

---

## Monitoring & Observability

- **Health Endpoint**: `/health` - Application status
- **Structured Logging**: JSON-formatted logs
- **Request Logging**: All API requests logged
- **Error Tracking**: Exception details captured
- **Metrics**: Validation counts, compliance trends, pattern usage

---

## Version Information

- **Current Version**: v0.2.0 (January 16, 2024)
- **Initial Release**: v0.1.0 (January 15, 2024)
- **Next Planned**: v0.3.0 (PDF reports, notifications, cost estimation)

---

## Related Documentation

- [README.md](../README.md) - Project overview and quick start
- [FEATURES.md](FEATURES.md) - Complete feature list
- [USER_GUIDE.md](USER_GUIDE.md) - User documentation
- [API.md](API.md) - API reference
- [CHANGELOG.md](../CHANGELOG.md) - Version history
- [QUICK_DEMO.md](QUICK_DEMO.md) - 5-minute demo guide
- [PROJECT_SUMMARY.md](../PROJECT_SUMMARY.md) - Comprehensive summary

---

*This architecture diagram represents the system as of v0.2.0. Future versions may include additional components and integrations.*
