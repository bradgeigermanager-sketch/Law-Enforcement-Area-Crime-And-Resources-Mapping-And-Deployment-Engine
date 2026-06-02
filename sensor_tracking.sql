-- NEW: Sensor Apparatus Tracking Matrix
CREATE TABLE observation_sensors (
    sensor_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    jurisdiction_id INT REFERENCES jurisdictions(jurisdiction_id),
    hardware_uid VARCHAR(100) UNIQUE NOT NULL, -- e.g., "ALPR-NYC-0942"
    sensor_type VARCHAR(30) CHECK (sensor_type IN ('CCTV_Camera', 'ALPR_Scanner', 'Acoustic_IoT', 'Mobile_Data_Terminal')),
    operational_status VARCHAR(20) CHECK (operational_status IN ('Active', 'Maintenance', 'Offline')),
    geom_location GEOMETRY(Point, 4326) NOT NULL, -- Exact placement coordinates
    coverage_radius_meters FLOAT NOT NULL DEFAULT 150.0, -- Field of view distance
    -- Computed PostGIS geometry polygon representing the true sensor visibility footprint
    geom_footprint GEOMETRY(Polygon, 4326) GENERATED ALWAYS AS (ST_Buffer(geom_location::geography, coverage_radius_meters)::geometry) STORED
);

-- EXPANDED: Track which sensor automatically captured the violation
ALTER TABLE crime_incidents ADD COLUMN capturing_sensor_id INT REFERENCES observation_sensors(sensor_id);

CREATE INDEX idx_sensors_geom ON observation_sensors USING GIST(geom_location);
CREATE INDEX idx_sensors_footprint ON observation_sensors USING GIST(geom_footprint);

