# Standard 3-Tier Web Application

## Overview

The Standard 3-Tier Web Application pattern is designed for web applications that require high availability, scalability, and proper security segmentation. This pattern separates concerns into three distinct tiers: presentation (web), application logic (app), and data storage (database).

## Architecture Components

### Web Tier
- **Purpose**: Serves static content and handles initial client requests
- **Instances**: Minimum 2 (for HA)
- **Load Balancing**: Application Load Balancer (ALB)
- **Instance Type**: t3.medium (recommended)
- **Security**: HTTPS only, WAF protection

### Application Tier
- **Purpose**: Executes business logic and processes requests
- **Instances**: Minimum 2 (for HA)
- **Load Balancing**: Internal load balancer
- **Instance Type**: t3.large (recommended)
- **Security**: Internal only, encrypted communication

### Database Tier
- **Purpose**: Persistent data storage
- **Instances**: 1 primary + standby (Multi-AZ)
- **Engine**: PostgreSQL 14+ (recommended)
- **Instance Type**: r5.large (memory-optimized)
- **Security**: Encryption at rest and in transit, automated backups

## Network Flow

```
Internet → ALB → Web Tier → App Tier → Database Tier
```

**Important**: Web tier MUST NOT directly communicate with database tier. All database access must go through the application tier.

## Security Requirements

1. **Encryption**
   - All production databases must be encrypted at rest
   - TLS 1.2+ for all inter-tier communication

2. **Network Segmentation**
   - Web tier: Public subnet (internet-facing)
   - App tier: Private subnet (no direct internet access)
   - Database tier: Private subnet (database subnet group)

3. **Access Control**
   - Security groups enforce tier isolation
   - Database only accessible from app tier
   - Web tier only accepts HTTPS traffic

## Compliance

This pattern is compliant with:
- PCI-DSS (Payment Card Industry Data Security Standard)
- SOX (Sarbanes-Oxley Act)
- SOC2 (Service Organization Control 2)

## Deployment

### Prerequisites
- VPC with public and private subnets across multiple AZs
- Route53 hosted zone (for DNS)
- ACM certificate (for HTTPS)

### Terraform Usage

See `pattern.yaml` for Terraform module usage.

## Monitoring & Operations

### Key Metrics
- Request latency (ALB → Web → App → DB)
- Error rates per tier
- Resource utilization (CPU, memory, disk)
- Database connection pool usage

### Backup & Recovery
- Automated daily backups (7-day retention minimum)
- Point-in-time recovery enabled
- Cross-region backup replication (for DR)

## Cost Considerations

Typical monthly cost for production deployment:
- **Small**: ~$500/month (2 web, 2 app, 1 db.t3.medium)
- **Medium**: ~$1,500/month (4 web, 4 app, 1 db.r5.large)
- **Large**: ~$5,000/month (8 web, 8 app, 1 db.r5.2xlarge)

## Support

For questions or support, contact the Enterprise Architecture Team.
