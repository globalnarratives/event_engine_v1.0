# Global Narratives System - Development Roadmap

**Last Updated:** October 31, 2025  
**Current Version:** v1.0 (Event Engine)  
**Active Development:** v1.1 (Seed Data System)

---

## Table of Contents

1. [Version History](#version-history)
2. [Current Development (v1.1)](#current-development-v11)
3. [Upcoming Versions](#upcoming-versions)
4. [Long-Term Vision](#long-term-vision)
5. [Contributing](#contributing)

---

## Version History

### Version 1.0 - Event Engine ✅

**Released:** October 17, 2025  
**Status:** Complete and Deployed

Foundation system for event collection and coding.

**Key Features Delivered:**
- Article collection from News API + RSS feeds
- Manual collection trigger via web UI button
- Article review dashboard with AJAX mark as junk/processed
- Event creation with CIE coding (preserves formatting/indentation)
- Actor/Institution/Position/Tenure management
- Split-view event creation (source article + form)
- Auto-generated event codes (e.ddmmyyyy.region.ordinal)
- C3I-inspired terminal aesthetic (dark theme, cyan/green accents)

**GitHub:**
- Repository: `event_engine_v1.0` (public)
- Tag: `v1.0`
- Commit: "v1.0: Working event engine with article collection, event creation, and AIP management"

---

## Current Development (v1.1)

### Version 1.1 - Seed Data System 🔄

**Target Release:** November 2025  
**Status:** In Progress

Populate the system with comprehensive reference data to enable systematic event coding.

### Goals

1. **Create comprehensive AIP database** with hundreds of actors, institutions, and positions
2. **Build import infrastructure** for bulk data loading from CSV
3. **Validate data integrity** across relationships and hierarchies
4. **Document seeding process** for future updates

### Priority Tasks

#### Task 1: Complete Import Script ⬜

**Status:** In Progress  
**File:** `scripts/import_seed_data.py`

**Requirements:**
- Read CSV files from `seed_data/` directory
- Parse and validate data format
- Create database records for:
  - Actors (with name fields split appropriately)
  - Institutions (with hierarchical codes)
  - Positions (linked to institutions)
  - Tenures (linking actors to positions with dates)
- Handle relationships and foreign keys correctly
- Robust error handling and logging
- Idempotent operation (can run multiple times safely without duplicating)

**Acceptance Criteria:**
- [ ] Script successfully imports all CSV files
- [ ] Database populated with valid AIPs
- [ ] Relationships properly established (position→institution, tenure→actor+position)
- [ ] Error messages are clear and actionable
- [ ] Script includes usage documentation
- [ ] Duplicate detection prevents re-imports

#### Task 2: Populate AIP Database ⬜

**Status:** Not Started  
**Dependencies:** Task 1 completion

**Requirements:**
- Populate CSV templates with real-world data
- Focus on key actors in current global narratives:
  - Israeli government and military leadership
  - Iranian government and IRGC
  - US government officials (State, Defense, White House)
  - European leaders (UK, France, Germany)
  - Middle Eastern leaders (Saudi Arabia, UAE, Egypt, Turkey)
  - Chinese government officials
  - Russian government officials
  - UN officials
  - Major NGO/IO leaders
- Ensure comprehensive coverage for active event coding

**Target Scale:**
- At least 200 actors
- At least 100 institutions
- At least 150 positions
- Current tenures properly linked
- Coverage of all major geographic regions (nam, weu, eeu, mea, sas, nea, sea, ssa, sam, oce)
- Focus on currently active political figures

**Acceptance Criteria:**
- [ ] At least 200 actors entered with complete name fields
- [ ] At least 100 institutions with proper hierarchical codes
- [ ] At least 150 positions linked to institutions
- [ ] Current tenures properly established
- [ ] All ten geographic regions represented
- [ ] Key current conflicts have adequate actor coverage

#### Task 3: Test Data Integrity ⬜

**Status:** Not Started  
**Dependencies:** Tasks 1-2 completion

**Requirements:**
- Verify all relationships are correct
- Check for duplicate entries across tables
- Validate hierarchical institution structures
- Confirm tenure date logic (no end dates before start dates)
- Test event creation with imported AIPs
- Verify dropdown population in event creation interface

**Test Cases:**
- [ ] All position codes reference valid institution codes
- [ ] All tenure entries reference valid actor_id and position_code
- [ ] No orphaned records in any table
- [ ] Hierarchical codes parse correctly (country.category.subcategory...)
- [ ] Date logic is sound across all tenures
- [ ] Events can be successfully created using imported AIPs
- [ ] Event_actors junction table populates correctly

---

## Upcoming Versions

### Version 1.2 - Scenarios System 📋

**Target Release:** December 2025 - January 2026  
**Status:** Planned

Implement forward-looking analytical capabilities with probability tracking.

**Planned Features:**

1. **Scenarios Database Schema**
   - Scenario model with probability tracking
   - Event-scenario relationship table with weights
   - Probability history for temporal tracking

2. **Scenarios Management UI**
   - Scenario creation form
   - Scenario listing/browsing interface
   - Event assignment workflow
   - Probability update mechanism
   - Resolution workflow (resolved-yes, resolved-no, expired)

3. **Probability Tracking System**
   - Algorithm for updating probabilities based on weighted events
   - Temporal probability tracking and history
   - Visualization of probability changes over time
   - Impact assessment for individual events

4. **Full CIE Functional Grammar**
   - Complete action code taxonomy
   - Formal syntax specification
   - Validation rules and constraints
   - Context markers and modifiers documentation

**Success Metrics:**
- Can create and track at least 20 active scenarios
- Probability calculations respond to event assignments
- Clear visualization of probability evolution
- CIE syntax documented comprehensively

### Version 1.3 - Advanced Features 🔮

**Target Release:** Q2 2026  
**Status:** Conceptual

**Planned Features:**

1. **Narratives System**
   - Higher-order structures containing multiple scenarios
   - Narrative-scenario relationships
   - Impact dimensions (political, economic, security, social)
   - Saliency, velocity, volatility measures
   - Temporal tracking of narrative evolution

2. **CIE Parser & Validation**
   - Automated parsing of CIE syntax
   - Real-time validation during event creation
   - Actor/action extraction from CIE text
   - Auto-population of event_actors junction table
   - Syntax highlighting in event creation interface

3. **Event References as Relationships**
   - Parse `$` operators from CIE
   - Create event_references table
   - Build event reference graphs
   - Visualize event networks and chains

4. **User Authentication & Multi-User Support**
   - User accounts with role-based access
   - Permission levels (admin, analyst, viewer)
   - User activity tracking
   - Audit logs for all data modifications

5. **Advanced Analytics Dashboard**
   - Actor network visualization
   - Temporal trend analysis
   - Scenario probability timelines
   - Geographic heat maps
   - Event frequency analysis

6. **API Layer**
   - RESTful API for external access
   - Query interface for events, actors, scenarios
   - Export capabilities (JSON, CSV)
   - Webhook support for real-time updates

### Version 2.0+ - Intelligence Platform 🚀

**Target Release:** 2027+  
**Status:** Vision

**Transformational Features:**

1. **Automated Event Suggestion**
   - AI-assisted event identification from articles
   - Suggested CIE coding for analyst review
   - Actor/action extraction from natural language

2. **Natural Language Query Interface**
   - Ask questions in plain English
   - Automated query translation to database searches
   - Conversational analytics

3. **Network Analysis Tools**
   - Actor relationship mapping
   - Influence networks
   - Coalition formation detection
   - Key player identification

4. **Predictive Modeling**
   - Machine learning for scenario probability updates
   - Pattern recognition in event sequences
   - Early warning systems for emerging narratives

5. **Collaborative Features**
   - Multi-analyst annotation
   - Shared workspaces
   - Comment threads on events/scenarios
   - Export templates for reports

6. **External Integrations**
   - Additional data sources (social media, financial data)
   - GIS integration for spatial analysis
   - Academic research databases
   - Intelligence community tools

---

## Long-Term Vision

### Intelligence Analysis Platform

Transform the Global Narratives System into a comprehensive platform for systematic intelligence analysis:

**Core Capabilities:**
- Real-time monitoring of global political events
- Systematic coding and categorization
- Probabilistic forecasting with transparent methodology
- Network analysis of actor relationships
- Longitudinal tracking of political contestations

**Use Cases:**
- Academic research on international relations
- Policy analysis and strategic planning
- Journalism and investigative reporting
- Intelligence community analysis
- Corporate risk assessment

**Design Principles:**
- **Transparency:** All methodologies documented and reproducible
- **Rigor:** Systematic coding with validation
- **Scalability:** Handle thousands of events, actors, scenarios
- **Usability:** Intuitive interfaces for domain experts
- **Openness:** Open-source core with potential commercial extensions

---

## Contributing

### Current Status

This is currently a **solo research project** by a single developer. The codebase is public to enable transparency and potential future collaboration.

### How to Engage

**For Now:**
- Review documentation and provide feedback via GitHub Issues
- Suggest improvements to CIE syntax or methodology
- Report bugs or data integrity issues

**Future Opportunities (v1.3+):**
- Contribute to AIP database (actors, institutions, positions)
- Develop analytical tools and visualizations
- Extend CIE parser capabilities
- Build integrations with external data sources

### Development Principles

**Code Quality:**
- Follow PEP 8 style guide for Python
- Write clear, self-documenting code
- Comment complex logic, especially CIE parsing
- Test thoroughly before committing

**Documentation:**
- Keep README, ARCHITECTURE, CIE_REFERENCE up to date
- Document breaking changes
- Maintain changelog
- Update roadmap as priorities shift

**Versioning:**
- Use semantic versioning (major.minor.patch)
- Tag releases in git
- Maintain backward compatibility where possible
- Clearly communicate breaking changes

---

## Development Workflow

### Current Workflow (Solo Development)

1. **Feature Planning:** Define scope in this document
2. **Implementation:** Build in local development environment
3. **Testing:** Manual testing of new features
4. **Documentation:** Update relevant docs
5. **Commit:** Descriptive commit messages
6. **Tag:** Version tags for milestones

### Future Workflow (v1.3+, Multi-User)

1. **Issue Creation:** Feature requests or bugs in GitHub Issues
2. **Branch:** Create feature branch from main
3. **Implementation:** Develop with tests
4. **Pull Request:** Submit for review
5. **Review:** Code review and approval
6. **Merge:** Integrate into main branch
7. **Deploy:** Release new version

---

## Technical Debt & Known Issues

### Current Technical Debt

1. **No automated testing:** All testing is manual
2. **No CI/CD pipeline:** Manual deployment process
3. **Limited error handling:** Some edge cases not covered
4. **No backup strategy:** Manual database backups only
5. **Hardcoded configurations:** Should use environment variables consistently

### Planned Improvements

**v1.2:**
- Implement basic unit tests for core functions
- Better error handling in article collection
- Automated backup scheduling

**v1.3:**
- Full test coverage
- CI/CD pipeline with GitHub Actions
- Comprehensive error handling
- Monitoring and alerting

---

## Timeline Summary

| Version | Target Date | Status | Key Milestone |
|---------|-------------|--------|---------------|
| v1.0 | Oct 2025 | ✅ Complete | Event Engine operational |
| v1.1 | Nov 2025 | 🔄 In Progress | AIP database populated |
| v1.2 | Jan 2026 | 📋 Planned | Scenarios with probability tracking |
| v1.3 | Q2 2026 | 🔮 Conceptual | Narratives + CIE parser |
| v2.0+ | 2027+ | 🚀 Vision | Full intelligence platform |

---

**For questions about development priorities or to propose changes, see GitHub Issues or contact project maintainer.**
