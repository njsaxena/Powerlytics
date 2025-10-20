-- Feature Engineering SQL for Powerlytics ML Models
CREATE OR REPLACE TABLE `{project_id}.powerlytics_dwh.analytics_hourly` AS
WITH hourly_base AS (
  SELECT 
    device_id,
    TIMESTAMP_TRUNC(timestamp, HOUR) AS hour_ts,
    AVG(power_w) AS avg_power_w,
    MAX(power_w) AS max_power_w,
    MIN(power_w) AS min_power_w,
    SUM(energy_wh) AS total_energy_wh,
    COUNTIF(power_w > 5000) AS high_power_events,
    AVG(voltage) AS avg_voltage,
    AVG(temp_c) AS avg_temp_c,
    AVG(CAST(occupancy AS FLOAT64)) AS occupancy_percentage,
    COUNTIF(power_w > 2 * AVG(power_w) OVER (PARTITION BY device_id ORDER BY TIMESTAMP_TRUNC(timestamp, HOUR) ROWS BETWEEN 23 PRECEDING AND CURRENT ROW)) AS anomaly_count
  FROM `{project_id}.powerlytics_dwh.raw_readings`
  WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  GROUP BY device_id, hour_ts
),
rolling_stats AS (
  SELECT 
    *,
    AVG(avg_power_w) OVER (PARTITION BY device_id ORDER BY hour_ts ROWS BETWEEN 23 PRECEDING AND CURRENT ROW) AS power_rolling_avg_24h,
    STDDEV(avg_power_w) OVER (PARTITION BY device_id ORDER BY hour_ts ROWS BETWEEN 23 PRECEDING AND CURRENT ROW) AS power_rolling_std_24h,
    LAG(avg_power_w, 1) OVER (PARTITION BY device_id ORDER BY hour_ts) AS power_lag_1h,
    LAG(avg_power_w, 24) OVER (PARTITION BY device_id ORDER BY hour_ts) AS power_lag_24h
  FROM hourly_base
)
SELECT 
  device_id,
  hour_ts,
  avg_power_w,
  max_power_w,
  min_power_w,
  total_energy_wh,
  high_power_events,
  avg_voltage,
  avg_temp_c,
  occupancy_percentage,
  anomaly_count,
  power_rolling_avg_24h,
  power_rolling_std_24h,
  power_lag_1h,
  power_lag_24h,
  -- Anomaly detection features
  CASE 
    WHEN power_rolling_std_24h > 0 THEN 
      ABS(avg_power_w - power_rolling_avg_24h) / power_rolling_std_24h
    ELSE 0 
  END AS z_score,
  CASE 
    WHEN ABS(avg_power_w - power_rolling_avg_24h) / NULLIF(power_rolling_std_24h, 0) > 3 THEN 1 
    ELSE 0 
  END AS is_anomaly
FROM rolling_stats;

-- Daily aggregation with cost and carbon footprint estimates
CREATE OR REPLACE TABLE `{project_id}.powerlytics_dwh.analytics_daily` AS
WITH daily_base AS (
  SELECT 
    device_id,
    DATE(timestamp) AS date_ts,
    SUM(energy_wh) AS total_energy_wh,
    AVG(power_w) AS avg_power_w,
    MAX(power_w) AS peak_power_w,
    EXTRACT(HOUR FROM timestamp) AS hour_of_day
  FROM `{project_id}.powerlytics_dwh.raw_readings`
  WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  GROUP BY device_id, date_ts, hour_of_day
),
daily_aggregated AS (
  SELECT 
    device_id,
    date_ts,
    SUM(total_energy_wh) AS total_energy_wh,
    AVG(avg_power_w) AS avg_power_w,
    MAX(peak_power_w) AS peak_power_w,
    ARRAY_AGG(hour_of_day ORDER BY peak_power_w DESC LIMIT 1)[OFFSET(0)] AS peak_hour,
    COUNTIF(avg_power_w < 100) AS low_power_hours,
    COUNTIF(avg_power_w > 2 * AVG(avg_power_w) OVER (PARTITION BY device_id, date_ts)) AS anomaly_count
  FROM daily_base
  GROUP BY device_id, date_ts
)
SELECT 
  *,
  -- Cost estimation (assuming $0.12/kWh average)
  total_energy_wh / 1000 * 0.12 AS cost_estimate_usd,
  -- Carbon footprint estimation (assuming 0.4 kg CO2/kWh)
  total_energy_wh / 1000 * 0.4 AS carbon_footprint_kg
FROM daily_aggregated;

