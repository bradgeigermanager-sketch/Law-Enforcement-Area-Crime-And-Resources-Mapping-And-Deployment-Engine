-- Track legal jurisdictions (e.g., Federal, State, Municipal)
CREATE TABLE jurisdictions (
    jurisdiction_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL,
    population_baseline INT NOT NULL -- Used for calculating rates per 100k
);

-- Track specific statutory violations
CREATE TABLE statutory_codes (
    statute_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    code_reference VARCHAR(50) UNIQUE NOT NULL, -- e.g., "18 U.S.C. § 2113"
    title VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL, -- e.g., "Property", "Violent", "Cyber", "Statutory"
    severity_level VARCHAR(20) CHECK (severity_level IN ('Felony', 'Misdemeanor', 'Infraction'))
);

-- Core ledger tracking the frequency of filed charges over time
CREATE TABLE charge_metrics (
    metric_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    jurisdiction_id INT REFERENCES jurisdictions(jurisdiction_id),
    statute_id INT REFERENCES statutory_codes(statute_id),
    reporting_period_start DATE NOT NULL,
    reporting_period_end DATE NOT NULL,
    charge_count INT NOT NULL CHECK (charge_count >= 0),
    CONSTRAINT unique_period_charge UNIQUE (jurisdiction_id, statute_id, reporting_period_start)
);

-- Optimizations for fast statistical queries
CREATE INDEX idx_metrics_lookup ON charge_metrics(reporting_period_start, statute_id);
CREATE INDEX idx_statute_category ON statutory_codes(category);

