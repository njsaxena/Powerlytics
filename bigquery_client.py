"""
BigQuery Client for EcoGridIQ
Handles all BigQuery operations for data retrieval and analysis
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class BigQueryClient:
    """Client for BigQuery operations"""
    
    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "ecogrid-iq")
        self.dataset_id = os.getenv("BIGQUERY_DATASET", "ecogrid_dwh")
        self.client = bigquery.Client(project=self.project_id)
        self.dataset_ref = self.client.dataset(self.dataset_id)
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def _run_query_async(self, query: str) -> List[Dict[str, Any]]:
        """Run a BigQuery query asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self._run_query_sync, query)
    
    def _run_query_sync(self, query: str) -> List[Dict[str, Any]]:
        """Run a BigQuery query synchronously"""
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"BigQuery query failed: {str(e)}")
            raise
    
    def test_connection(self) -> bool:
        """Test BigQuery connection"""
        try:
            query = f"SELECT 1 as test"
            self.client.query(query).result()
            return True
        except Exception as e:
            logger.error(f"BigQuery connection test failed: {str(e)}")
            return False
    
    async def get_devices(self) -> List[Dict[str, Any]]:
        """Get list of all devices with current status"""
        query = f"""
        SELECT 
            d.device_id,
            d.device_name,
            d.device_type,
            d.location,
            d.capacity_w,
            d.status,
            c.power_w as current_power,
            c.energy_wh as total_energy_today,
            h.avg_power_w as avg_power_last_24h,
            h.anomaly_count as anomalies_last_24h
        FROM `{self.project_id}.{self.dataset_id}.device_metadata` d
        LEFT JOIN `{self.project_id}.{self.dataset_id}.current_usage` c 
            ON d.device_id = c.device_id AND c.rn = 1
        LEFT JOIN `{self.project_id}.{self.dataset_id}.analytics_hourly` h
            ON d.device_id = h.device_id 
            AND h.hour_ts >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
            AND h.hour_ts = (
                SELECT MAX(hour_ts) 
                FROM `{self.project_id}.{self.dataset_id}.analytics_hourly` h2 
                WHERE h2.device_id = h.device_id
            )
        WHERE d.status = 'active'
        ORDER BY d.device_id
        """
        return await self._run_query_async(query)
    
    async def get_current_usage(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get current usage for a specific device"""
        query = f"""
        SELECT 
            device_id,
            power_w,
            energy_wh,
            timestamp,
            voltage,
            temp_c,
            occupancy
        FROM `{self.project_id}.{self.dataset_id}.raw_readings`
        WHERE device_id = @device_id
        ORDER BY timestamp DESC
        LIMIT 1
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("device_id", "STRING", device_id)
            ]
        )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            rows = list(results)
            return dict(rows[0]) if rows else None
        except Exception as e:
            logger.error(f"Failed to get current usage for {device_id}: {str(e)}")
            return None
    
    async def get_usage_history(self, device_id: str, hours: int) -> List[Dict[str, Any]]:
        """Get usage history for a specific device"""
        query = f"""
        SELECT 
            device_id,
            timestamp,
            power_w,
            energy_wh,
            voltage,
            temp_c,
            occupancy
        FROM `{self.project_id}.{self.dataset_id}.raw_readings`
        WHERE device_id = @device_id
            AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @hours HOUR)
        ORDER BY timestamp ASC
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("device_id", "STRING", device_id),
                bigquery.ScalarQueryParameter("hours", "INT64", hours)
            ]
        )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Failed to get usage history for {device_id}: {str(e)}")
            return []
    
    async def get_anomalies(
        self, 
        device_id: Optional[str] = None,
        since: Optional[datetime] = None,
        severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get detected anomalies"""
        if since is None:
            since = datetime.now() - timedelta(hours=24)
        
        query = f"""
        SELECT 
            device_id,
            timestamp,
            type,
            severity,
            original_power,
            anomaly_power,
            confidence,
            detected_at
        FROM `{self.project_id}.{self.dataset_id}.anomalies`
        WHERE timestamp >= @since
        """
        
        params = [bigquery.ScalarQueryParameter("since", "TIMESTAMP", since)]
        
        if device_id:
            query += " AND device_id = @device_id"
            params.append(bigquery.ScalarQueryParameter("device_id", "STRING", device_id))
        
        if severity:
            query += " AND severity = @severity"
            params.append(bigquery.ScalarQueryParameter("severity", "STRING", severity))
        
        query += " ORDER BY timestamp DESC"
        
        job_config = bigquery.QueryJobConfig(query_parameters=params)
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Failed to get anomalies: {str(e)}")
            return []
    
    async def get_chat_context(self, device_id: Optional[str], query: str) -> Dict[str, Any]:
        """Get relevant context for chat responses"""
        context = {
            "recent_anomalies": [],
            "usage_patterns": {},
            "device_info": {},
            "cost_analysis": {}
        }
        
        try:
            # Get recent anomalies
            context["recent_anomalies"] = await self.get_anomalies(
                device_id=device_id,
                since=datetime.now() - timedelta(hours=24)
            )
            
            # Get device information
            if device_id:
                devices = await self.get_devices()
                context["device_info"] = next(
                    (d for d in devices if d["device_id"] == device_id), 
                    {}
                )
                
                # Get usage patterns
                context["usage_patterns"] = await self.get_device_analysis(device_id)
            
            # Get cost analysis
            context["cost_analysis"] = await self.get_cost_analysis(device_id)
            
        except Exception as e:
            logger.error(f"Failed to get chat context: {str(e)}")
        
        return context
    
    async def get_device_analysis(self, device_id: str) -> Dict[str, Any]:
        """Get detailed analysis for a device"""
        query = f"""
        WITH device_stats AS (
            SELECT 
                AVG(power_w) as avg_power,
                MAX(power_w) as max_power,
                MIN(power_w) as min_power,
                STDDEV(power_w) as power_std,
                COUNT(*) as reading_count
            FROM `{self.project_id}.{self.dataset_id}.raw_readings`
            WHERE device_id = @device_id
                AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
        ),
        hourly_patterns AS (
            SELECT 
                EXTRACT(HOUR FROM timestamp) as hour,
                AVG(power_w) as avg_power_hourly
            FROM `{self.project_id}.{self.dataset_id}.raw_readings`
            WHERE device_id = @device_id
                AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
            GROUP BY hour
            ORDER BY hour
        )
        SELECT 
            (SELECT * FROM device_stats) as stats,
            ARRAY_AGG(STRUCT(hour, avg_power_hourly) ORDER BY hour) as hourly_pattern
        FROM hourly_patterns
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("device_id", "STRING", device_id)
            ]
        )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            rows = list(results)
            return dict(rows[0]) if rows else {}
        except Exception as e:
            logger.error(f"Failed to get device analysis for {device_id}: {str(e)}")
            return {}
    
    async def get_cost_analysis(self, device_id: Optional[str] = None) -> Dict[str, Any]:
        """Get cost analysis data"""
        query = f"""
        SELECT 
            SUM(total_energy_wh) as total_energy_wh,
            SUM(cost_estimate_usd) as total_cost_usd,
            SUM(carbon_footprint_kg) as total_carbon_kg,
            AVG(cost_estimate_usd) as avg_daily_cost
        FROM `{self.project_id}.{self.dataset_id}.analytics_daily`
        WHERE date_ts >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        """
        
        if device_id:
            query += " AND device_id = @device_id"
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("device_id", "STRING", device_id)
                ]
            )
        else:
            job_config = bigquery.QueryJobConfig()
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            rows = list(results)
            return dict(rows[0]) if rows else {}
        except Exception as e:
            logger.error(f"Failed to get cost analysis: {str(e)}")
            return {}
    
    async def get_total_energy_today(self) -> float:
        """Get total energy consumption today"""
        query = f"""
        SELECT SUM(total_energy_wh) as total_energy
        FROM `{self.project_id}.{self.dataset_id}.analytics_daily`
        WHERE date_ts = CURRENT_DATE()
        """
        
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            rows = list(results)
            return rows[0].total_energy if rows and rows[0].total_energy else 0.0
        except Exception as e:
            logger.error(f"Failed to get total energy today: {str(e)}")
            return 0.0
    
    async def get_usage_trends(self, hours: int) -> List[Dict[str, Any]]:
        """Get usage trends for dashboard"""
        query = f"""
        SELECT 
            TIMESTAMP_TRUNC(timestamp, HOUR) as hour_ts,
            AVG(power_w) as avg_power,
            SUM(energy_wh) as total_energy
        FROM `{self.project_id}.{self.dataset_id}.raw_readings`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @hours HOUR)
        GROUP BY hour_ts
        ORDER BY hour_ts
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("hours", "INT64", hours)
            ]
        )
        
        try:
            query_job = self.client.query(query, job_config=job_config)
            results = query_job.result()
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Failed to get usage trends: {str(e)}")
            return []
