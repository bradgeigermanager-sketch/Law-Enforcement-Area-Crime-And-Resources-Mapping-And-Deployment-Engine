-- NEW: Tracking ledger for alert thresholds triggered by the engine
CREATE TABLE automated_alerts_log (
    alert_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    grid_latitude NUMERIC(8,6) NOT NULL,
    grid_longitude NUMERIC(9,6) NOT NULL,
    trigger_velocity FLOAT NOT NULL,
    alert_severity VARCHAR(20) CHECK (alert_severity IN ('INFO', 'WARNING', 'CRITICAL')),
    dispatched_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    webhook_status_code INT
);

-- NEW: Ledger tracking optimal resource distributions
CREATE TABLE resource_allocations (
    allocation_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    target_week DATE NOT NULL,
    grid_latitude NUMERIC(8,6) NOT NULL,
    grid_longitude NUMERIC(9,6) NOT NULL,
    allocated_units INT NOT NULL CHECK (allocated_units >= 0),
    expected_risk_coverage FLOAT NOT NULL,
    optimized_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_alerts_time ON automated_alerts_log(dispatched_at);
CREATE INDEX idx_allocations_week ON resource_allocations(target_week);

