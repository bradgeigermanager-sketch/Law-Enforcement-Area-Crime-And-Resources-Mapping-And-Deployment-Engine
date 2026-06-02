-- NEW: Track multiple distributed operational base facilities
CREATE TABLE precinct_bases (
    base_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(100) UNIQUE NOT NULL,
    fleet_capacity INT NOT NULL,
    geom_location GEOMETRY(Point, 4326) NOT NULL
);

-- EXPANDED: Track alert status and automated escalation tiers
CREATE TABLE automated_escalations_log (
    escalation_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    grid_latitude NUMERIC(8,6) NOT NULL,
    grid_longitude NUMERIC(9,6) NOT NULL,
    active_tier VARCHAR(20) CHECK (active_tier IN ('TIER_1_LOCAL', 'TIER_2_REGIONAL', 'TIER_3_TACTICAL_CRITICAL')),
    trigger_reason VARCHAR(255) NOT NULL,
    escalated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bases_geom ON precinct_bases USING GIST(geom_location);
CREATE INDEX idx_escalations_grid ON automated_escalations_log(grid_latitude, grid_longitude);

