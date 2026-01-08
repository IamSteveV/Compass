# Compass - Architecture Validation System

A comprehensive Architecture Validation & Pattern Management System for validating infrastructure against architectural standards.

## Overview

Compass is a Compliance and Pattern Assessment System that provides:
- **Validation Engine**: Validate infrastructure against 15+ architectural rules
- **Pattern Library**: Pre-approved architecture patterns (3-tier, microservices, HA database)
- **Pattern Matching**: Automatically identify matching patterns with similarity scores
- **Approval Routing**: Fast-track, Standard, or Full Review based on pattern match
- **Analytics Dashboard**: Compliance metrics, trends, and violation tracking

## Tech Stack

- **Frontend**: React with TypeScript, Vite, TanStack Query, Recharts
- **Backend**: Express.js with TypeScript
- **Styling**: Tailwind CSS, shadcn/ui components
- **Fonts**: IBM Plex Sans, IBM Plex Mono

## Project Structure

```
├── client/src/
│   ├── components/
│   │   ├── ui/           # shadcn components
│   │   ├── app-sidebar.tsx
│   │   └── theme-provider.tsx
│   ├── pages/
│   │   ├── dashboard.tsx  # Main dashboard with metrics
│   │   ├── patterns.tsx   # Pattern library browser
│   │   ├── validation.tsx # Validation engine
│   │   ├── rules.tsx      # Rules browser by category
│   │   └── analytics.tsx  # Analytics dashboard
│   └── App.tsx
├── server/
│   ├── routes.ts         # API endpoints
│   └── storage.ts        # In-memory storage with sample data
└── shared/
    └── schema.ts         # Zod schemas and TypeScript types
```

## API Endpoints

- `GET /api/patterns` - List all patterns
- `GET /api/patterns/:id` - Get single pattern
- `GET /api/rules` - List all validation rules
- `GET /api/rules/:id` - Get single rule
- `GET /api/validations` - List validation history
- `POST /api/validate` - Run validation
- `GET /api/analytics` - Get analytics data

## Validation Rules

15 rules across 6 categories:
- **Security** (4): Database encryption, DMZ isolation, backup requirements
- **Metadata** (2): Required tags, DR tier designation
- **Technology** (2): Approved database versions, instance types
- **Resilience** (2): Multi-AZ, automated backups
- **Network** (3): Subnet isolation, SSL/TLS, flow logs
- **Cost** (2): Unused resources, oversized instances

## Architecture Patterns

- **PAT-001**: Standard 3-Tier Web Application
- **PAT-002**: Microservices Architecture
- **COMP-001**: High Availability Database

## Features

- Dark/light mode toggle
- Real-time compliance scoring
- Pattern similarity matching
- Approval track recommendations
- Interactive charts and visualizations
- Responsive sidebar navigation

## Running the Application

The application runs on port 5000 with `npm run dev`.
