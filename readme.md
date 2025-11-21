# Global Narratives System v1.1

**Event Engine with Seed Data System**

A Flask-based analytical system for tracking and analyzing global events using the Compressed Information Expression (CIE) coding language. Version 1.1 adds comprehensive seed data for 218 ministerial positions across 10 major countries, establishing a production-ready foundation for tracking global political actors.

---

## Overview

The Global Narratives System treats news articles as substrate - raw material for creating precisely-coded events that capture real-world actions. Events are linked to actors (individuals) and positions (organizational roles) to maintain comprehensive relationship tracking.

### Core Philosophy

- **Articles are substrate** - News articles are imperfect representations; events are the authoritative analytical unit
- **Events are authoritative** - CIE-coded events are the primary data structure
- **Positions perdure, individuals change** - Organizational roles are tracked separately from the people who hold them
- **Precision over interpretation** - CIE maintains strict observational boundaries
- **Codes are hierarchical and self-describing** - CIE codes embed structural information

---

## What's New in v1.1

### Seed Data System
- **218 ministerial positions** across 10 countries (USA, France, UK, Canada, Australia, Japan, Germany, Russia, Spain, Turkey)
- **215+ current office holders** with biographical data
- **Comprehensive institution mapping** covering foreign affairs, defense, finance, justice, and 11 other functional areas
- **CSV-based data management** for easy updates and version control
- **Automated import system** with validation and error handling

### Data Structure
- **Countries:** 10 major democracies and regional powers
- **Institutions:** Ministerial departments with hierarchical organization
- **Positions:** Cabinet-level and sub-cabinet positions with CIE codes
- **Actors:** Current office holders with birth years and biographical info
- **Tenures:** Start dates for all current positions (reshuffle-ready)

### Import Tools
- `import_seed_data.py` - Automated CSV import with validation
- `rebuild_db.py` - Database schema rebuild utility
- UTF-8 encoding support for international names
- Foreign key validation and relationship verification
- Detailed error reporting with row-level diagnostics

---

## Features

### v1.1 (Current)
- ✅ Complete seed data for 10 countries
- ✅ CSV-based data management
- ✅ Automated import system
- ✅ Actor-Institution-Position (AIP) database
- ✅ Current office holder tracking
- ✅ Tenure management with start dates

### v1.0 (Foundation)
- ✅ Article collection (News API + RSS)
- ✅ CIE-coded event creation
- ✅ Actor/Institution/Position management
- ✅ Split-view event creation interface
- ✅ C3I terminal aesthetic
- ✅ Search and filtering

---

## Technology Stack

- **Backend:** Flask (Python 3.9+)
- **Database:** PostgreSQL 12+
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
   git clone https://github.com/globalnarratives/event_engine_v1.0.git
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

6. **Initialize database schema**
   ```bash
   python rebuild_db.py
   ```

7. **Import seed data**
   ```bash
   python import_seed_data.py --clear
   ```
   
   This imports:
   - 218 ministerial positions
   - 215+ current office holders
   - Institutional structures for 10 countries
   - Current tenure data with start dates

8. **Run the application**
   ```bash
   python run.py
   ```

9. **Access the application**
   ```
   http://localhost:5000
   ```

---

## Seed Data Management

### CSV Files (in `seed_data/` directory)

1. **institution_codes.csv**
   - Ministerial departments and government institutions
   - Columns: country_code, institution_name, institution_code, institution_layer, institution_type, institution_subtype_01

2. **position_codes.csv**
   - Cabinet and sub-cabinet positions
   - Columns: country_code, institution_name, institution_code, position_code, position_title, hierarchy_level, description

3. **actor_codes.csv**
   - Current office holders (unique individuals only)
   - Columns: actor_id, surname, given_name, middle_name, birth_year, position_code, position_title

4. **tenure_codes.csv**
   - Links actors to positions with start dates
   - Columns: actor_id, position_code, tenure_start, tenure_end, notes

### Updating Seed Data

To update positions, actors, or tenures:

1. Edit the relevant CSV file(s) in the `seed_data/` directory
2. Save changes (Excel or text editor with UTF-8 encoding)
3. Run the import script:
   ```bash
   python import_seed_data.py --clear
   ```

The `--clear` flag wipes the existing data and performs a fresh import from CSVs.

### Date Format

All dates use **DD-MM-YY** format (e.g., `21-01-25` for January 21, 2025).

### Handling Cabinet Reshuffles

When ministers change:
1. Update `actor_codes.csv` (add new actors if needed)
2. Update `tenure_codes.csv` (set end_date for outgoing, add new row for incoming)
3. Run import script to refresh database

---

## Database Schema

### Core Tables

**v1.1 Additions:**
- **institutions** - Organizational entities with hierarchical structure
  - Fields: institution_code (PK), institution_name, institution_type, institution_layer, institution_subtype_01, country_code, description
  
- **positions** - Organizational roles within institutions
  - Fields: position_code (PK), country_code, institution_code (FK), institution_name, position_title, hierarchy_level, description
  
- **actors** - Individual people with CIE actor IDs
  - Fields: actor_id (PK), surname, given_name, middle_name, birth_year, position_code (current), position_title (current), biographical_info
  
- **tenures** - Actor-position assignments with time bounds
  - Fields: tenure_id (PK), actor_id (FK), position_code (FK), tenure_start, tenure_end, notes

**v1.0 Foundation:**
- **articles** - Collected news articles awaiting review
- **events** - CIE-coded events (primary analytical unit)
- **event_actors** - Links events to actors/positions (subjects and objects)

