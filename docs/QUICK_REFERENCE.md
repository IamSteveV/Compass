# Quick Reference Card

Fast reference for common commands and operations.

---

## Installation

```bash
# Clone and setup
git clone https://github.com/yourorg/compass.git && cd Compass
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Initialize
python -c "from src.database.session import init_db; init_db()"

# Start
uvicorn src.api.main:app --reload --port 5000
```

---

## Starting the Application

```bash
# Development (auto-reload)
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 5000

# Production (4 workers)
uvicorn src.api.main:app --host 0.0.0.0 --port 5000 --workers 4

# With Docker
docker compose up -d

# With custom port
uvicorn src.api.main:app --port 8080
```

---

## Key URLs

| Resource | URL |
|----------|-----|
| Web UI | http://localhost:5000/static/index.html |
| Dashboard | http://localhost:5000/static/dashboard.html |
| API Docs | http://localhost:5000/api/docs |
| Health Check | http://localhost:5000/health |
| Metrics | http://localhost:5000/metrics |
| Root | http://localhost:5000/ |

---

## CLI Commands

### Validation

```bash
# Validate Terraform plan
python validate.py validate --terraform-plan path/to/plan.json

# Validate with output to file
python validate.py validate --terraform-plan plan.json --output report.json

# Verbose output
python validate.py validate --terraform-plan plan.json --verbose

# CMDB validation
python validate.py validate --cmdb-app "APP-12345"
```

### List Rules

```bash
# List all validation rules
python validate.py list-rules

# List rules by category
python validate.py list-rules --category security

# List rules by severity
python validate.py list-rules --severity critical
```

### List Patterns

```bash
# List all patterns
python validate.py list-patterns

# List approved patterns only
python validate.py list-patterns --status approved
```

---

## API Endpoints

### Validation

```bash
# Validate Terraform plan
curl -X POST http://localhost:5000/api/validate/terraform \
  -F "file=@plan.json"

# Validate CMDB application
curl -X POST http://localhost:5000/api/validate/cmdb \
  -H "Content-Type: application/json" \
  -d '{"app_id": "APP-12345"}'

# Get validation rules
curl http://localhost:5000/api/validate/rules
```

### Patterns

```bash
# Get all patterns
curl http://localhost:5000/api/patterns/

# Get specific pattern
curl http://localhost:5000/api/patterns/PAT-001

# Get pattern diagram
curl http://localhost:5000/api/patterns/PAT-001/diagram

# Search patterns
curl http://localhost:5000/api/patterns/search/web
```

### Analytics

```bash
# Dashboard summary
curl http://localhost:5000/api/analytics/dashboard/summary

# Compliance overview (last 30 days)
curl http://localhost:5000/api/analytics/compliance/overview?days=30

# Recent validations
curl http://localhost:5000/api/analytics/validations/recent?limit=10

# Popular patterns
curl http://localhost:5000/api/analytics/patterns/popular?limit=5

# Top violations
curl http://localhost:5000/api/analytics/violations/top-rules?limit=10
```

### System

```bash
# Health check
curl http://localhost:5000/health

# System metrics
curl http://localhost:5000/metrics

# API info
curl http://localhost:5000/api
```

---

## Database Commands

```bash
# Initialize database
python -c "from src.database.session import init_db; init_db()"

# Create migration
alembic revision -m "description"

# Run migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history

# Reset database (CAUTION)
rm validation.db && python -c "from src.database.session import init_db; init_db()"
```

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_validation_engine.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run integration tests only
pytest tests/integration/ -v

# Run tests matching pattern
pytest -k "test_validation" -v

# Generate coverage report
pytest --cov=src --cov-report=term-missing
```

---

## Docker Commands

```bash
# Build image
docker build -t compass:latest .

# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f app

# Restart service
docker compose restart app

# Execute command in container
docker compose exec app python -m pytest

# Rebuild and start
docker compose up -d --build

# Clean up
docker compose down -v --remove-orphans
```

---

## Code Quality

```bash
# Format code
black src/ tests/

