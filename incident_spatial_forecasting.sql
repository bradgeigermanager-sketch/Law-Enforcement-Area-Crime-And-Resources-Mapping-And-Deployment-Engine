-- ALTERation to support precise timestamp components and forecast models
ALTER TABLE crime_incidents ADD COLUMN hour_of_day INT GENERATED ALWAYS AS (EXTRACT(HOUR FROM incident_timestamp)) STORED;
ALTER TABLE crime_incidents ADD COLUMN day_of_week INT GENERATED ALWAYS AS (EXTRACT(DOW FROM incident_timestamp)) STORED;

-- NEW: Cache Table for Spatial Forecasting Output Engine
CREATE TABLE spatial_hotspot_forecasts (
    forecast_id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    jurisdiction_id INT REFERENCES jurisdictions(jurisdiction_id),
    grid_latitude NUMERIC(8,6) NOT NULL,
    grid_longitude NUMERIC(9,6) NOT NULL,
    forecast_target_week DATE NOT NULL,
    predicted_incident_density FLOAT NOT NULL,
    confidence_lower_bound FLOAT NOT NULL,
    confidence_upper_bound FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_forecast_spatial ON spatial_hotspot_forecasts(grid_latitude, grid_longitude);
CREATE INDEX idx_forecast_date ON spatial_hotspot_forecasts(forecast_target_week);