See `schema.sql` for complete database structure.

---

## Usage

### Viewing Seed Data

Navigate to the **Actors**, **Positions**, or **Institutions** sections to browse the imported data:
- View current office holders by country
- Search for specific ministers or positions
- Track position histories and tenures
- Identify vacant positions

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
   - Assign subject and object actors/positions (now pre-populated with 215+ real actors)
5. Preview and save

### Managing Actors/Positions/Institutions

**Option 1: Edit CSVs and Reimport** (Recommended for bulk changes)
1. Edit files in `seed_data/` directory
2. Run `python import_seed_data.py --clear`

**Option 2: Use Web Interface** (For individual records)
1. Navigate to Actors/Positions/Institutions sections
2. Click "Add New" or "Edit" buttons
3. Fill forms and save

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
├── seed_data/               # ✨ NEW in v1.1
│   ├── actor_codes.csv
│   ├── position_codes.csv
│   ├── institution_codes.csv
│   └── tenure_codes.csv
├── config.py                # Configuration management
├── run.py                   # Application entry point
├── setup.py                 # Database initialization
├── import_seed_data.py      # ✨ NEW in v1.1 - CSV import tool
├── rebuild_db.py            # ✨ NEW in v1.1 - Schema rebuild
├── schema.sql               # PostgreSQL schema
└── requirements.txt         # Python dependencies
```

---

## CIE Coding Language

The Compressed Information Expression (CIE) language enables precise, information-dense coding of events:

### Code Structure

**Event codes:** `e.ddmmyyyy.region.ordinal`
- Example: `e.09102025.nam.0001` (first North American event on Oct 9, 2025)

**Actor codes:** `country.birth_year.ordinal`
- Example: `usa.1942.001` (first US actor born in 1942 in the dataset)

**Position codes:** `country.type.function.subfunction.ordinal`
- Example: `usa.min.forn.exc.01` (USA, Minister, Foreign Affairs, Executive, #1)
- Example: `fra.hos.fisc.exc.01` (France, Head of State, Fiscal, Executive, #1)

**Institution codes:** `type.function`
- Example: `min.forn` (Ministry of Foreign Affairs)
- Example: `min.dfns` (Ministry of Defense)
- Prepended with country code in database: `usa.min.forn`

### Code Type Abbreviations

**Position Types:**
- `min` = Minister (Cabinet-level)
- `hos` = Head of State (President, Monarch)
- `hog` = Head of Government (Prime Minister, Chancellor)
- `amb` = Ambassador

**Functional Areas:**
- `forn` = Foreign Affairs
- `fisc` = Fiscal/Finance/Treasury
- `dfns` = Defense
- `jstc` = Justice
- `gndm` = Gendarmerie/Interior/Home Affairs
- `hlth` = Health
- `educ` = Education
- `labr` = Labor
- `agrc` = Agriculture
- `resr` = Resources/Environment
- `infr` = Infrastructure/Transport
- `comc` = Commerce/Trade
- `cltr` = Culture
- `scnc` = Science/Higher Education
- `spec` = Special Functions (varies by country)

**Action Codes:**
- `[rl]` = Release/Announcement
- `[s-tr]` = State Transfer
- (More to be systematized in future versions)

CIE maintains strict boundaries between observation and interpretation.

---

## Covered Countries (v1.1)

### North America
- 🇺🇸 **United States** (USA) - 22 positions
- 🇨🇦 **Canada** (CAN) - 30 positions

### Europe
- 🇫🇷 **France** (FRA) - 41 positions
- 🇬🇧 **United Kingdom** (GBR) - 25 positions
- 🇩🇪 **Germany** (DEU) - 16 positions
- 🇪🇸 **Spain** (ESP) - 22 positions
- 🇷🇺 **Russia** (RUS) - 22 positions

### Asia-Pacific
- 🇯🇵 **Japan** (JPN) - 20 positions
- 🇦🇺 **Australia** (AUS) - 31 positions

### Eurasia
- 🇹🇷 **Turkey** (TUR) - 17 positions

**Total: 218 positions, 215+ unique actors**

---

## Out of Scope (Current Version)

The following features are planned but not yet implemented:

### Coming in v1.2 (Scenarios System)
- Scenarios and narratives
- Event-scenario assignments
- Probability tracking and updates
- Narrative threading

### Future Enhancements
- Event references as database relationships
- CIE parser and syntax validation
- User authentication and roles
- Advanced analytics and visualization
- API layer for external access
- Field reporting integration
- Bulk actor/position/institution management via web interface
- Automated reshuffle detection
- Government tracking and systematization

---

## Development Notes

### Known Issues
- `datetime.utcnow()` deprecation warnings (Python 3.12+ compatibility)
- RSS collector may have issues with malformed feeds
- Manual tenure end-date updates required (not yet automated)

### Design Decisions (v1.1)
- **Position codes over institution codes** for positions table primary key (CIE hierarchy principle)
- **Country code prepending** handled by import script (keeps CSVs clean)
- **Actors deduplicated** - one row per person, multiple tenures for multiple offices
- **CSV-based workflow** chosen over web forms for bulk data management
- **UTF-8-sig encoding** to handle Windows Excel BOM characters

---

## Contributing

This is a test implementation. Contribution guidelines will be established for future versions.

---

## License

Apache 2.0

---

## Contact

[To be determined]

---

## Acknowledgments

Built with Flask, PostgreSQL, and a terminal aesthetic inspired by C3I systems.

Special thanks to Wikipedia's cabinet pages and ministry documentation for providing structured data on government positions worldwide.