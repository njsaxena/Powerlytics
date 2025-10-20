
-- Powerlytics BigQuery Data Warehouse Schema
-- Creates tables for raw data, analytics, and ML features

-- Create dataset
CREATE SCHEMA IF NOT EXISTS `{project_id}.powerlytics_dwh`
OPTIONS (
  description = "Powerlytics Energy Analytics Data Warehouse",
  location = "US"
);

-- Raw readings table (partitioned by date, clustered by device_id)
CREATE OR REPLACE TABLE `{project_id}.powerlytics_dwh.raw_readings` (
  device_id STRING NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  power_w FLOAT64,
  energy_wh FLOAT64,
  voltage FLOAT64,
  occupancy BOOL,
  temp_c FLOAT64,
  source STRING,
  ingest_ts TIMESTAMP
)
PARTITION BY DATE(timestamp)
CLUSTER BY device_id
OPTIONS (
  description = "Raw energy readings from IoT devices",
  partition_expiration_days = 365
);

-- Anomalies table
CREATE OR REPLACE TABLE `{project_id}.powerlytics_dwh.anomalies` (
  device_id STRING NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  type STRING NOT NULL,
  severity STRING NOT NULL,
  original_power FLOAT64,
  anomaly_power FLOAT64,
  confidence FLOAT64,
  detected_at TIMESTAMP
)
PARTITION BY DATE(timestamp)
CLUSTER BY device_id, type
OPTIONS (
  description = "Detected energy consumption anomalies"
);

-- Hourly aggregated data for analytics
CREATE OR REPLACE TABLE `{project_id}.powerlytics_dwh.analytics_hourly` (
  device_id STRING NOT NULL,
  hour_ts TIMESTAMP NOT NULL,
  avg_power_w FLOAT64,
  max_power_w FLOAT64,
  min_power_w FLOAT64,
  total_energy_wh FLOAT64,
  high_power_events INT64,
  avg_voltage FLOAT64,
  avg_temp_c FLOAT64,
  occupancy_percentage FLOAT64,
  anomaly_count INT64
)
PARTITION BY DATE(hour_ts)
CLUSTER BY device_id
OPTIONS (
  description = "Hourly aggregated energy consumption metrics"
);

-- Daily aggregated data
CREATE OR REPLACE TABLE `{project_id}.powerlytics_dwh.analytics_daily` (
  device_id STRING NOT NULL,
  date_ts DATE NOT NULL,
  total_energy_wh FLOAT64,
  avg_power_w FLOAT64,
  peak_power_w FLOAT64,
  peak_hour INT64,
  low_power_hours INT64,
  anomaly_count INT64,
  cost_estimate_usd FLOAT64,
  carbon_footprint_kg FLOAT64
)
PARTITION BY date_ts
CLUSTER BY device_id
OPTIONS (
  description = "Daily aggregated energy consumption and cost metrics"
);