# Check formatting
black src/ tests/ --check

# Lint code
flake8 src/ tests/

# Type checking
mypy src/

# Run all quality checks
black src/ tests/ && flake8 src/ tests/ && mypy src/
```

---

## Development Utilities

### Generate Sample Data

```bash
# Generate all sample files
python scripts/generate_sample_data.py --output-dir examples

# Generate specific pattern
python scripts/generate_sample_data.py --pattern 3-tier --output-dir examples
```

### Interactive Python Shell

```bash
# Start Python shell with context
python

>>> from src.validation.engine import ValidationEngine
>>> from src.patterns.library import PatternLibrary
>>> engine = ValidationEngine()
>>> patterns = PatternLibrary()
>>> patterns.get_all_patterns()
```

### Database Inspection

```bash
# SQLite
sqlite3 validation.db

# List tables
.tables

# Describe table
.schema validation_history

# Query data
SELECT * FROM validation_history LIMIT 5;

# Exit
.quit
```

---

## Environment Variables

```bash
# Core settings
export APP_ENV=development
export APP_DEBUG=true
export LOG_LEVEL=INFO

# Database
export DATABASE_URL=sqlite:///./validation.db

# ServiceNow
export SERVICENOW_INSTANCE=your-instance.service-now.com
export SERVICENOW_USERNAME=user
export SERVICENOW_PASSWORD=pass

# Validation
export VALIDATION_PARALLEL_EXECUTION=true
export VALIDATION_MAX_WORKERS=4
```

---

## File Locations

| Item | Path |
|------|------|
| Application | `src/` |
| Configuration | `config/config.yaml` |
| Environment | `.env` |
| Patterns | `patterns/` |
| Database | `validation.db` |
| Logs | `logs/` |
| Tests | `tests/` |
| Static Files | `static/` |
| Documentation | `docs/` |
| Examples | `examples/` |

---

## Validation Rules Reference

### Security (4 rules)

| Rule ID | Name | Severity |
|---------|------|----------|
| SEC-001 | No Direct Web-to-Database | Critical |
| SEC-002 | Database Encryption | Critical |
| SEC-003 | DMZ Isolation | Critical |
| SEC-004 | Backup Requirement | High |

### Network (3 rules)

| Rule ID | Name | Severity |
|---------|------|----------|
| NET-001 | Public Subnet Isolation | Critical |
| NET-002 | SSL/TLS Requirement | High |
| NET-003 | VPC Flow Logs | Medium |

### Cost (2 rules)

| Rule ID | Name | Severity |
|---------|------|----------|
| COST-001 | Unused Resources | Low |
| COST-002 | Oversized Instances | Low |

### Metadata (2 rules)

| Rule ID | Name | Severity |
|---------|------|----------|
| META-001 | Required Fields | High |
| META-002 | DR Tier Designation | Medium |

### Technology (2 rules)

| Rule ID | Name | Severity |
|---------|------|----------|
| TECH-001 | Database Versions | Medium |
| TECH-002 | Instance Types | Low |

### Resilience (2 rules)

| Rule ID | Name | Severity |
|---------|------|----------|
| RES-001 | Multi-AZ Requirement | High |
| RES-002 | Automated Backups | High |

---

## Pattern Reference

### PAT-001: 3-Tier Web Application
- **Components**: ALB, Web tier (2+), App tier (2+), Database (Multi-AZ)
- **Approval**: Fast Track ≥95%, Standard 85-94%, Full <85%
- **Use Case**: Traditional web applications

### PAT-002: Microservices Architecture
- **Components**: API Gateway, Services, Databases, Message Queue
- **Approval**: Same thresholds as PAT-001
- **Use Case**: Modern distributed applications

### COMP-001: High Availability Database
- **Components**: Primary DB (Multi-AZ), Read replicas (2+)
- **Approval**: Same thresholds as PAT-001
- **Use Case**: Mission-critical data storage

---

## Approval Routing Thresholds

| Pattern Match Score | Approval Track | Review Time |
|---------------------|----------------|-------------|
| ≥95% | Fast Track | Auto-approve eligible |
| 85-94% | Standard Review | 2-3 days |
| <85% | Full Review | Architecture committee |

---

## Common Workflows

### Workflow 1: Quick Validation

```bash
# 1. Generate sample data
python scripts/generate_sample_data.py

