-- Ensure the PostGIS extension is enabled for spatial operations
CREATE EXTENSION IF NOT EXISTS postgis;

-- EXPANDED: Track legal jurisdictions with spatial boundaries
CREATE TABLE jurisdictions (
    jurisdiction_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL,
    population_baseline INT NOT NULL,
    -- Stores the multi-polygon boundary of the legal district (SRID 4326 = WGS 84 GPS)
    geom_boundary GEOMETRY(MultiPolygon, 4326) NOT NULL 
);

-- NEW: Track specific physical locations or facilities (Courthouses, Police Precincts)
CREATE TABLE judicial_facilities (
    facility_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    jurisdiction_id INT REFERENCES jurisdictions(jurisdiction_id),
    name VARCHAR(150) NOT NULL,
    facility_type VARCHAR(50) CHECK (facility_type IN ('Courthouse', 'Precinct', 'Correctional')),
    geom_location GEOMETRY(Point, 4326) NOT NULL
);

-- EXPANDED: Track specific statutory violations (unchanged from baseline)
CREATE TABLE statutory_codes (
    statute_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    code_reference VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    severity_level VARCHAR(20) CHECK (severity_level IN ('Felony', 'Misdemeanor', 'Infraction'))
);

-- NEW: Granular Incident Ledger tracking exact coordinate-based event data
CREATE TABLE crime_incidents (
    incident_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    statute_id INT REFERENCES statutory_codes(statute_id),
    jurisdiction_id INT REFERENCES jurisdictions(jurisdiction_id),
    incident_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    -- Exact point location where the violation occurred
    geom_location GEOMETRY(Point, 4326) NOT NULL 
);

-- Spatial Indexes to optimize localized bounding-box and radius queries
CREATE INDEX idx_jurisdictions_geom ON jurisdictions USING GIST(geom_boundary);
CREATE INDEX idx_facilities_geom ON judicial_facilities USING GIST(geom_location);
CREATE INDEX idx_incidents_geom ON crime_incidents USING GIST(geom_location);
CREATE INDEX idx_incidents_time ON crime_incidents(incident_timestamp);

