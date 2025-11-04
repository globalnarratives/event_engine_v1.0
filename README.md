# Global Narratives System

**A comprehensive framework for tracking, analyzing, and forecasting global political dynamics through systematic event coding and narrative analysis.**

**Current Version:** v1.0 (Event Engine) - Complete  
**Next Version:** v1.1 (Seed Data System) - In Progress  
**Last Updated:** October 31, 2025

---

## Why Global Narratives?

Traditional news analysis faces a fundamental problem:

- **Too granular:** Individual articles exist in isolation, making patterns invisible
- **Too broad:** High-level narratives lack systematic evidence and reproducibility

**Global Narratives bridges this gap** by providing structured methods for capturing "who is seeking to get what, when, and how" in political, social, and economic contestation.

### What Makes This Different

**Systematic Event Coding:**  
Every international political event is captured in a standardized, machine-readable format (CIE - Compressed Information Expression) that preserves nuance while enabling quantitative analysis.

**Actor-Institution Tracking:**  
Maintains comprehensive relationships between political actors, institutions, and positions over time - not just "who did what" but "who holds what power, and how does that change?"

**Probabilistic Forecasting:**  
Builds testable scenarios with probability tracking, allowing analysts to systematically evaluate how events influence future outcomes.

**Longitudinal Analysis:**  
Tracks political contestations over time with multi-dimensional impact assessment (saliency, potency, velocity, volatility).

### Questions This System Can Answer

- "How has Iranian military activity evolved since October 2023?"
- "Which actors are most central to the Israel-Hezbollah conflict network?"
- "What's the probability of direct Israel-Iran military confrontation by year-end?"
- "How do Chinese diplomatic actions correlate with US policy shifts?"
- "Which narratives are gaining momentum, and which are fading?"

---

## Project Status

### ✅ Version 1.0 - Event Engine (Complete)

**Deployed:** October 17, 2025

Core functionality for systematic event collection and coding:

- **Article Collection:** Automated ingestion from News API + RSS feeds
- **Event Creation:** Split-view interface for coding events in CIE format
- **AIP Management:** Track actors, institutions, positions, and tenures
- **Terminal Aesthetic:** C3I-inspired dark theme with cyan/green accents

### 🔄 Version 1.1 - Seed Data System (In Progress)

**Target:** November 2025

Populating the system with comprehensive reference data:

- CSV seed data templates ✅
- Import script for bulk AIP loading (in progress)
- Hundreds of real-world actors, institutions, and positions
- Coverage of major global regions and current conflicts

### 📋 Version 1.2 - Scenarios System (Planned)

**Target:** December 2025 - January 2026

Forward-looking analytical capabilities:

- Scenario creation with probability tracking
- Event-scenario assignment mechanisms
- Temporal probability updates
- Full functional grammar for CIE

---

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 18
- News API key ([get one here](https://newsapi.org))

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/event_engine_v1.0.git
cd event_engine_v1.0

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials and API keys

# Initialize database
python init_db.py

# Run the application
flask run
```

Visit `http://localhost:5000` in your browser.

---

## Key Concepts

### CIE (Compressed Information Expression)

The core structured language for encoding political events. Captures essential elements in machine-readable format while preserving analytical nuance.

**Example:**
```
e.17102025.eeu.001
rus.min.for.exc.01 [s-tr] tur.hos 
- $ tur.hos {s-st} $ rus.com.hyc.002
```

**Translation:**  
Russian Foreign Minister threatens Turkish Head of State, in response to Turkish Head of State's statement regarding Gazprom.

For detailed CIE documentation, see [CIE_REFERENCE.md](CIE_REFERENCE.md).

### AIP System (Actor-Institution-Position)

Structured tracking of political actors, their institutional affiliations, and positions held over time.

**Example:**
- **Actor:** Benjamin Netanyahu
- **Code:** `isr.1949.0001`
- **Institution:** Government of Israel (`isr`)
- **Position:** Head of Government (`isr.hog`)
- **Tenure:** 2022-12-29 to present

### Scenarios (Coming in v1.2)

Binary, falsifiable predictions about future conditions with specific dates and probability tracking.

**Example:**
```
Scenario: Israel will deploy at least 50 ground troops to Southern Lebanon 
          by January 31, 2026
Initial Probability: 35%
Current Probability: 62%
Status: Active
Event Count: 47
```

---

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical architecture, database schema, system design
- **[CIE_REFERENCE.md](CIE_REFERENCE.md)** - Complete CIE format guide with examples
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Roadmap, tasks, and version planning

---

## Technology Stack

- **Backend:** Flask (Python 3.9+)
- **Database:** PostgreSQL 18
- **ORM:** SQLAlchemy
- **Forms:** WTForms
- **Templates:** Jinja2
- **Data Sources:** News API, RSS feeds (feedparser)

---

## Contributing

This is currently a solo research project. Suggestions and feedback are welcome via GitHub Issues.

### Code Conventions

- Python: PEP 8 style guide
- Database: Snake_case for table/column names
- CIE: Follow documented syntax in CIE_REFERENCE.md

---

## Foundational Research

Based on:  
**"Global Narratives: A Framework for Analyzing International Political Dynamics"** (2015)

Key concepts:
- Lasswell's "who gets what, when, and how" framework adapted to "who is seeking to get what"
- Quantitative measurement of political contestations
- Longitudinal tracking with saliency, potency, velocity, and volatility measures
- Second-order effects mapping

---

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

## Contact

For questions or issues, please use [GitHub Issues](https://github.com/yourusername/event_engine_v1.0/issues).

---

**GitHub Repository:** [event_engine_v1.0](https://github.com/yourusername/event_engine_v1.0)  
**Version:** v1.1-dev  
**Status:** Active Development