-- Device metadata table
CREATE OR REPLACE TABLE `{project_id}.powerlytics_dwh.device_metadata` (
  device_id STRING NOT NULL,
  device_name STRING,
  device_type STRING,
  location STRING,
  installation_date DATE,
  capacity_w FLOAT64,
  efficiency_rating FLOAT64,
  manufacturer STRING,
  model STRING,
  last_maintenance DATE,
  status STRING,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
CLUSTER BY device_id, device_type
OPTIONS (
  description = "Device metadata and configuration information"
);

-- ML features table for model training
CREATE OR REPLACE TABLE `{project_id}.powerlytics_dwh.ml_features` (
  device_id STRING NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  power_w FLOAT64,
  energy_wh FLOAT64,
  hour_of_day INT64,
  day_of_week INT64,
  month INT64,
  is_weekend BOOL,
  is_holiday BOOL,
  temp_c FLOAT64,
  occupancy BOOL,
  power_lag_1h FLOAT64,
  power_lag_24h FLOAT64,
  power_rolling_avg_1h FLOAT64,
  power_rolling_avg_24h FLOAT64,
  power_rolling_std_24h FLOAT64,
  energy_delta_1h FLOAT64,
  energy_delta_24h FLOAT64,
  anomaly_score FLOAT64,
  is_anomaly BOOL
)
PARTITION BY DATE(timestamp)
CLUSTER BY device_id
OPTIONS (
  description = "Engineered features for ML model training and prediction"
);

-- Forecasts table for storing predictions
CREATE OR REPLACE TABLE `{project_id}.powerlytics_dwh.forecasts` (
  device_id STRING NOT NULL,
  forecast_timestamp TIMESTAMP NOT NULL,
  prediction_horizon_hours INT64,
  predicted_power_w FLOAT64,
  confidence_interval_lower FLOAT64,
  confidence_interval_upper FLOAT64,
  model_version STRING,
  created_at TIMESTAMP
)
PARTITION BY DATE(forecast_timestamp)
CLUSTER BY device_id, prediction_horizon_hours
OPTIONS (
  description = "Energy consumption forecasts from ML models"
);

-- Recommendations table for storing AI-generated insights
CREATE OR REPLACE TABLE `{project_id}.powerlytics_dwh.recommendations` (
  device_id STRING NOT NULL,
  recommendation_id STRING NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  type STRING NOT NULL,
  priority STRING NOT NULL,
  title STRING NOT NULL,
  description STRING,
  action_required STRING,
  potential_savings_usd FLOAT64,
  potential_savings_percent FLOAT64,
  confidence_score FLOAT64,
  status STRING,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
PARTITION BY DATE(timestamp)
CLUSTER BY device_id, type, priority
OPTIONS (
  description = "AI-generated energy optimization recommendations"
);

-- Create views for common queries
CREATE OR REPLACE VIEW `{project_id}.powerlytics_dwh.current_usage` AS
SELECT 
  device_id,
  power_w,
  energy_wh,
  timestamp,
  ROW_NUMBER() OVER (PARTITION BY device_id ORDER BY timestamp DESC) as rn
FROM `{project_id}.powerlytics_dwh.raw_readings`
WHERE DATE(timestamp) = CURRENT_DATE();

CREATE OR REPLACE VIEW `{project_id}.powerlytics_dwh.device_summary` AS
SELECT 
  d.device_id,
  d.device_name,
  d.device_type,
  d.location,
  c.power_w as current_power,
  c.energy_wh as total_energy_today,
  h.avg_power_w as avg_power_last_24h,
  h.anomaly_count as anomalies_last_24h
FROM `{project_id}.powerlytics_dwh.device_metadata` d
LEFT JOIN `{project_id}.powerlytics_dwh.current_usage` c 
  ON d.device_id = c.device_id AND c.rn = 1
LEFT JOIN `{project_id}.powerlytics_dwh.analytics_hourly` h
  ON d.device_id = h.device_id 
  AND h.hour_ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
  AND h.hour_ts = (
    SELECT MAX(hour_ts) 
    FROM `{project_id}.powerlytics_dwh.analytics_hourly` h2 
    WHERE h2.device_id = h.device_id
  );

-- Insert sample device metadata
(REPLACED_TABLE)
INSERT INTO `{project_id}.powerlytics_dwh.device_metadata` 
(device_id, device_name, device_type, location, installation_date, capacity_w, efficiency_rating, manufacturer, model, status, created_at, updated_at)
VALUES
('device_001', 'Main House Panel', 'electrical_panel', 'main_floor', '2023-01-15', 5000.0, 0.95, 'Powerlytics', 'PL-Panel-5000', 'active', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('device_002', 'Garage Workshop', 'workshop', 'garage', '2023-02-01', 2000.0, 0.90, 'Powerlytics', 'PL-Workshop-2000', 'active', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('device_003', 'HVAC System', 'hvac', 'basement', '2023-01-20', 3000.0, 0.88, 'Powerlytics', 'PL-HVAC-3000', 'active', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('device_004', 'Kitchen Appliances', 'appliances', 'kitchen', '2023-03-01', 1500.0, 0.92, 'Powerlytics', 'PL-Kitchen-1500', 'active', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP()),
('device_005', 'Smart Lighting', 'lighting', 'throughout', '2023-02-15', 800.0, 0.98, 'Powerlytics', 'PL-Lighting-800', 'active', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());
