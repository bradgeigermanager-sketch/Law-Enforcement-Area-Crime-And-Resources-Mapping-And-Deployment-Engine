-- NEW: Logging matrix tracking sensor heartbeat disruptions
CREATE TABLE sensor_heartbeat_failures (
    failure_log_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    sensor_id INT REFERENCES observation_sensors(sensor_id),
    disruption_type VARCHAR(50) CHECK (disruption_type IN ('Packet_Loss', 'Power_Failure', 'Optics_Occlusion')),
    logged_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- NEW: Tactical route impedance parameters
CREATE TABLE precinct_transit_impedance (
    route_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    origin_facility_id INT REFERENCES judicial_facilities(facility_id),
    target_grid_latitude NUMERIC(8,6) NOT NULL,
    target_grid_longitude NUMERIC(9,6) NOT NULL,
    base_distance_meters FLOAT NOT NULL,
    estimated_transit_minutes FLOAT NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_heartbeat_time ON sensor_heartbeat_failures(logged_at);
CREATE INDEX idx_transit_lookup ON precinct_transit_impedance(origin_facility_id, target_grid_latitude, target_grid_longitude);

