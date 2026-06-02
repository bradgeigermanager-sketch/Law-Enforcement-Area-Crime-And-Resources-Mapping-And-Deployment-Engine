-- NEW: Telemetry ledger tracking database node cluster health state
CREATE TABLE db_cluster_health_log (
    node_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    node_name VARCHAR(50) NOT NULL, -- e.g., 'Primary-DB-01', 'Replica-DB-02'
    is_writable BOOLEAN NOT NULL DEFAULT TRUE,
    replication_lag_seconds INT DEFAULT 0,
    connection_status VARCHAR(20) CHECK (connection_status IN ('CONNECTED', 'DEGRADED', 'DISCONNECTED')),
    last_heartbeat_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- NEW: Ledger tracking active decoupled buffer spillover during a crash
CREATE TABLE write_buffer_escalations_log (
    spillover_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    cached_transaction_count INT NOT NULL DEFAULT 0,
    buffer_file_path VARCHAR(255), -- Reference to local SQLite or text cache binary
    escalation_state VARCHAR(30) CHECK (escalation_state IN ('STABLE_SYNC', 'BUFFERING_LOCAL', 'SPOOLING_RECOVERY')),
    triggered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_db_heartbeat ON db_cluster_health_log(connection_status, last_heartbeat_timestamp);
CREATE INDEX idx_buffer_state ON write_buffer_escalations_log(escalation_state, triggered_at);