-- ML Features table with comprehensive feature engineering
CREATE OR REPLACE TABLE `{project_id}.powerlytics_dwh.ml_features` AS
WITH base_features AS (
  SELECT 
    r.device_id,
    r.timestamp,
    r.power_w,
    r.energy_wh,
    EXTRACT(HOUR FROM r.timestamp) AS hour_of_day,
    EXTRACT(DAYOFWEEK FROM r.timestamp) AS day_of_week,
    EXTRACT(MONTH FROM r.timestamp) AS month,
    EXTRACT(DAYOFWEEK FROM r.timestamp) IN (1, 7) AS is_weekend,
    -- Simple holiday detection (can be enhanced with external data)
    EXTRACT(MONTH FROM r.timestamp) = 12 AND EXTRACT(DAY FROM r.timestamp) = 25 AS is_holiday,
    r.temp_c,
    r.occupancy,
    -- Lag features
    LAG(r.power_w, 1) OVER (PARTITION BY r.device_id ORDER BY r.timestamp) AS power_lag_1h,
    LAG(r.power_w, 12) OVER (PARTITION BY r.device_id ORDER BY r.timestamp) AS power_lag_12h,
    LAG(r.power_w, 24) OVER (PARTITION BY r.device_id ORDER BY r.timestamp) AS power_lag_24h,
    -- Rolling averages
    AVG(r.power_w) OVER (PARTITION BY r.device_id ORDER BY r.timestamp ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) AS power_rolling_avg_1h,
    AVG(r.power_w) OVER (PARTITION BY r.device_id ORDER BY r.timestamp ROWS BETWEEN 23 PRECEDING AND CURRENT ROW) AS power_rolling_avg_24h,
    STDDEV(r.power_w) OVER (PARTITION BY r.device_id ORDER BY r.timestamp ROWS BETWEEN 23 PRECEDING AND CURRENT ROW) AS power_rolling_std_24h,
    -- Energy deltas
    r.energy_wh - LAG(r.energy_wh, 1) OVER (PARTITION BY r.device_id ORDER BY r.timestamp) AS energy_delta_1h,
    r.energy_wh - LAG(r.energy_wh, 12) OVER (PARTITION BY r.device_id ORDER BY r.timestamp) AS energy_delta_12h,
    r.energy_wh - LAG(r.energy_wh, 24) OVER (PARTITION BY r.device_id ORDER BY r.timestamp) AS energy_delta_24h
  FROM `{project_id}.powerlytics_dwh.raw_readings` r
  WHERE r.timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
),
anomaly_detection AS (
  SELECT 
    *,
    -- Z-score based anomaly detection
    CASE 
      WHEN power_rolling_std_24h > 0 THEN 
        ABS(power_w - power_rolling_avg_24h) / power_rolling_std_24h
      ELSE 0 
    END AS anomaly_score,
    CASE 
      WHEN ABS(power_w - power_rolling_avg_24h) / NULLIF(power_rolling_std_24h, 0) > 3 THEN 1 
      ELSE 0 
    END AS is_anomaly
  FROM base_features
)
SELECT 
  device_id,
  timestamp,
  power_w,
  energy_wh,
  hour_of_day,
  day_of_week,
  month,
  is_weekend,
  is_holiday,
  temp_c,
  occupancy,
  power_lag_1h,
  power_lag_12h,
  power_lag_24h,
  power_rolling_avg_1h,
  power_rolling_avg_24h,
  power_rolling_std_24h,
  energy_delta_1h,
  energy_delta_12h,
  energy_delta_24h,
  anomaly_score,
  is_anomaly
FROM anomaly_detection;

-- Create materialized view for real-time anomaly detection
CREATE OR REPLACE MATERIALIZED VIEW `{project_id}.powerlytics_dwh.realtime_anomalies` AS
SELECT 
  device_id,
  timestamp,
  power_w,
  anomaly_score,
  CASE 
    WHEN anomaly_score > 3 THEN 'high'
    WHEN anomaly_score > 2 THEN 'medium'
    WHEN anomaly_score > 1.5 THEN 'low'
    ELSE 'normal'
  END AS severity,
  power_rolling_avg_24h,
  power_rolling_std_24h
FROM `{project_id}.powerlytics_dwh.ml_features`
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
  AND anomaly_score > 1.5
ORDER BY timestamp DESC;

-- Create view for model training data
CREATE OR REPLACE VIEW `{project_id}.powerlytics_dwh.training_data` AS
SELECT 
  device_id,
  timestamp,
  power_w,
  hour_of_day,
  day_of_week,
  month,
  is_weekend,
  is_holiday,
  temp_c,
  occupancy,
  power_lag_1h,
  power_lag_12h,
  power_lag_24h,
  power_rolling_avg_1h,
  power_rolling_avg_24h,
  power_rolling_std_24h,
  energy_delta_1h,
  energy_delta_12h,
  energy_delta_24h,
  anomaly_score,
  is_anomaly
FROM `{project_id}.powerlytics_dwh.ml_features`
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
  AND power_lag_1h IS NOT NULL
  AND power_lag_12h IS NOT NULL
  AND power_lag_24h IS NOT NULL;
