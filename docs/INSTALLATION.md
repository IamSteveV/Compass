# Installation Guide

Complete installation instructions for the Architecture Validation & Pattern Management System.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Installation](#detailed-installation)
  - [1. Local Development Setup](#1-local-development-setup)
  - [2. Docker Installation](#2-docker-installation)
  - [3. Production Deployment](#3-production-deployment)
- [Configuration](#configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

---

## Prerequisites

### System Requirements

**Minimum Requirements:**
- **OS**: Linux, macOS, or Windows 10/11
- **RAM**: 2 GB minimum, 4 GB recommended
- **Disk Space**: 500 MB for application and dependencies
- **CPU**: 2 cores minimum

**Software Requirements:**
- **Python**: 3.10 or higher (3.11 recommended)
- **pip**: Latest version (22.0+)
- **Git**: 2.0 or higher
- **(Optional) Docker**: 20.10+ and Docker Compose 2.0+
- **(Optional) Graphviz**: For diagram generation

### Check Prerequisites

```bash
# Check Python version
python --version  # or python3 --version
# Expected: Python 3.10.x or higher

# Check pip version
pip --version  # or pip3 --version
# Expected: pip 22.x or higher

# Check Git
git --version
# Expected: git version 2.x

# (Optional) Check Docker
docker --version
docker compose version
```

### Upgrading Prerequisites

**Python (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
```

**Python (macOS with Homebrew):**
```bash
brew install python@3.10
```

**Python (Windows):**
Download from [python.org](https://www.python.org/downloads/)

---

## Quick Start

For those who want to get started immediately:

```bash
# Clone the repository
git clone https://github.com/yourorg/compass.git
cd Compass

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Initialize database
python -c "from src.database.session import init_db; init_db()"

# Start the application
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 5000
```

**Access the application:**
- Web UI: http://localhost:5000/static/index.html
- Dashboard: http://localhost:5000/static/dashboard.html
- API Docs: http://localhost:5000/api/docs

---

## Detailed Installation

### 1. Local Development Setup

#### Step 1: Clone the Repository

```bash
# Using HTTPS
git clone https://github.com/yourorg/compass.git
cd Compass

# Or using SSH
git clone git@github.com:yourorg/compass.git
cd Compass
```

#### Step 2: Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Verify activation:**
```bash
which python  # Linux/macOS
where python  # Windows
# Should point to venv directory
```

#### Step 3: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

**Expected packages (43 total):**
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- sqlalchemy==2.0.23
- pydantic==2.5.0
- psutil==5.9.6
- [... and 38 more]

#### Step 4: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit configuration (use your preferred editor)
nano .env  # or vim, code, etc.
```

**Required configuration (.env):**
```bash
# Application
APP_ENV=development
APP_DEBUG=true

# ServiceNow CMDB (optional, for CMDB integration)
SERVICENOW_INSTANCE=your-instance.service-now.com
SERVICENOW_USERNAME=your-username
SERVICENOW_PASSWORD=your-password

# Database (optional, defaults to SQLite)
DATABASE_URL=sqlite:///./validation.db

# Patterns Repository
PATTERNS_REPO_PATH=./patterns
```

#### Step 5: Initialize Database

```bash
# Create database tables
python -c "from src.database.session import init_db; init_db()"

# Verify database creation
ls -la validation.db  # Should show the database file
```

#### Step 6: Load Pattern Library

```bash
# Patterns are already in ./patterns directory
# Verify patterns exist
ls -la patterns/reference-architectures/
# Should show: 3-tier-web, microservices, ha-database
```

#### Step 7: Start the Application

**Development mode (with auto-reload):**
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 5000
```

**Production mode:**
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 5000 --workers 4
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Initializing database...
INFO:     Database initialized successfully
INFO:     Application startup complete.
```

#### Step 8: Verify Installation

Open browser to:
- **Web UI**: http://localhost:5000/static/index.html
- **Health Check**: http://localhost:5000/health
- **API Docs**: http://localhost:5000/api/docs

---

### 2. Docker Installation

#### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

#### Step 1: Clone Repository

```bash
git clone https://github.com/yourorg/compass.git
cd Compass
```

#### Step 2: Configure Environment

```bash
cp .env.example .env
# Edit .env as needed
```

#### Step 3: Build Docker Image

```bash
# Build the image
docker build -t compass:latest .

# Verify image
docker images | grep compass
```

#### Step 4: Run with Docker Compose

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Check status
docker compose ps
```

**docker-compose.yml services:**
- `app`: FastAPI application (port 5000)
- `db`: PostgreSQL database (optional, if configured)

#### Step 5: Access Application

- **Web UI**: http://localhost:5000/static/index.html
- **API**: http://localhost:5000/api/docs

#### Docker Commands Reference

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# Restart services
docker compose restart

# View logs
docker compose logs -f app

# Execute commands in container
docker compose exec app python -m pytest

# Rebuild after code changes
docker compose up -d --build

# Clean up everything
docker compose down -v --remove-orphans
```

---

### 3. Production Deployment

#### Option A: Systemd Service (Linux)

**Step 1: Install to /opt**

```bash
sudo mkdir -p /opt/compass
sudo cp -r . /opt/compass/
cd /opt/compass

# Create virtual environment
sudo python3 -m venv venv
sudo venv/bin/pip install -r requirements.txt
```

**Step 2: Create systemd service**

```bash
sudo nano /etc/systemd/system/compass.service
```

**Service file content:**
```ini
[Unit]
Description=Architecture Validation & Pattern Management System
After=network.target

[Service]
Type=simple
User=compass
Group=compass
WorkingDirectory=/opt/compass
Environment="PATH=/opt/compass/venv/bin"
ExecStart=/opt/compass/venv/bin/uvicorn src.api.main:app --host 0.0.0.0 --port 5000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Step 3: Create user and set permissions**

```bash
sudo useradd -r -s /bin/false compass
sudo chown -R compass:compass /opt/compass
```

**Step 4: Start service**

```bash
sudo systemctl daemon-reload
sudo systemctl enable compass
sudo systemctl start compass
sudo systemctl status compass
```

#### Option B: Nginx Reverse Proxy

**Install Nginx:**
```bash
sudo apt install nginx
```

**Configure Nginx:**
```bash
sudo nano /etc/nginx/sites-available/compass
```

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name compass.yourdomain.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/compass/static;
        expires 30d;
    }
}
```

**Enable and restart:**
```bash
sudo ln -s /etc/nginx/sites-available/compass /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Option C: Kubernetes Deployment

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: compass
spec:
  replicas: 3
  selector:
    matchLabels:
      app: compass
  template:
    metadata:
      labels:
        app: compass
    spec:
      containers:
      - name: compass
        image: compass:latest
        ports:
        - containerPort: 5000
        env:
        - name: APP_ENV
          value: "production"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: compass-service
spec:
  selector:
    app: compass
  ports:
  - port: 80
    targetPort: 5000
  type: LoadBalancer
```

**Deploy:**
```bash
kubectl apply -f deployment.yaml
kubectl get pods
kubectl get services
```

---

## Configuration

### Environment Variables

**Core Settings:**
```bash
# Application environment
APP_ENV=production              # development | production
APP_DEBUG=false                 # true | false
LOG_LEVEL=INFO                  # DEBUG | INFO | WARNING | ERROR

# Server settings
HOST=0.0.0.0
PORT=5000
WORKERS=4
```

**Database Configuration:**
```bash
# SQLite (default)
DATABASE_URL=sqlite:///./validation.db

# PostgreSQL (production recommended)
DATABASE_URL=postgresql://user:password@localhost:5432/compass

# Connection pool
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
```

**ServiceNow Integration:**
```bash
SERVICENOW_INSTANCE=your-instance.service-now.com
SERVICENOW_USERNAME=api_user
SERVICENOW_PASSWORD=secure_password
SERVICENOW_TIMEOUT=30
```

**Pattern Library:**
```bash
PATTERNS_REPO_PATH=./patterns
PATTERNS_AUTO_RELOAD=true
```

**Validation Engine:**
```bash
VALIDATION_PARALLEL_EXECUTION=true
VALIDATION_MAX_WORKERS=4
VALIDATION_FAIL_ON_CRITICAL=true
```

### config.yaml

Advanced configuration in `config/config.yaml`:

```yaml
validation:
  severity_levels:
    - critical
    - high
    - medium
    - low
  fail_on_critical: true
  parallel_execution: true
  max_workers: 4

approval:
  routing:
    fast_track_threshold: 0.95
    standard_review_threshold: 0.85

patterns:
  directory: "./patterns"
  auto_reload: true

servicenow:
  timeout: 30
  verify_ssl: true
```

---

## Verification

### 1. Health Check

```bash
curl http://localhost:5000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "version": "0.3.0",
  "timestamp": "2025-01-17T12:00:00Z",
  "python_version": "3.10.0",
  "components": {
    "validation_engine": {
      "status": "healthy",
      "rules_count": 15
    },
    "pattern_library": {
      "status": "healthy",
      "patterns_count": 3
    },
    "database": {
      "status": "healthy",
      "type": "sqlite"
    }
  }
}
```

### 2. System Metrics

```bash
curl http://localhost:5000/metrics
```

### 3. API Documentation

Visit: http://localhost:5000/api/docs

Verify all endpoints are listed:
- `/api/validate/terraform`
- `/api/patterns/`
- `/api/analytics/dashboard/summary`
- etc.

### 4. Run Test Validation

**CLI Test:**
```bash
# Generate sample data first
python scripts/generate_sample_data.py --output-dir examples

# Run validation
python validate.py validate --terraform-plan examples/terraform_plan_3-tier.json
```

**Web UI Test:**
1. Navigate to http://localhost:5000/static/index.html
2. Upload `examples/terraform_plan_3-tier.json`
3. Verify results display correctly
4. Check confetti animation appears (if compliance ≥95%)

### 5. Check Dashboard

Visit: http://localhost:5000/static/dashboard.html

Verify:
- System health indicator shows "healthy"
- Charts render correctly
- Auto-refresh toggle works
- Export button functions

### 6. Run Test Suite

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**Expected output:**
```
==================== test session starts ====================
collected 45 items

tests/unit/test_validation_engine.py ........... [ 24%]
tests/unit/test_pattern_matcher.py .......... [ 44%]
tests/integration/test_end_to_end.py ........ [ 62%]
tests/api/test_endpoints.py ................ [ 100%]

==================== 45 passed in 12.34s ====================
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Port Already in Use

**Error:**
```
ERROR: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find process using port 5000
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use a different port
uvicorn src.api.main:app --port 5001
```

#### Issue 2: Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or appropriate activation command

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
```

#### Issue 3: Database Connection Error

**Error:**
```
sqlalchemy.exc.OperationalError: unable to open database file
```

**Solution:**
```bash
# Check database file permissions
ls -la validation.db

# Recreate database
rm validation.db
python -c "from src.database.session import init_db; init_db()"

# For PostgreSQL, verify connection
psql -h localhost -U username -d compass
```

#### Issue 4: Pattern Library Not Loading

**Error:**
```
Pattern library empty or patterns not found
```

**Solution:**
```bash
# Verify patterns directory exists
ls -la patterns/reference-architectures/

# Check pattern YAML files
cat patterns/reference-architectures/3-tier-web/pattern.yaml

# Verify PATTERNS_REPO_PATH in .env
grep PATTERNS_REPO_PATH .env
```

#### Issue 5: ServiceNow Connection Timeout

**Error:**
```
requests.exceptions.Timeout: HTTPSConnectionPool
```

**Solution:**
```bash
# Test ServiceNow connectivity
curl -u username:password https://your-instance.service-now.com/api/now/table/cmdb_ci?sysparm_limit=1

# Increase timeout in .env
SERVICENOW_TIMEOUT=60

# Check firewall/proxy settings
```

#### Issue 6: Permission Denied (Linux)

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:**
```bash
# Fix ownership
sudo chown -R $USER:$USER .

# Fix permissions
chmod -R 755 .
chmod 644 *.py
```

#### Issue 7: Python Version Mismatch

**Error:**
```
SyntaxError: invalid syntax (related to type hints)
```

**Solution:**
```bash
# Check Python version
python --version

# Use python3.10 explicitly
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Debug Mode

**Enable debug logging:**

```bash
# In .env
APP_DEBUG=true
LOG_LEVEL=DEBUG

# Run with verbose output
uvicorn src.api.main:app --reload --log-level debug
```

**Check logs:**
```bash
# Application logs
tail -f logs/app.log

# Uvicorn access logs
uvicorn src.api.main:app --access-log
```

### Performance Issues

**Database slow?**
```bash
# Add indexes (for PostgreSQL)
# Create migration
alembic revision -m "add_indexes"

# In migration file:
op.create_index('idx_validation_timestamp', 'validation_history', ['timestamp'])
op.create_index('idx_pattern_id', 'validation_history', ['pattern_id'])
```

**High memory usage?**
```bash
# Reduce workers
uvicorn src.api.main:app --workers 2

# Check memory with psutil
python -c "import psutil; print(psutil.Process().memory_info())"
```

### Getting Help

1. **Check documentation**: Review docs/ directory
2. **Search issues**: https://github.com/yourorg/compass/issues
3. **Check logs**: Review application and server logs
4. **Run diagnostics**: Use `/health` and `/metrics` endpoints
5. **Create issue**: Include logs, environment details, and steps to reproduce

---

## Uninstallation

### Local Development

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv/

# Remove database
rm validation.db

# Remove the entire directory
cd ..
rm -rf Compass/
```

### Docker

```bash
# Stop and remove containers
docker compose down -v --remove-orphans

# Remove images
docker rmi compass:latest

# Remove volumes
docker volume prune
```

### Systemd Service

```bash
# Stop and disable service
sudo systemctl stop compass
sudo systemctl disable compass

# Remove service file
sudo rm /etc/systemd/system/compass.service
sudo systemctl daemon-reload

# Remove application
sudo rm -rf /opt/compass

# Remove user
sudo userdel compass
```

### Nginx

```bash
# Remove configuration
sudo rm /etc/nginx/sites-enabled/compass
sudo rm /etc/nginx/sites-available/compass
sudo systemctl restart nginx
```

---

## Next Steps

After successful installation:

1. **Read User Guide**: See [USER_GUIDE.md](USER_GUIDE.md)
2. **Try Quick Demo**: See [QUICK_DEMO.md](QUICK_DEMO.md)
3. **Explore API**: Visit http://localhost:5000/api/docs
4. **Review Architecture**: See [ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md)
5. **Configure Patterns**: Customize patterns in `patterns/` directory
6. **Set up CI/CD**: Configure validation in your pipeline

---

## Support

- **Documentation**: See `docs/` directory
- **GitHub Issues**: https://github.com/yourorg/compass/issues
- **API Reference**: http://localhost:5000/api/docs
- **Health Check**: http://localhost:5000/health

---

*Installation guide for Architecture Validation & Pattern Management System v0.3.0*
