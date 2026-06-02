-- NEW: Tracks granular personnel certifications and dynamic hardware capabilities
CREATE TABLE vehicle_unit_manifests (
    unit_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    unit_callsign VARCHAR(30) UNIQUE NOT NULL, -- e.g., 'X-RAY-01', 'CYBER-MOBILE-2'
    assigned_role_code VARCHAR(20) NOT NULL, -- e.g., 'TACTICAL', 'MUNICIPAL'
    -- Array tracking verified training and personnel certifications
    active_certifications TEXT[] NOT NULL, -- e.g., '{"TACTICAL_ENTRY", "HEAVY_BALLISTICS", "LETHAL_FORCE_AUTH"}'
    -- Array tracking actual vehicle and technical hardware attachments
    hardware_capabilities TEXT[] NOT NULL, -- e.g., '{"ALL_WEATHER_SUSPENSION", "MOBILE_SQLITE_LOG", "ANALOG_RADIO_MESH"}'
    current_availability_status VARCHAR(20) CHECK (current_availability_status IN ('Available', 'Deployed', 'Overloaded'))
);

-- NEW: Network diagnostics logger driving the auto-recovery loop
CREATE TABLE network_link_telemetry (
    link_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    endpoint_name VARCHAR(100) UNIQUE NOT NULL,
    current_latency_ms INT NOT NULL,
    packet_loss_percentage NUMERIC(5,2) NOT NULL,
    last_ping_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_unit_certs ON vehicle_unit_manifests USING GIN(active_certifications);
CREATE INDEX idx_unit_hardware ON vehicle_unit_manifests USING GIN(hardware_capabilities);

