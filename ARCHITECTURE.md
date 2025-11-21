# Global Narratives System - Technical Architecture

**Last Updated:** October 31, 2025  
**Current Version:** v1.0 (Event Engine)

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Technology Stack](#technology-stack)
4. [Database Schema](#database-schema)
5. [File Structure](#file-structure)
6. [System Components](#system-components)
7. [Data Flow](#data-flow)
8. [Future Architecture Plans](#future-architecture-plans)

---

## System Overview

The Global Narratives System is built as a monolithic Flask application with PostgreSQL backend. The current architecture prioritizes:

- **Simplicity:** Single codebase, straightforward deployment
- **Flexibility:** Easy to modify and extend during active development
- **Clarity:** Clear separation between models, views, and controllers

As the system matures (v1.3+), we may consider microservices architecture for specific components like automated news ingestion or AI-assisted event coding.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   Web Interface (Flask)                 │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│ │  Articles    │ │   Events     │ │    AIPs      │    │
│ │  Dashboard   │ │  Creation    │ │  Management  │    │
│ └──────────────┘ └──────────────┘ └──────────────┘    │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│         Application Logic (Flask + Python)              │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│ │   Article    │ │    Event     │ │     AIP      │    │
│ │  Processing  │ │   Coding     │ │   Linking    │    │
│ └──────────────┘ └──────────────┘ └──────────────┘    │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│         Data Layer (SQLAlchemy ORM + PostgreSQL)        │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│ │   Articles   │ │    Events    │ │    Actors    │    │
│ │    Table     │ │    Table     │ │    Table     │    │
│ └──────────────┘ └──────────────┘ └──────────────┘    │
│ ┌──────────────┐ ┌──────────────┐                      │
│ │ Institutions │ │  Positions   │                      │
│ │    Table     │ │    Table     │                      │
│ └──────────────┘ └──────────────┘                      │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│               External Data Sources                     │
│ ┌──────────────┐ ┌──────────────┐                      │
│ │   News API   │ │  RSS Feeds   │                      │
│ └──────────────┘ └──────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend
- **Python 3.9+**
- **Flask 2.x** - Web framework
- **SQLAlchemy 2.x** - ORM for database interactions
- **WTForms** - Form handling and validation
- **feedparser** - RSS feed parsing

### Database
- **PostgreSQL 18** - Primary data store
  - Chosen for: JSON support, full-text search capabilities, robustness

### Frontend
- **Jinja2** - Template engine
- **HTML5/CSS3** - Markup and styling
- **Vanilla JavaScript** - Interactive elements (AJAX for article actions)
- **C3I-inspired aesthetic** - Dark theme, cyan/green accents

### Data Sources
- **News API** - International news aggregation
- **RSS Feeds** - Direct feeds from major outlets (Channel NewsAsia, SCMP, Reuters, Guardian)

### Future Considerations
- **Neo4j** (v1.3+) - Graph database for actor/event relationship networks
- **Elasticsearch** (v1.3+) - Advanced search and text analysis
- **Redis** (v1.2+) - Caching layer for frequent queries

---

## Database Schema

### Current Tables (v1.0)

#### `articles`
Stores collected news articles from various sources.

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer (PK) | Unique identifier |
| `title` | String(500) | Article headline |
| `description` | Text | Article summary/lead |
| `url` | String(500) | Source URL (unique) |
| `source_name` | String(200) | Publication name |
| `published_at` | DateTime | Publication timestamp |
| `content` | Text | Full article text |
| `collected_at` | DateTime | When article was ingested |
| `processed` | Boolean | Whether coded into events |
| `junk` | Boolean | Marked as irrelevant |

**Indexes:**
- `url` (unique)
- `published_at`
- `processed`, `junk` (for filtering)

#### `events`
Political events coded in CIE format.

| Column | Type | Description |
|--------|------|-------------|
| `event_code` | String(50) (PK) | CIE event code (e.ddmmyyyy.region.ordinal) |
| `event_date` | Date | Date of event |
| `region` | String(3) | Regional code (nam, mea, etc.) |
| `ordinal` | Integer | Daily sequence number |
| `recorded_timestamp` | Timestamp | When event was recorded |
| `core_action` | String(10) | Primary action code from CIE |
| `cie_description` | String(250) | Full CIE-formatted event |
| `natural_summary` | String(250) | Plain English description |
| `article_url` | String(500) | Reference to source article URL |
| `article_headline` | String(250) | Source article headline |
| `created_by` | String(100) | User who created event |

**Indexes:**
- `event_code` (primary key)
- `event_date`
- `region`
- `core_action`

#### `actors`
Individual political actors.

| Column | Type | Description |
|--------|------|-------------|
| `actor_id` | String(20) (PK) | Unique actor identifier |
| `surname` | String(150) | Last name / family name |
| `given_name` | String(150) | First name |
| `middle_name` | String(150) | Middle name(s) |
| `biographical_info` | Text | Background information |

**Indexes:**
- `actor_id` (primary key)
- `surname`
- `given_name`

#### `institutions`
Organizations, governments, agencies.

| Column | Type | Description |
|--------|------|-------------|
| `institution_code` | String(100) (PK) | Hierarchical institution code |
| `institution_name` | String(300) | Institution name |
| `country_code` | String(3) | ISO country code |
| `description` | Text | Institutional details |

**Indexes:**
- `institution_code` (primary key)
- `country_code`

#### `positions`
Formal roles/titles within institutions.

| Column | Type | Description |
|--------|------|-------------|
| `position_code` | String(100) (PK) | Position code |
| `position_title` | String(300) | Position title |
| `institution_code` | String(100) | Associated institution code |
| `hierarchy_level` | String(50) | Hierarchy level (executive, ministerial, etc.) |
| `description` | Text | Position details |

**Indexes:**
- `position_code` (primary key)
- `institution_code`
- `hierarchy_level`

**Note:** `institution_code` links to the `institutions` table's `institution_code` field.

#### `tenures`
Time-bound relationships between actors and positions.

| Column | Type | Description |
|--------|------|-------------|
| `tenure_id` | Serial (PK) | Unique identifier |
| `position_code` | String(100) | Position held |
| `actor_id` | String(20) | Actor holding position |
| `tenure_start` | Date | Tenure begins |
| `tenure_end` | Date (nullable) | Tenure ends (null = current) |

**Indexes:**
- `tenure_id` (primary key)
- `actor_id`
- `position_code`
- `tenure_start`, `tenure_end`
- Composite: `(actor_id, position_code, tenure_start)`

**Note:** Links actors to positions with start/end dates for historical tracking.

#### `event_actors`
Many-to-many relationship linking events to actors/institutions mentioned in CIE.

| Column | Type | Description |
|--------|------|-------------|
| `event_actor_id` | Serial (PK) | Unique identifier |
| `event_code` | String(50) | Event being linked |
| `code_id` | String(100) | Actor or institution code |
| `code_type` | String(20) | Type (actor, institution, position) |
| `role_type` | String(20) | Role in event (subject, object, reference) |

**Indexes:**
- `event_actor_id` (primary key)
- `event_code`
- `code_id`
- `code_type`
- `role_type`

**Note:** This junction table allows querying all events involving a specific actor or institution, critical for network analysis and actor-centric queries.

### Future Tables (v1.2+)

#### `scenarios` (v1.2)
Predictive scenarios with probability tracking.

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer (PK) | Unique identifier |
| `title` | String(500) | Scenario description |
| `initial_probability` | Float | Starting probability (0-1) |
| `current_probability` | Float | Current probability (0-1) |
| `resolution_date` | Date | When scenario resolves |
| `status` | String(50) | active, resolved-yes, resolved-no, expired |
| `created_at` | DateTime | Record creation |
| `resolved_at` | DateTime (nullable) | Resolution timestamp |

#### `event_scenarios` (v1.2)
Many-to-many: Events assigned to scenarios with weights.

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer (PK) | Unique identifier |
| `event_id` | Integer (FK) | Associated event |
| `scenario_id` | Integer (FK) | Associated scenario |
| `weight` | Integer | Impact weight (-7 to +7) |
| `assigned_at` | DateTime | Assignment timestamp |

#### `narratives` (v1.3+)
Higher-order narrative structures.

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer (PK) | Unique identifier |
| `title` | String(500) | Narrative name |
| `description` | Text | Detailed description |
| `start_date` | Date | Narrative begins |
| `end_date` | Date (nullable) | Narrative ends |
| `geographic_scope` | String(100) | Primary region(s) |
| `saliency` | Float | Importance measure |
| `status` | String(50) | active, dormant, resolved |

#### `event_references` (v1.3+)
Event-to-event relationships parsed from CIE `$` operators.

| Column | Type | Description |
|--------|------|-------------|
| `id` | Integer (PK) | Unique identifier |
| `source_event_id` | Integer (FK) | Event making reference |
| `target_event_id` | Integer (FK) | Event being referenced |
| `reference_type` | String(50) | Type of relationship |

---

## File Structure

```
event_engine_v1.0/
├── app.py                    # Main Flask application
├── models.py                 # SQLAlchemy database models
├── forms.py                  # WTForms form definitions
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
│
├── templates/                # Jinja2 HTML templates
│   ├── base.html            # Base template with layout
│   ├── articles.html        # Article dashboard
│   ├── create_event.html    # Event creation (split view)
│   └── manage_aips.html     # AIP management interface
│
├── static/                   # Static assets
│   ├── css/
│   │   └── style.css        # C3I-inspired styling
│   └── js/
│       └── app.js           # Interactive components
│
├── seed_data/                # CSV templates for bulk import
│   ├── actors.csv
│   ├── institutions.csv
│   ├── positions.csv
│   └── tenures.csv
│
├── scripts/                  # Utility scripts
│   └── import_seed_data.py  # [IN PROGRESS] CSV import
│
├── .env.example              # Environment variable template
├── .gitignore                # Git ignore patterns
└── README.md                 # Project documentation
```

---

## System Components

### 1. Article Collection Pipeline

**Purpose:** Automated ingestion of international news articles.

**Components:**
- News API client (pull from newsapi.org)
- RSS feed parsers (feedparser library)
- Deduplication logic (by URL)
- Manual trigger via web UI button

**Data Flow:**
1. Scheduled/manual collection trigger
2. Fetch articles from APIs/RSS feeds
3. Check for duplicates (URL matching)
4. Store in `articles` table
5. Display in dashboard for review

**Current Sources:**
- News API (configured sources)
- Channel NewsAsia RSS
- South China Morning Post RSS
- Reuters RSS
- The Guardian RSS

### 2. Event Coding Interface

**Purpose:** Manual creation of CIE-formatted events from source articles.

**Components:**
- Split-view interface (article | form)
- CIE text area with preserved formatting
- Natural language summary field
- Auto-generated event codes
- AIP selection dropdowns

**Features:**
- Textarea preserves indentation and line breaks for CIE
- Event codes auto-generate: `e.ddmmyyyy.region.ordinal`
- Region and date extracted from form inputs
- Source article linked for provenance

### 3. AIP Management System

**Purpose:** Maintain comprehensive database of actors, institutions, positions, tenures.

**Components:**
- Actor CRUD interface
- Institution hierarchy management
- Position creation and linking
- Tenure tracking with date ranges

**Key Features:**
- Hierarchical institution relationships (parent/child)
- Multi-tenure support (same actor, different periods)
- Status tracking (current, former, acting, interim)

---

## Data Flow

### News Collection Flow
```
External Sources → API/RSS Clients → Deduplication Check → Database Storage → Dashboard Display
```

### Event Creation Flow
```
Article Selection → Split View Display → CIE Coding → Validation → Event Storage → Source Linking
```

### AIP Lookup Flow
```
Event Creation Form → Actor/Institution Dropdowns → Database Query → Code Display → Event Link
```

---

## Future Architecture Plans

### Version 1.2 - Scenarios Layer

**New Components:**
- Scenario management interface
- Event-scenario assignment UI
- Probability calculation engine
- Temporal tracking system

**Architecture Changes:**
- Add `scenarios` and `event_scenarios` tables
- Implement probability update algorithms
- Build scenario resolution workflow

### Version 1.3+ - Advanced Features

**Potential Components:**
- **CIE Parser:** Automated validation and parsing of CIE syntax
- **Graph Database Layer:** Neo4j for actor/event relationship networks
- **Search Infrastructure:** Elasticsearch for full-text and structured search
- **API Layer:** RESTful API for external access
- **Authentication System:** Multi-user support with roles/permissions
- **Analytics Dashboard:** Visualization of trends, networks, probabilities

**Architecture Evolution:**
- Consider microservices for: news ingestion, AI-assisted coding, analytics
- Implement caching layer (Redis) for frequent queries
- Add message queue (RabbitMQ/Celery) for async tasks
- Deploy containerization (Docker) for easier scaling

---

## Design Decisions

### Why Flask over FastAPI/Django?
- **Simplicity:** Minimal boilerplate for early development
- **Flexibility:** Easy to modify structure during active design
- **Learning curve:** Lower barrier for non-expert developer
- **Future migration:** Can migrate to FastAPI/microservices later if needed

### Why PostgreSQL over MySQL/MongoDB?
- **JSON support:** Native JSONB for flexible data structures
- **Full-text search:** Built-in capabilities for text analysis
- **Robustness:** Strong ACID compliance, mature ecosystem
- **Future features:** PostGIS for geographic analysis, advanced indexing

### Why Monolithic over Microservices?
- **Current scale:** Single developer, moderate data volume
- **Development speed:** Faster iteration without inter-service complexity
- **Later migration:** Can extract services (e.g., news ingestion) when needed
- **Simplicity:** Easier debugging and deployment in early stages

---

## Performance Considerations

### Current Bottlenecks (Anticipated)
1. **CIE Parsing:** Manual hierarchical code breakdown will be slow at scale
2. **Article Deduplication:** URL-based matching doesn't catch near-duplicates
3. **Actor Lookups:** Linear search through dropdowns becomes unwieldy

### Planned Optimizations (v1.2+)
1. **Database Indexing:** Add composite indexes for frequent query patterns
2. **Caching Layer:** Redis for actor/institution lookups
3. **CIE Parser:** Automated parsing to extract actors/actions from CIE text
4. **Search Infrastructure:** Elasticsearch for fuzzy matching and full-text search

---

## Security Considerations

### Current State (v1.0)
- **No authentication:** Single-user local deployment
- **No input sanitization:** Trusted user environment
- **No rate limiting:** Local-only access

### Future Requirements (v1.3+)
- **Authentication:** User accounts with role-based access
- **Input validation:** Sanitize all user inputs (SQL injection, XSS)
- **API rate limiting:** Prevent abuse of external-facing endpoints
- **Data encryption:** Sensitive information at rest and in transit
- **Audit logging:** Track all data modifications with timestamps

---

## Deployment

### Current Deployment (v1.0)
- **Environment:** Local development machine
- **Database:** Local PostgreSQL instance
- **Access:** localhost:5000 only

### Future Deployment (v1.2+)
- **Environment:** Cloud hosting (AWS/GCP/Azure) or dedicated server
- **Database:** Managed PostgreSQL service
- **Access:** HTTPS with domain, authentication required
- **Backup:** Automated daily backups with point-in-time recovery

---

**For questions about technical implementation, see GitHub repository or contact project maintainer.**