# 2. Validate
python validate.py validate --terraform-plan examples/terraform_plan_3-tier.json

# 3. View in web UI
# Upload same file at http://localhost:5000/static/index.html
```

### Workflow 2: CI/CD Integration

```bash
# In your CI/CD pipeline:
terraform plan -out=plan.tfplan
terraform show -json plan.tfplan > plan.json
python validate.py validate --terraform-plan plan.json

# Exit code 0 = passed, 1 = failed
```

### Workflow 3: Check System Health

```bash
# 1. Check health
curl http://localhost:5000/health | jq

# 2. Check metrics
curl http://localhost:5000/metrics | jq

# 3. View dashboard
open http://localhost:5000/static/dashboard.html
```

---

## Troubleshooting Quick Fixes

```bash
# Port in use
lsof -i :5000 | grep LISTEN
kill -9 <PID>

# Module not found
source venv/bin/activate
pip install -r requirements.txt

# Database locked
rm validation.db
python -c "from src.database.session import init_db; init_db()"

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# Reinstall dependencies
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Check uvicorn processes
ps aux | grep uvicorn
pkill -f uvicorn
```

---

## Git Workflow

```bash
# Start new feature
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "Add my feature"

# Push to remote
git push -u origin feature/my-feature

# Update from main
git checkout main
git pull
git checkout feature/my-feature
git merge main

# Create PR (using gh CLI)
gh pr create --title "My Feature" --body "Description"
```

---

## Keyboard Shortcuts (Web UI)

| Action | Shortcut |
|--------|----------|
| Upload file | `Ctrl+U` (if implemented) |
| Refresh dashboard | `Ctrl+R` |
| Toggle auto-refresh | `Ctrl+A` (if implemented) |
| Export data | `Ctrl+E` (if implemented) |
| Copy report | `Ctrl+C` (after validation) |

---

## Performance Tips

```bash
# Use parallel execution
export VALIDATION_PARALLEL_EXECUTION=true

# Increase workers
uvicorn src.api.main:app --workers 8

# Use PostgreSQL instead of SQLite
export DATABASE_URL=postgresql://user:pass@localhost/compass

# Enable caching (if implemented)
export ENABLE_CACHE=true
export CACHE_TTL=300
```

---

## Monitoring Commands

```bash
# Watch logs
tail -f logs/app.log

# Monitor requests
watch -n 1 'curl -s http://localhost:5000/health | jq .components'

# Check resource usage
docker stats compass_app_1

# Monitor database size
watch -n 5 'ls -lh validation.db'
```

---

## Useful One-Liners

```bash
# Count validation rules
grep -r "class.*Rule" src/validation/rules/ | wc -l

# List all API endpoints
grep -r "@router\." src/api/routers/ | cut -d: -f2 | sort

# Check Python imports
pipdeptree

# Find TODO comments
grep -r "TODO" src/

# Count lines of code
find src/ -name "*.py" | xargs wc -l | tail -1
```

---

## Version Information

- **Current Version**: v0.3.0
- **Python Required**: 3.10+
- **Dependencies**: 43 packages
- **Database**: SQLite / PostgreSQL
- **API Framework**: FastAPI 0.104.1

---

## Support Resources

| Resource | Link/Command |
|----------|--------------|
| Documentation | `docs/` directory |
| API Docs | http://localhost:5000/api/docs |
| GitHub Issues | https://github.com/yourorg/compass/issues |
| Health Check | `curl http://localhost:5000/health` |
| User Guide | [docs/USER_GUIDE.md](USER_GUIDE.md) |
| Installation | [docs/INSTALLATION.md](INSTALLATION.md) |
| Architecture | [docs/ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md) |

---

*Quick Reference for Architecture Validation & Pattern Management System*
*Print this page for easy reference during development!*
