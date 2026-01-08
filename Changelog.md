# Changelog

All notable changes to the Global Narratives System - Event Engine will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.5.0] - 2026-01-07

### Phase 1.5: Control Frame Integration - COMPLETED

#### Added
- **CIE Syntax Highlighting:** IDE-style color coding for Control Frame display
  - Cyan for operators, symbols, and bullets
  - Pink for entity codes
  - Yellow for action codes and brackets
  - Green for relation operators
- **Scenario Linkage Sidebar:** Right-panel display in Control Frame detail view (dummy data)
- **Control Frame Detail View:** Complete read-only view matching creation form layout
- **JSONB Entity Storage:** Migrated from PostgreSQL ARRAY to JSONB for subjects/objects
- **Parse Tree Caching:** Store complete Lark parse trees as JSONB for future analysis
- **CIE Highlighter Module:** Server-side syntax highlighting engine (`cie_highlighter.py`)
- **Comprehensive Seed Data:** 
  - 117 action codes
  - 266 institutions across 10 countries
  - 250 ministerial positions
  - 243 actors with biographical data
  - 249 tenure assignments
- **CSV Import System:** UTF-8-sig encoding support for BOM handling
- **Event Code Generation:** Automatic format `e.DDMMYYYY.RRR.NNN`

#### Changed
- **Database Schema:** Full reset with improved column constraints
- **Entity Display:** Comma-separated format instead of individual rows
- **Border Styling:** Increased line weight from 1px to 2px for better visual hierarchy
- **Font Sizing:** Increased display value text from 0.95rem to 1.05rem
- **Label Alignment:** Right-aligned CF labels using Courier font for consistency
- **CSS Organization:** Consolidated from 1000+ lines to ~810 lines, removed duplicates

#### Fixed
- **PostgreSQL Array Bug:** Resolved malformed array literal errors via JSONB migration
- **Date Parsing:** Corrected tenure date format from YYYY-MM-DD to DD-MM-YY
- **BOM Encoding:** Added utf-8-sig support for Excel-generated CSV files
- **Grid Height Alignment:** CIE display and scenario sidebar now match heights
- **Foreign Key Constraints:** Resolved NOT NULL violations in tenure imports

#### Technical Decisions
- **JSONB over ARRAY:** Better Python integration, more flexible queries
- **Server-Side Highlighting:** Leverage existing Lark parser for accuracy
- **Layout Mirroring:** Detail view matches creation form for analytical continuity
- **Explicit Enumeration:** Define valid CIE patterns rather than compositional rules

---

## [1.0.0] - 2025-12-XX

### Phase 1.0: Event Engine Foundation - COMPLETED

#### Added
- **Flask Application:** Core web framework setup
- **PostgreSQL Database:** SQLAlchemy ORM with initial schema
- **Article Collection:** RSS feed integration and news API connectors
- **Event Creation:** Basic form-based event input
- **Actor Management:** Entity browsing and basic CRUD
- **Control Frame Model:** Initial database structure for CIE events
- **Reference Data:** Action codes, institutions, positions taxonomy

#### Infrastructure
- **Project Structure:** Modular Flask blueprint architecture
- **Static Assets:** C3I terminal aesthetic CSS foundation
- **Template System:** Jinja2 base templates and inheritance
- **Configuration:** Environment-based config management

---

## [Unreleased]

### Planned for Phase 1.6
- Event editing functionality
- Advanced event search with CIE pattern matching
- Event relationship visualization
- Expanded EU country reference data
- Bulk event import tools

### Planned for Phase 2.0
- Scenarios database schema
- Scenario creation interface
- Scenario-event linkage logic
- Probability tracking algorithms
- Scenario resolution workflows

---

## Development Notes

### Version Numbering
- **Major version (1.x.x):** Complete phase milestones
- **Minor version (x.5.x):** Significant feature additions within phase
- **Patch version (x.x.1):** Bug fixes and minor improvements

### Key Milestones
- **v1.0:** Event Engine core functionality
- **v1.5:** Control Frame integration complete
- **v2.0:** Scenarios system (planned)
- **v3.0:** Narratives layer (planned)

---

*Changelog maintained by Peter Marino*  
*Last Updated: January 7, 2026*