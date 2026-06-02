-- NEW: Directory tracking primary and alternative notification channels
CREATE TABLE communications_failover_paths (
    failover_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    primary_channel_type VARCHAR(30) CHECK (primary_channel_type IN ('SLACK_WEBHOOK', 'TWILIO_SMS', 'CENTRAL_SERVER')),
    backup_channel_type VARCHAR(30) CHECK (backup_channel_type IN ('TWILIO_SMS', 'LOCAL_SQLITE_CACHE', 'PEER_MESH_RADIO')),
    failover_trigger_timeout_secs INT DEFAULT 15,
    is_active BOOLEAN DEFAULT TRUE
);

-- NEW: Ledger defining personnel fallback chains when primary units are overloaded
CREATE TABLE activity_fallback_rules (
    fallback_rule_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    primary_role_code VARCHAR(30) NOT NULL,    -- e.g., 'TACTICAL'
    secondary_role_code VARCHAR(30) NOT NULL,  -- e.g., 'MUNICIPAL' (Fallback 1)
    tertiary_role_code VARCHAR(30) NOT NULL,   -- e.g., 'LOCAL_PATROL' (Fallback 2)
    min_qualification_required VARCHAR(100)
);

CREATE INDEX idx_comms_failover ON communications_failover_paths(primary_channel_type) WHERE is_active = TRUE;

