# Compass Design Guidelines
**Enterprise Architecture Validation & Pattern Management System**

## Design Approach
**Selected System**: Carbon Design System (IBM)  
**Justification**: Purpose-built for data-intensive enterprise applications with complex information hierarchies. Provides proven patterns for dashboards, data tables, and analytics visualization.

**Core Principles**:
- Data clarity over decoration
- Immediate access to functionality
- Scannable information hierarchy
- Professional restraint

---

## Typography System

**Font Stack**: IBM Plex Sans via Google Fonts CDN
- **Headings**: Plex Sans Medium (500)
  - Page titles: text-2xl (24px)
  - Section headers: text-xl (20px)
  - Card headers: text-lg (18px)
- **Body**: Plex Sans Regular (400)
  - Primary text: text-base (16px)
  - Secondary text: text-sm (14px)
  - Captions/metadata: text-xs (12px)
- **Data/Code**: IBM Plex Mono Regular
  - Metrics: text-3xl to text-5xl (bold weight)
  - Code snippets: text-sm

---

## Layout System

**Spacing Units**: Tailwind 4, 6, 8, 12, 16 for consistent rhythm
- Component padding: p-6
- Card spacing: gap-6
- Section margins: mb-8 to mb-12
- Page padding: p-8 on desktop, p-4 on mobile

**Grid Structures**:
- Dashboard metrics: 4-column grid (lg:grid-cols-4 md:grid-cols-2)
- Content sections: 12-column foundation with 2-column sidebar layouts
- Data tables: Full-width with horizontal scroll
- Analytics charts: 2-column grid for comparisons

**Container Strategy**:
- Max-width: max-w-7xl for main content
- Sidebar: fixed w-64 on desktop, collapsible on mobile
- Full-bleed sections for tables and visualizations

---

## Component Library

### Navigation
**Top Bar**: Fixed header with logo, global search, notifications, user profile
- Height: h-16
- Contains: breadcrumb navigation for context
- Actions: Quick validation trigger, settings access

**Sidebar Navigation**: Category-based with icons
- Categories: Dashboard, Pattern Library, Validation, Rules (Security, Metadata, Technology, Resilience, Network, Cost), Analytics
- Active state: border-l-4 accent with subtle background
- Icons: Heroicons outline style
- Collapsible on mobile with hamburger menu

### Dashboard Components
**Metric Cards**: Elevated cards with clear hierarchy
- Large numeric value (text-4xl font-bold)
- Label (text-sm opacity-70)
- Trend indicator with icon (up/down arrow)
- Optional sparkline chart
- Padding: p-6, rounded-lg, shadow-sm

**Status Indicators**:
- Compliance score: Circular progress with percentage
- Pass/Fail badges: Rounded pills with icons
- Severity levels: Dot indicators (critical/high/medium/low)

**Charts & Visualizations**:
- Use Recharts or Chart.js libraries
- Bar charts: Compliance by category
- Line graphs: Trend analysis over time  
- Donut charts: Distribution breakdowns
- Consistent axis labels and legends

### Pattern Library Browser
**Card Grid Layout**: 3-column responsive grid
- Pattern cards: Image preview, title, category badge, description snippet
- Hover: Subtle elevation increase (shadow-md to shadow-lg)
- Quick actions: View, Edit, Clone icons

**Detail View**: Split layout
- Left: Pattern visualization/diagram (60%)
- Right: Metadata, tags, validation rules (40%)
- Tabs: Overview, Rules, History, Dependencies

### Validation Results
**Results Table**: Striped rows with expandable details
- Columns: Pattern, Status, Severity, Issues Found, Last Validated
- Inline actions: Re-validate, View Details, Export
- Expandable rows show detailed findings
- Sticky header on scroll

**Visual Results Panel**:
- Split view: Code/diagram on left, violations highlighted
- Right panel: Issue list with line numbers
- Annotations: Tooltip overlays on problem areas

### Rules Browser
**Accordion Categories**: Expandable sections per category
- Category header: Icon, title, rule count badge
- Rule items: Title, description, severity indicator
- Search/filter bar at top
- Tag filters: Technology, compliance framework

### Data Tables
**Standard Pattern**:
- Zebra striping (subtle)
- Sortable columns with arrow indicators
- Pagination: Items per page selector, page navigation
- Bulk actions: Checkbox selection with action bar
- Empty states: Centered illustration with action prompt

### Forms & Inputs
**Validation Forms**:
- Label above input (text-sm font-medium)
- Input fields: border rounded-md h-10 px-4
- Helper text below (text-xs)
- Error states: red border with error icon
- Multi-select: Dropdown with tags

### Modals & Overlays
**Modal Pattern**:
- Backdrop: Semi-transparent overlay
- Content: max-w-2xl centered, shadow-xl
- Header: Title, close button (×)
- Footer: Action buttons (Cancel left, Primary right)
- Scrollable body for long content

---

## Images & Assets

**Icons**: Heroicons (outline style) via CDN
- Navigation: 20px (w-5 h-5)
- Inline actions: 16px (w-4 h-4)  
- Large features: 24px (w-6 h-6)

**Hero Section**: No traditional hero image
- Dashboard opens immediately to metrics and data
- Optional: Subtle abstract geometric pattern background for login/empty states

**Illustrations**:
- Empty states: Simple line illustrations (undraw.co style)
- Error states: Friendly error icons
- Loading states: Skeleton screens, not spinners

---

## Page Structures

**Dashboard**: No scroll required for key metrics
- Top: 4 metric cards (compliance score, total patterns, active validations, issues)
- Middle: 2-column charts (compliance trends, category breakdown)
- Bottom: Recent validations table (5 rows)

**Pattern Library**: Search-first interface
- Sticky search/filter bar
- 3-column card grid, infinite scroll or pagination
- Sidebar filters: Category, technology, status

**Validation Engine**: Action-oriented layout
- Top: Validation controls (pattern selector, trigger button)
- Results: Split-screen with visual + tabular views
- Export options: PDF, JSON, CSV

**Rules Browser**: Organized by category
- Left sidebar: Category navigation
- Main: Rule cards with expandable details
- Right panel: Applied filters, recent activity

**Analytics**: Dashboard-style charts
- Flexible grid allowing 1, 2, or 3 columns per row
- Date range selector at top
- Export/share options per chart

---

## Accessibility & Interactions

- Focus states: Visible ring on all interactive elements
- Keyboard navigation: Full support with logical tab order
- ARIA labels: All icons and actions
- Animations: Minimal - only state transitions (150-200ms ease)
- Responsive: Mobile-first with sidebar collapse, stacked layouts

---

**Quality Mandate**: Comprehensive, production-ready implementation with all sections fully realized. Professional polish with attention to enterprise usability standards.