# UI Capabilities Gap Analysis

## Overview
This document identifies API/CLI capabilities that are not yet available in the web UI and provides an implementation roadmap.

## Current Status (v0.4.0)

### ✅ Available in UI
1. **Terraform Plan Validation** - Upload and validate Terraform plan files
2. **CMDB Validation** - Query and validate CMDB applications
3. **Pattern Browsing** - View approved architecture patterns
4. **Notifications** - Configure and test email notifications
5. **PDF Reports** - Download validation reports as PDF
6. **Report Export** - Copy and download reports as JSON

### ❌ Missing from UI

#### 1. Terraform Cloud Integration (HIGH PRIORITY)
**API Endpoints Available:**
- `GET /api/terraform/cloud/test` - Test connection
- `POST /api/terraform/cloud/workspaces` - List workspaces
- `POST /api/terraform/cloud/workspace/analyze` - Analyze workspace
- `POST /api/terraform/cloud/workspace/validate` - Validate workspace

**UI Needed:**
- Terraform Cloud configuration panel
- Workspace browser
- Workspace analysis viewer
- Workspace validation with results

#### 2. Terraform State File Analysis (HIGH PRIORITY)
**API Endpoints Available:**
- `POST /api/terraform/state/analyze` - Analyze state file
- `POST /api/terraform/state/validate` - Validate state file

**UI Needed:**
- State file upload interface
- State analysis results viewer
- Resource categorization display
- Security findings viewer
- Cost drivers visualization

#### 3. Resource Graph Visualization (MEDIUM PRIORITY)
**API Endpoints Available:**
- `POST /api/terraform/graph/generate` - Generate graphs (JSON, Mermaid, DOT)
- `POST /api/terraform/graph/stats` - Graph statistics
- `POST /api/terraform/analyze/circular-dependencies` - Find cycles

**UI Needed:**
- Interactive resource graph visualizer
- Dependency tree viewer
- Circular dependency highlighter
- Graph export options

#### 4. Analytics Dashboard (MEDIUM PRIORITY)
**API Endpoints Available:**
- `GET /api/analytics/dashboard/summary` - Dashboard summary
- `GET /api/analytics/compliance/overview` - Compliance overview
- `GET /api/analytics/patterns/adoption` - Pattern adoption stats
- `GET /api/analytics/patterns/popular` - Popular patterns
- `GET /api/analytics/violations/top-rules` - Top violations

**UI Needed:**
- Compliance metrics dashboard
- Pattern adoption charts
- Violation trends
- Top violations table

#### 5. Validation History (MEDIUM PRIORITY)
**API Endpoints Available:**
- `GET /api/history/validations/recent` - Recent validations
- `GET /api/history/validations/{validation_id}` - Specific validation
- `GET /api/history/validations/application/{application_name}` - By application
- `GET /api/history/violations/application/{application_name}` - By application
- `POST /api/history/save` - Save validation

**UI Needed:**
- Validation history timeline
- Filter by application/date/status
- Historical trend charts
- Compare validations

#### 6. Pattern Search (LOW PRIORITY)
**API Endpoints Available:**
- `GET /api/patterns/search/{query}` - Search patterns

**UI Needed:**
- Enhanced search bar with filters
- Search results with relevance scoring
- Filter by category/status

## Implementation Roadmap

### Phase 1: Terraform Integration (Week 1-2)
Priority: HIGH
**Deliverables:**
1. Add "Terraform Cloud" navigation item
2. Create Terraform Cloud workspace browser
3. Add state file analyzer UI
4. Implement workspace validation flow

**Files to Create/Modify:**
- `static/index.html` - Add Terraform section
- `static/js/terraform.js` - New file for Terraform UI logic
- `static/css/style.css` - Styling for new components

### Phase 2: Analytics & History (Week 3)
Priority: MEDIUM
**Deliverables:**
1. Enhance dashboard with analytics
2. Add validation history viewer
3. Create compliance trend charts
4. Add violation tracking

**Files to Create/Modify:**
- `static/dashboard.html` - Enhanced with analytics
- `static/js/dashboard.js` - Add analytics functions
- Create `static/js/history.js` - History viewer

### Phase 3: Visualization (Week 4)
Priority: MEDIUM
**Deliverables:**
1. Resource graph visualizer
2. Dependency tree viewer
3. Interactive diagrams

**Files to Create/Modify:**
- Create `static/visualizer.html` - Dedicated page
- Create `static/js/visualizer.js` - Graph rendering
- Add Mermaid.js or D3.js library

### Phase 4: Search & Polish (Week 5)
Priority: LOW
**Deliverables:**
1. Enhanced pattern search
2. UI/UX improvements
3. Mobile responsiveness

## Quick Wins (Immediate Implementation)

### 1. Add Terraform State File Upload (30 minutes)
Add to existing Terraform validation tab:
```html
<li class="nav-item">
    <a class="nav-link" data-bs-toggle="tab" href="#terraform-state-tab">State File</a>
</li>
```

### 2. Add "View Analytics" Link (15 minutes)
Link existing dashboard to analytics endpoints.

### 3. Add History Sidebar (45 minutes)
Show recent validations in a collapsible sidebar.

## API Coverage Summary

| Category | Total Endpoints | UI Available | Coverage |
|----------|----------------|--------------|----------|
| Validation | 3 | 2 | 67% |
| Patterns | 7 | 2 | 29% |
| Analytics | 6 | 0 | 0% |
| History | 6 | 0 | 0% |
| Terraform | 10 | 1 | 10% |
| Notifications | 4 | 2 | 50% |
| Reports | 2 | 1 | 50% |
| **TOTAL** | **38** | **8** | **21%** |

## Recommendations

1. **Immediate:** Implement Terraform state file analyzer UI (highest value, moderate effort)
2. **Short-term:** Add analytics dashboard enhancement (high value, high effort)
3. **Medium-term:** Build resource graph visualizer (medium value, high effort)
4. **Long-term:** Complete validation history interface (medium value, medium effort)

## Technical Considerations

### JavaScript Libraries Needed
- **Mermaid.js** or **D3.js** - For graph visualization
- **Chart.js** (already included) - For charts and metrics
- **Moment.js** or **date-fns** - For date formatting in history

### Performance
- Implement pagination for history (50 items per page)
- Add caching for analytics data (5-minute TTL)
- Lazy load graph visualizations

### Mobile Responsiveness
- All new UI components must be responsive
- Use Bootstrap grid system consistently
- Test on mobile devices before release

## Next Steps

1. Review and prioritize with stakeholders
2. Create detailed UI mockups for Phase 1
3. Implement Terraform Cloud integration UI
4. Add comprehensive E2E tests for new UI features
5. Update user documentation

---

**Document Version:** 1.0
**Last Updated:** 2025-11-12
**Author:** Claude (Architecture Validation System)
