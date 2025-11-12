# User Guide - Architecture Validation System

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Validating Infrastructure](#validating-infrastructure)
4. [Understanding Results](#understanding-results)
5. [Browsing Patterns](#browsing-patterns)
6. [Troubleshooting](#troubleshooting)

## Introduction

The Architecture Validation System helps ensure your infrastructure deployments comply with enterprise architectural standards. It validates infrastructure against a set of rules and matches it against approved architecture patterns.

### Key Concepts

- **Validation Rules**: Automated checks for security, compliance, resilience, and technology standards
- **Architecture Patterns**: Pre-approved reference architectures (e.g., 3-tier web, microservices)
- **Pattern Matching**: Automatic identification of which pattern your infrastructure most closely resembles
- **Approval Routing**: Automatic recommendation for review process based on pattern match score

## Getting Started

### Accessing the System

#### Web Interface
Open your browser to: http://localhost:5000

#### Command Line
```bash
python validate.py --help
```

#### API
API documentation: http://localhost:5000/api/docs

### First Time Setup

1. **Configure ServiceNow Connection** (if using CMDB validation):
   ```bash
   cp .env.example .env
   # Edit .env and add your ServiceNow credentials
   ```

2. **Verify Installation**:
   ```bash
   # Check available patterns
   python validate.py patterns

   # Check available rules
   python validate.py rules
   ```

## Validating Infrastructure

### Option 1: Terraform Plan Validation

Terraform validation checks your infrastructure-as-code before deployment.

#### Step 1: Generate Terraform Plan

```bash
# Create binary plan
terraform plan -out=tfplan.binary

# Convert to JSON
terraform show -json tfplan.binary > tfplan.json
```

#### Step 2: Validate

**Using CLI:**
```bash
python validate.py validate --terraform-plan tfplan.json
```

**Using Web UI:**
1. Navigate to http://localhost:5000
2. Select "Terraform Plan" tab
3. Upload `tfplan.json`
4. Click "Validate"

**Using API:**
```bash
curl -X POST http://localhost:5000/api/validate/terraform \
  -F "file=@tfplan.json"
```

### Option 2: CMDB Application Validation

CMDB validation checks your deployed infrastructure.

#### Step 1: Find Your Application

Get your application name or sys_id from ServiceNow CMDB.

#### Step 2: Validate

**Using CLI:**
```bash
python validate.py validate --cmdb-app "MyApplication"
```

**Using Web UI:**
1. Navigate to http://localhost:5000
2. Select "CMDB Query" tab
3. Enter application name or sys_id
4. Click "Validate"

**Using API:**
```bash
curl -X POST http://localhost:5000/api/validate/cmdb \
  -H "Content-Type: application/json" \
  -d '{"app_id": "MyApplication"}'
```

## Understanding Results

### Validation Report Structure

```
┌─────────────────────────────────────────┐
│ Pattern Match: 3-Tier Web (92%)        │
│ Approval Track: STANDARD REVIEW         │
│                                         │
│ ✓ Passed: 12 rules                     │
│ ⚠ Warnings: 2 rules                    │
│ ✗ Violations: 1 rule                   │
│                                         │
│ Compliance Score: 85%                   │
└─────────────────────────────────────────┘
```

### Pattern Match

**Similarity Score**: How closely your infrastructure matches the identified pattern (0-100%)

**Approval Tracks**:
- **Fast Track (≥95%)**: Minimal review required, auto-approve eligible
- **Standard Review (85-94%)**: Light architectural review (2-3 days)
- **Full Review (<85%)**: Complete architecture committee review

### Validation Results

**Status Types**:
- ✓ **Passed**: Resource complies with rule
- ⚠ **Warning**: Non-critical issue, should be addressed
- ✗ **Failed**: Rule violation, must be fixed
- ○ **Skipped**: Rule not applicable to this resource

**Severity Levels**:
1. **Critical**: Must be fixed before deployment
2. **High**: Should be fixed soon
3. **Medium**: Fix in next sprint
4. **Low**: Nice to have

### Example Results Interpretation

#### Good Result
```
Pattern Match: 3-Tier Web (97%)
Approval Track: FAST TRACK ✓
Passed: 25, Warnings: 1, Violations: 0
Compliance Score: 96%
```
→ **Action**: Proceed with deployment, address warning in next iteration

#### Needs Work
```
Pattern Match: 3-Tier Web (87%)
Approval Track: STANDARD REVIEW
Passed: 18, Warnings: 4, Violations: 3
Compliance Score: 72%
```
→ **Action**: Fix violations before deployment, review warnings with architect

#### Requires Review
```
Pattern Match: Unknown (45%)
Approval Track: FULL REVIEW
Passed: 10, Warnings: 8, Violations: 7
Compliance Score: 40%
```
→ **Action**: Submit to architecture committee, significant rework likely needed

## Browsing Patterns

### Viewing Available Patterns

**CLI:**
```bash
# List all patterns
python validate.py patterns

# View specific pattern
python validate.py patterns --pattern-id PAT-001
```

**Web UI:**
1. Navigate to http://localhost:5000
2. Click "Patterns" in navigation
3. Browse pattern cards
4. Click a pattern for details

**API:**
```bash
# List all patterns
curl http://localhost:5000/api/patterns/

# Get specific pattern
curl http://localhost:5000/api/patterns/PAT-001
```

### Using Patterns

Each pattern includes:
- **Description**: What the pattern is for
- **Components**: Required infrastructure components
- **Network Topology**: How components connect
- **Constraints**: Must/must-not rules
- **Terraform Module**: Ready-to-use IaC module
- **Documentation**: Links to diagrams, ADRs, examples

### Example: Using the 3-Tier Web Pattern

1. **Review Pattern**: Check PAT-001 documentation
2. **Use Terraform Module**:
   ```hcl
   module "web_app" {
     source = "git::https://github.com/bank/patterns.git//3-tier-web?ref=v1.0"

     application_name = "my-app"
     environment      = "production"
     owner           = "team-a"
     vpc_id          = "vpc-12345"
     subnet_ids      = ["subnet-1", "subnet-2"]
   }
   ```
3. **Generate Plan**: `terraform plan -out=tfplan.binary`
4. **Validate**: Should achieve 95%+ match with PAT-001

## Troubleshooting

### Common Issues

#### "Pattern not found"

**Problem**: Pattern library not loading
**Solution**:
```bash
# Check patterns directory exists
ls -la patterns/

# Verify YAML syntax
cat patterns/reference-architectures/3-tier-web/pattern.yaml
```

#### "ServiceNow connection failed"

**Problem**: Cannot connect to CMDB
**Solution**:
1. Verify credentials in `.env`:
   ```
   SNOW_INSTANCE_URL=https://your-instance.service-now.com
   SNOW_API_USER=your_username
   SNOW_API_PASSWORD=your_password
   ```
2. Test connection:
   ```bash
   curl -u username:password \
     https://your-instance.service-now.com/api/now/table/cmdb_ci_appl?sysparm_limit=1
   ```

#### "Invalid Terraform plan JSON"

**Problem**: Uploaded file is not valid JSON plan
**Solution**:
1. Ensure using `terraform show -json` (not `terraform plan`)
2. Verify JSON syntax: `python -m json.tool tfplan.json`
3. Check Terraform version compatibility

#### "All rules showing as SKIPPED"

**Problem**: Resources missing required metadata
**Solution**:
1. Ensure resources have proper tags/metadata
2. Check that resource types are recognized
3. Review validation context

### Getting Help

1. **Check Logs**:
   ```bash
   # Docker logs
   docker-compose logs -f

   # Application logs
   tail -f logs/app.log
   ```

2. **Verbose Mode**:
   ```bash
   python validate.py validate --terraform-plan tfplan.json --verbose
   ```

3. **API Errors**:
   - Check `/api/docs` for endpoint documentation
   - Review request/response in browser dev tools
   - Check HTTP status codes and error messages

4. **Contact Support**:
   - Create issue in repository
   - Email: architecture-team@company.com
   - Slack: #architecture-validation

## Best Practices

### For Developers

1. **Validate Early**: Run validation before submitting PR
2. **Use Approved Patterns**: Start from a pattern when possible
3. **Address Warnings**: Don't ignore warnings, they become violations
4. **Tag Properly**: Include all required metadata tags

### For Architects

1. **Keep Patterns Updated**: Review patterns quarterly
2. **Monitor Compliance Trends**: Track compliance scores over time
3. **Refine Rules**: Adjust rules based on feedback
4. **Document Exceptions**: Track and justify any approved deviations

### For Operations

1. **Periodic Scans**: Run CMDB validation monthly
2. **Drift Detection**: Compare Terraform vs CMDB
3. **Audit Trail**: Save validation reports
4. **Automated Gates**: Integrate into CI/CD pipelines

## Advanced Usage

### Saving Reports

```bash
# Save as JSON
python validate.py validate --terraform-plan tfplan.json \
  --output validation-report.json

# Use in scripts
if [ $? -eq 0 ]; then
  echo "Validation passed"
else
  echo "Validation failed"
  cat validation-report.json
  exit 1
fi
```

### CI/CD Integration

**GitHub Actions Example**:
```yaml
- name: Validate Architecture
  run: |
    python validate.py validate \
      --terraform-plan tfplan.json \
      --output report.json

- name: Upload Report
  uses: actions/upload-artifact@v2
  with:
    name: validation-report
    path: report.json
```

### Custom Rules

Contact the Architecture team to request new validation rules or discuss exceptions to existing rules.

## Appendix

### All Validation Rules

See full list: `python validate.py rules`

### All Patterns

See full list: `python validate.py patterns`

### Configuration Reference

See `config/config.yaml` for all configuration options.
