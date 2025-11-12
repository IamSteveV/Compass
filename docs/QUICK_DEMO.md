# Quick Demo Guide

## 5-Minute Demo of Architecture Validation System

This guide walks you through a quick demonstration of the system's key features.

### Prerequisites
```bash
cd Compass
pip install -r requirements.txt
```

### Step 1: Generate Sample Data (30 seconds)

```bash
# Generate sample Terraform plans and CMDB applications
python scripts/generate_sample_data.py --output-dir examples

# You should see:
# Generated: examples/sample_3_tier_plan.json
# Generated: examples/sample_3_tier_cmdb.json
# Generated: examples/sample_microservices_plan.json
# ... etc
```

### Step 2: List Available Patterns (10 seconds)

```bash
python validate.py patterns

# Output:
# ┌─────────┬──────────────────────────────────┬─────────┬──────────┐
# │ ID      │ Name                             │ Version │ Status   │
# ├─────────┼──────────────────────────────────┼─────────┼──────────┤
# │ PAT-001 │ Standard 3-Tier Web Application  │ 1.0     │ approved │
# │ PAT-002 │ Microservices Architecture       │ 1.0     │ approved │
# │ COMP-001│ High Availability Database       │ 1.0     │ approved │
# └─────────┴──────────────────────────────────┴─────────┴──────────┘
```

### Step 3: View Validation Rules (10 seconds)

```bash
python validate.py rules

# Output shows all 15 rules with categories and severities
```

### Step 4: Validate Terraform Plan (30 seconds)

```bash
python validate.py validate --terraform-plan examples/sample_3_tier_plan.json

# Output:
# ═══════════════════════════════════════════
#         Validation Results
# ═══════════════════════════════════════════
# 
# Pattern Match: Standard 3-Tier Web Application
# Match Score: 92%
# Approval Track: STANDARD REVIEW
# 
# ✓ Passed: 12
# ⚠ Warnings: 2
# ✗ Violations: 0
# 
# Compliance Score: 92%
# ...
```

### Step 5: Start Web Application (1 minute)

```bash
# Terminal 1: Start the server
python app.py

# Wait for: "Uvicorn running on http://0.0.0.0:5000"
```

### Step 6: Use Web Interface (2 minutes)

Open browser to: http://localhost:5000

**Try These:**

1. **Upload a Terraform Plan**
   - Click "Terraform Plan" tab
   - Upload `examples/sample_3_tier_plan.json`
   - Click "Validate"
   - See results with pattern match and violations

2. **Browse Patterns**
   - Click "Patterns" in navigation
   - Click on "Standard 3-Tier Web Application"
   - View components, constraints, and Terraform module

3. **View Dashboard** (if validations exist)
   - Click "Dashboard" in navigation
   - See compliance metrics
   - View charts and trends

### Step 7: Try the API (30 seconds)

Open: http://localhost:5000/api/docs

**Interactive API Documentation:**

1. Expand "POST /api/validate/terraform"
2. Click "Try it out"
3. Upload sample file
4. Click "Execute"
5. See JSON response

### Sample Use Cases

#### Use Case 1: Validate Before Deployment
```bash
# In your Terraform directory
terraform plan -out=tfplan.binary
terraform show -json tfplan.binary > tfplan.json

# Validate
python validate.py validate --terraform-plan tfplan.json

# Check exit code
echo $?  # 0 = passed, 1 = failed
```

#### Use Case 2: Pattern Matching
```bash
# Generate a microservices plan
python validate.py validate --terraform-plan examples/sample_microservices_plan.json

# Should match PAT-002: Microservices Architecture
```

#### Use Case 3: CI/CD Integration
```yaml
# .github/workflows/terraform.yml
- name: Validate Architecture
  run: |
    terraform show -json tfplan.binary > tfplan.json
    python validate.py validate --terraform-plan tfplan.json --output report.json
    
- name: Check Compliance
  run: |
    SCORE=$(jq -r '.summary.compliance_score' report.json)
    if (( $(echo "$SCORE < 0.8" | bc -l) )); then
      echo "Compliance too low: $SCORE"
      exit 1
    fi
```

## Demo Script for Presentation

### Introduction (1 minute)
"We've built a system that validates infrastructure against architectural standards and matches deployments against pre-approved patterns."

### Live Demo (4 minutes)

1. **Show the Problem** (30 sec)
   - "Manual architecture reviews are slow and inconsistent"
   - "Violations discovered after deployment are expensive"

2. **Generate Test Data** (30 sec)
   ```bash
   python scripts/generate_sample_data.py
   ```
   - "We can generate realistic test data for any pattern"

3. **CLI Validation** (1 min)
   ```bash
   python validate.py validate --terraform-plan examples/sample_3_tier_plan.json
   ```
   - "15 validation rules check security, compliance, and best practices"
   - "Pattern matching identifies 92% similarity to approved 3-tier pattern"
   - "Automatic approval routing: this would get standard review"

4. **Web Interface** (1 min)
   - Open http://localhost:5000
   - Upload plan file
   - "User-friendly interface for non-technical stakeholders"
   - "Visual results with clear action items"

5. **Dashboard & Analytics** (1 min)
   - Open http://localhost:5000/static/dashboard.html
   - "Track compliance over time"
   - "Identify most common violations"
   - "Monitor pattern adoption"

### Key Benefits (30 seconds)
- **Fast**: Validation in < 30 seconds
- **Consistent**: Same rules every time
- **Early**: Catch issues before deployment
- **Trackable**: Full audit trail
- **Automated**: Integrate with CI/CD

## Testing Different Scenarios

### Compliant Infrastructure
```bash
# 3-tier with all best practices
python validate.py validate --terraform-plan examples/sample_3_tier_plan.json
# Expected: High compliance, fast-track or standard review
```

### Non-Compliant Infrastructure
Create a test file with violations:
```json
{
  "resources": [{
    "type": "database",
    "environment": "production",
    "encrypted": false,  # Violation!
    "backup_enabled": false  # Violation!
  }]
}
```

```bash
python validate.py validate --terraform-plan test_violations.json
# Expected: Multiple critical violations
```

### Pattern Mismatch
```bash
# Try validating microservices as 3-tier
# Should show lower similarity score
```

## Stopping the Demo

```bash
# Stop the web server
Ctrl+C in the terminal running app.py

# Clean up (optional)
rm -rf examples/
rm -rf __pycache__/
```

## Next Steps

After the demo:
1. Read the [User Guide](USER_GUIDE.md)
2. Explore the [API Documentation](API.md)
3. Review the [Complete Feature List](FEATURES.md)
4. Check out [Integration Examples](../tests/integration/)

## Troubleshooting Demo Issues

**"ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

**"Port already in use"**
```bash
# Change port
export APP_PORT=5001
python app.py
```

**"No patterns found"**
```bash
# Check patterns directory
ls patterns/reference-architectures/
```

**"Database initialization failed"**
```bash
# SQLite should work without config
# Error is non-fatal for demo
```
