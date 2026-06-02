-- NEW: Directory of authorized organizational roles and their primary device endpoints
CREATE TABLE responder_roles (
    role_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    role_name VARCHAR(50) UNIQUE NOT NULL, -- e.g., 'TACTICAL_UNIT', 'CYBER_FORENSICS', 'INFRA_ENG'
    assigned_precinct_id INT, 
    dispatch_channel VARCHAR(20) CHECK (dispatch_channel IN ('TWILIO_SMS', 'SLACK_ALERT', 'MD_TERMINAL')),
    endpoint_address VARCHAR(255) NOT NULL -- Cell number, webhook URL, or machine identifier
);

-- NEW: Rule engine matrix matching incident types to responder profiles
CREATE TABLE notification_routing_rules (
    rule_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    trigger_category VARCHAR(50) NOT NULL, -- e.g., 'Violent', 'Cyber', 'Statutory/Regulatory'
    min_escalation_tier VARCHAR(20) NOT NULL, -- e.g., 'TIER_2_REGIONAL', 'TIER_3_CRITICAL'
    target_role_id INT REFERENCES responder_roles(role_id),
    auto_escalate_on_sensor_failure BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_routing_rules ON notification_routing_rules(trigger_category, min_escalation_tier) WHERE is_active = TRUE;

