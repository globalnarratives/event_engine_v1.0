-- Global Narratives System v1.0 Database Schema
-- PostgreSQL

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS event_actors CASCADE;
DROP TABLE IF EXISTS tenures CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS articles CASCADE;
DROP TABLE IF EXISTS positions CASCADE;
DROP TABLE IF EXISTS actors CASCADE;
DROP TABLE IF EXISTS institutions CASCADE;

-- =============================================================================
-- ARTICLES TABLE
-- Stores collected news articles awaiting analyst review
-- =============================================================================

CREATE TABLE articles (
    article_id SERIAL PRIMARY KEY,
    url VARCHAR(500) NOT NULL UNIQUE,
    headline VARCHAR(250) NOT NULL,
    summary TEXT NOT NULL,
    source_name VARCHAR(200) NOT NULL,
    published_date DATE NOT NULL,
    collected_date TIMESTAMP NOT NULL DEFAULT NOW(),
    is_processed BOOLEAN NOT NULL DEFAULT FALSE,
    is_junk BOOLEAN NOT NULL DEFAULT FALSE
);

-- Indexes for articles
CREATE INDEX idx_articles_processed ON articles(is_processed);
CREATE INDEX idx_articles_published ON articles(published_date);
CREATE INDEX idx_articles_junk ON articles(is_junk);

-- =============================================================================
-- INSTITUTIONS TABLE
-- Organizational entities that contain positions
-- =============================================================================

CREATE TABLE institutions (
    institution_code VARCHAR(100) PRIMARY KEY,
    institution_name VARCHAR(300) NOT NULL,
    institution_type VARCHAR(50),
    country_code VARCHAR(3),
    description TEXT
);

-- Indexes for institutions
CREATE INDEX idx_institutions_country ON institutions(country_code);
CREATE INDEX idx_institutions_type ON institutions(institution_type);

-- =============================================================================
-- POSITIONS TABLE
-- Organizational roles within institutions
-- =============================================================================

CREATE TABLE positions (
    position_code VARCHAR(100) PRIMARY KEY,
    position_title VARCHAR(300) NOT NULL,
    institution_code VARCHAR(100) NOT NULL,
    hierarchy_level VARCHAR(50),
    description TEXT,
    FOREIGN KEY (institution_code) REFERENCES institutions(institution_code)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Indexes for positions
CREATE INDEX idx_positions_institution ON positions(institution_code);
CREATE INDEX idx_positions_level ON positions(hierarchy_level);

-- =============================================================================
-- ACTORS TABLE
-- Individual people
-- =============================================================================

CREATE TABLE actors (
    actor_id VARCHAR(20) PRIMARY KEY,
    surname VARCHAR(150) NOT NULL,
    given_name VARCHAR(150) NOT NULL,
    middle_name VARCHAR(150),
    biographical_info TEXT
);

-- Indexes for actors
CREATE INDEX idx_actors_surname ON actors(surname);
CREATE INDEX idx_actors_country_year ON actors(LEFT(actor_id, 8));

-- =============================================================================
-- EVENTS TABLE
-- Primary analytical data - CIE-coded events
-- =============================================================================

CREATE TABLE events (
    event_code VARCHAR(50) PRIMARY KEY,
    event_date DATE NOT NULL,
    region VARCHAR(3) NOT NULL,
    ordinal INTEGER NOT NULL,
    recorded_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    core_action VARCHAR(10) NOT NULL,
    cie_description VARCHAR(250) NOT NULL,
    natural_summary VARCHAR(250) NOT NULL,
    article_url VARCHAR(500) NOT NULL,
    article_headline VARCHAR(250),
    created_by VARCHAR(100),
    CONSTRAINT chk_region CHECK (region IN ('weu', 'eeu', 'nam', 'sam', 'nea', 'sea', 'sas', 'mea', 'ssa')),
    CONSTRAINT unique_event_ordinal UNIQUE (event_date, region, ordinal)
);

-- Indexes for events
CREATE INDEX idx_events_date ON events(event_date);
CREATE INDEX idx_events_region ON events(region);
CREATE INDEX idx_events_action ON events(core_action);

-- =============================================================================
-- TENURES TABLE
-- Junction table linking actors to positions with time bounds
-- =============================================================================

CREATE TABLE tenures (
    tenure_id SERIAL PRIMARY KEY,
    actor_id VARCHAR(20) NOT NULL,
    position_code VARCHAR(100) NOT NULL,
    tenure_start DATE NOT NULL,
    tenure_end DATE,
    FOREIGN KEY (actor_id) REFERENCES actors(actor_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (position_code) REFERENCES positions(position_code)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT chk_tenure_dates CHECK (tenure_end IS NULL OR tenure_end >= tenure_start),
    CONSTRAINT unique_tenure UNIQUE (actor_id, position_code, tenure_start)
);

-- Indexes for tenures
CREATE INDEX idx_tenures_actor ON tenures(actor_id);
CREATE INDEX idx_tenures_position ON tenures(position_code);
CREATE INDEX idx_tenures_dates ON tenures(position_code, tenure_start, tenure_end);

-- =============================================================================
-- EVENT_ACTORS TABLE
-- Junction table linking events to actors or positions (both subjects and objects)
-- =============================================================================

CREATE TABLE event_actors (
    event_actor_id SERIAL PRIMARY KEY,
    event_code VARCHAR(50) NOT NULL,
    code VARCHAR(100) NOT NULL,
    code_type VARCHAR(20) NOT NULL,
    role_type VARCHAR(20) NOT NULL,
    FOREIGN KEY (event_code) REFERENCES events(event_code)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT chk_code_type CHECK (code_type IN ('position', 'actor')),
    CONSTRAINT chk_role_type CHECK (role_type IN ('subject', 'object'))
);

-- Indexes for event_actors
CREATE INDEX idx_event_actors_event ON event_actors(event_code);
CREATE INDEX idx_event_actors_code ON event_actors(code);
CREATE INDEX idx_event_actors_role ON event_actors(role_type);
CREATE INDEX idx_event_actors_type ON event_actors(code_type);

-- =============================================================================
-- COMMENTS AND DOCUMENTATION
-- =============================================================================

COMMENT ON TABLE articles IS 'News articles collected from external sources awaiting analyst review';
COMMENT ON TABLE institutions IS 'Organizational entities that contain positions';
COMMENT ON TABLE positions IS 'Organizational roles within institutions that persist over time';
COMMENT ON TABLE actors IS 'Individual people identified by CIE actor codes';
COMMENT ON TABLE events IS 'CIE-coded events - the primary analytical unit';
COMMENT ON TABLE tenures IS 'Links actors to positions with time bounds - positions can be vacant';
COMMENT ON TABLE event_actors IS 'Links events to actors/positions as subjects or objects';

COMMENT ON COLUMN articles.url IS 'Also serves as deduplication key';
COMMENT ON COLUMN events.event_code IS 'Format: e.ddmmyyyy.region.ordinal';
COMMENT ON COLUMN events.event_date IS 'Extracted from event_code for efficient querying';
COMMENT ON COLUMN events.region IS 'Extracted from event_code for efficient querying';
COMMENT ON COLUMN events.ordinal IS 'Daily sequence number within region, extracted from event_code';
COMMENT ON COLUMN actors.actor_id IS 'Format: country.year.ordinal (e.g., usa.1942.0217)';
COMMENT ON COLUMN event_actors.code IS 'Either position_code or actor_id depending on code_type';
COMMENT ON COLUMN event_actors.code_type IS 'Indicates if code references a position or actor directly';
COMMENT ON COLUMN event_actors.role_type IS 'Subject (initiator) or object (recipient) of action';