# Global Narratives System v1.0

**Event Creation Test Implementation**

A Flask-based analytical system for tracking and analyzing global events using the Compressed Information Expression (CIE) coding language. This system establishes the foundational workflow for collecting news articles, creating analytically-coded events, and managing actors, institutions, and positions.

---

## Overview

The Global Narratives System treats news articles as substrate - raw material for creating precisely-coded events that capture real-world actions. Events are linked to actors (individuals) and positions (organizational roles) to maintain comprehensive relationship tracking.

### Core Philosophy

- **Articles are substrate** - News articles are imperfect representations; events are the authoritative analytical unit
- **Events are authoritative** - CIE-coded events are the primary data structure
- **Positions perdure, individuals change** - Organizational roles are tracked separately from the people who hold them
- **Precision over interpretation** - CIE maintains strict observational boundaries

---

## Features (v1.0)

### Article Collection
- Automated collection from The News API
- RSS feed integration for multiple sources
- Manual collection trigger via web interface
- Automatic deduplication by URL
- Article review dashboard with filtering

### Event Management
- CIE-coded event creation from articles
- Split-view interface showing source article alongside event form
- Auto-generated event codes with regional and temporal structure
- Support for both position codes and actor codes
- Event search and filtering
- Preserved formatting for multi-line CIE expressions

### Actor/Institution/Position Management
- Hierarchical institution structure
- Position tracking within institutions
- Individual actor records with CIE-compliant IDs
- Tenure system linking actors to positions over time
- Vacancy tracking for positions
- Current holder resolution on specific dates

### User Interface
- C3I-inspired terminal aesthetic (dark theme, cyan/green accents)
- AJAX-powered article processing (no page reloads)
- Responsive design for professional analyst use
- Real-time character counters on forms
- Comprehensive search and filtering

---

## Technology Stack

- **Backend:** Flask (Python 3.9+)
- **Database:** PostgreSQL 18
- **Frontend:** HTML/CSS with Jinja2 templates
- **News Sources:** The News API + RSS feeds
- **Key Libraries:** SQLAlchemy, WTForms, feedparser, requests

---

## Installation

### Prerequisites
- Python 3.9 or higher
- PostgreSQL 12 or higher
- pip and virtualenv

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Narratives_event_test_1.0
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

   Required environment variables:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/global_narratives
   FLASK_SECRET_KEY=<random-secret-key>
   NEWS_API_KEY=<your-news-api-key>
   RSS_FEEDS=<comma-separated-feed-urls>
   ```

5. **Create database**
   ```bash
   createdb global_narratives
   ```

6. **Initialize database and load test data**
   ```bash
   python setup.py
   ```

7. **Run the application**
   ```bash
   python run.py
   ```

8. **Access the application**
   ```
   http://localhost:5000
   ```

---

## Database Schema

### Core Tables
- **articles** - Collected news articles awaiting review
- **events** - CIE-coded events (primary analytical unit)
- **actors** - Individual people with CIE actor IDs
- **institutions** - Organizational entities
- **positions** - Organizational roles within institutions
- **tenures** - Actor-position assignments with time bounds
- **event_actors** - Links events to actors/positions (subjects and objects)

See `schema.sql` for complete database structure.

---

## Usage

### Collecting Articles

**Manual Collection:**
Click "Collect Articles Now" button on the Articles dashboard

**Automatic Collection (via cron):**
```bash
# Add to crontab for daily collection at 00:00 UTC
0 0 * * * /path/to/venv/bin/python /path/to/collectors/collect_articles.py
```

### Creating Events

1. Navigate to Articles dashboard
2. Review unprocessed articles
3. Click "Create Event" on desired article
4. Fill CIE-coded event form:
   - Select region
   - Enter core action code
   - Write CIE description (supports multi-line with indentation)
   - Write natural language summary
   - Assign subject and object actors/positions
5. Preview and save

### Managing Actors/Positions/Institutions

**Create Institutions → Positions → Actors → Tenures** (in that order)

1. **Institutions:** Organizations (e.g., `usa.gov`)
2. **Positions:** Roles within organizations (e.g., `usa.hos`)
3. **Actors:** Individual people with birth year-based IDs (e.g., `usa.1942.0001`)
4. **Tenures:** Assign actors to positions with start/end dates

---

## Project Structure

```
Narratives_event_test_1.0/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # SQLAlchemy database models
│   ├── forms/               # WTForms for all interfaces
│   ├── routes/              # Blueprint routes
│   ├── templates/           # Jinja2 HTML templates
│   ├── static/              # CSS and JavaScript
│   └── utils/               # Helper functions
├── collectors/
│   ├── news_api_collector.py
│   ├── rss_collector.py
│   └── collect_articles.py  # Main collection script
├── config.py                # Configuration management
├── run.py                   # Application entry point
├── setup.py                 # Database initialization
├── schema.sql               # PostgreSQL schema
└── requirements.txt         # Python dependencies
```

---

## CIE Coding Language

The Compressed Information Expression (CIE) language enables precise, information-dense coding of events:

- **Event codes:** `e.ddmmyyyy.region.ordinal` (e.g., `e.09102025.nam.0001`)
- **Actor codes:** `country.year.ordinal` (e.g., `usa.1942.0001`)
- **Position codes:** Hierarchical (e.g., `usa.hos`, `jpn.com.mde.002.exc.01`)
- **Action codes:** Categorize event types (e.g., `[rl]`, `[s-tr]`)

CIE maintains strict boundaries between observation and interpretation.

---

## Out of Scope (v1.0)

The following features are planned but not included in this test implementation:

- Scenarios and narratives
- Event-scenario assignments
- Probability tracking and updates
- Event references as database relationships
- CIE parser and syntax validation
- User authentication and roles
- Advanced analytics and visualization
- API layer for external access
- Field reporting integration

---

## Development Notes

### Known Issues
- `datetime.utcnow()` deprecation warnings (Python 3.12+ compatibility)
- RSS collector may have issues with malformed feeds

### Future Enhancements
- Bulk import/export for actors, institutions, positions
- Enhanced CIE syntax validation
- Scenario and narrative tracking
- Probability update algorithms
- Advanced relationship visualization

---

## Contributing

This is a test implementation. Contribution guidelines will be established for future versions.

---

## License

[To be determined]

---

## Contact

[To be determined]

---

## Acknowledgments

Built with Flask, PostgreSQL, and a terminal aesthetic inspired by C3I systems.