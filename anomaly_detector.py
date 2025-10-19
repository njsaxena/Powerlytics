"""
Anomaly Detection for EcoGridIQ
Real-time anomaly detection using statistical methods and ML models
"""

import os
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

@dataclass
class AnomalyResult:
    """Anomaly detection result"""
    device_id: str
    timestamp: datetime
    power_w: float
    anomaly_score: float
    severity: str
    type: str
    confidence: float
    explanation: str

class AnomalyDetector:
    """Real-time anomaly detection for energy consumption"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.anomaly_thresholds = {
            'low': 2.0,      # 2 standard deviations
            'medium': 3.0,   # 3 standard deviations
            'high': 4.0      # 4 standard deviations
        }
    
    async def detect_realtime_anomalies(self) -> List[Dict[str, Any]]:
        """Detect anomalies in real-time data"""
        try:
            # This would typically fetch recent data from BigQuery
            # For now, return empty list as this is a mock implementation
            return []
        except Exception as e:
            logger.error(f"Real-time anomaly detection failed: {str(e)}")
            return []
    
    async def detect_anomalies_in_data(
        self,
        device_id: str,
        data_points: List[Dict[str, Any]]
    ) -> List[AnomalyResult]:
        """Detect anomalies in a dataset"""
        
        if len(data_points) < 10:  # Need minimum data for detection
            return []
        
        try:
            # Extract power values
            power_values = [dp['power_w'] for dp in data_points if 'power_w' in dp]
            timestamps = [dp['timestamp'] for dp in data_points if 'timestamp' in dp]
            
            if len(power_values) < 10:
                return []
            
            # Convert to numpy array for easier processing
            power_array = np.array(power_values)
            
            # Detect different types of anomalies
            anomalies = []
            
            # 1. Statistical anomalies (Z-score based)
            statistical_anomalies = await self._detect_statistical_anomalies(
                device_id, power_array, timestamps
            )
            anomalies.extend(statistical_anomalies)
            
            # 2. Trend anomalies
            trend_anomalies = await self._detect_trend_anomalies(
                device_id, power_array, timestamps
            )
            anomalies.extend(trend_anomalies)
            
            # 3. Seasonal anomalies
            seasonal_anomalies = await self._detect_seasonal_anomalies(
                device_id, power_array, timestamps
            )
            anomalies.extend(seasonal_anomalies)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Anomaly detection failed for {device_id}: {str(e)}")
            return []
    
    async def _detect_statistical_anomalies(
        self,
        device_id: str,
        power_values: np.ndarray,
        timestamps: List[datetime]
    ) -> List[AnomalyResult]:
        """Detect statistical anomalies using Z-score method"""
        
        anomalies = []
        
        # Calculate rolling statistics
        window_size = min(24, len(power_values) // 2)  # 24-hour window or half the data
        
        for i in range(window_size, len(power_values)):
            # Get window data
            window_data = power_values[i-window_size:i]
            
            # Calculate statistics
            mean = np.mean(window_data)
            std = np.std(window_data)
            
            if std == 0:  # Avoid division by zero
                continue
            
            # Calculate Z-score for current value
            z_score = abs(power_values[i] - mean) / std
            
            # Determine severity
            severity = 'low'
            if z_score >= self.anomaly_thresholds['high']:
                severity = 'high'
            elif z_score >= self.anomaly_thresholds['medium']:
                severity = 'medium'
            elif z_score >= self.anomaly_thresholds['low']:
                severity = 'low'
            else:
                continue  # Not an anomaly
            
            # Create anomaly result
            anomaly = AnomalyResult(
                device_id=device_id,
                timestamp=timestamps[i],
                power_w=float(power_values[i]),
                anomaly_score=float(z_score),
                severity=severity,
                type='statistical',
                confidence=min(0.95, z_score / 5.0),  # Confidence based on Z-score
                explanation=f"Power consumption {z_score:.1f} standard deviations above normal"
            )
            
            anomalies.append(anomaly)
        
        return anomalies
    
    async def _detect_trend_anomalies(
        self,
        device_id: str,
        power_values: np.ndarray,
        timestamps: List[datetime]
    ) -> List[AnomalyResult]:
        """Detect trend-based anomalies"""
        
        anomalies = []
        
        if len(power_values) < 12:  # Need at least 12 data points
            return anomalies
        
        # Calculate rolling trend
        window_size = 6  # 6-hour window for trend analysis
        
        for i in range(window_size, len(power_values)):
            window_data = power_values[i-window_size:i]
            
            # Calculate linear trend
            x = np.arange(len(window_data))
            coeffs = np.polyfit(x, window_data, 1)
            trend_slope = coeffs[0]
            
            # Check for sudden trend changes
            if abs(trend_slope) > np.std(window_data) * 0.5:  # Significant trend
                # Check if current value deviates from trend
                predicted_value = coeffs[0] * len(window_data) + coeffs[1]
                actual_value = power_values[i]
                deviation = abs(actual_value - predicted_value)
                
                if deviation > np.std(window_data) * 1.5:  # Significant deviation
                    anomaly = AnomalyResult(
                        device_id=device_id,
                        timestamp=timestamps[i],
                        power_w=float(actual_value),
                        anomaly_score=float(deviation / np.std(window_data)),
                        severity='medium',
                        type='trend',
                        confidence=0.8,
                        explanation=f"Sudden deviation from trend: {deviation:.1f}W difference"
                    )
                    anomalies.append(anomaly)
        
        return anomalies
    
    async def _detect_seasonal_anomalies(
        self,
        device_id: str,
        power_values: np.ndarray,
        timestamps: List[datetime]
    ) -> List[AnomalyResult]:
        """Detect seasonal anomalies based on time of day patterns"""
        
        anomalies = []
        
        if len(power_values) < 48:  # Need at least 2 days of data
            return anomalies
        
        # Group by hour of day
        hourly_groups = {}
        for i, timestamp in enumerate(timestamps):
            hour = timestamp.hour
            if hour not in hourly_groups:
                hourly_groups[hour] = []
            hourly_groups[hour].append((i, power_values[i]))
        
        # Calculate hourly baselines
        hourly_baselines = {}
        for hour, values in hourly_groups.items():
            if len(values) >= 3:  # Need at least 3 samples
                power_vals = [v[1] for v in values]
                hourly_baselines[hour] = {
                    'mean': np.mean(power_vals),
                    'std': np.std(power_vals)
                }
        
        # Check for anomalies based on hourly patterns
        for i, (timestamp, power) in enumerate(zip(timestamps, power_values)):
            hour = timestamp.hour
            
            if hour in hourly_baselines:
                baseline = hourly_baselines[hour]
                if baseline['std'] > 0:
                    z_score = abs(power - baseline['mean']) / baseline['std']
                    
                    if z_score >= self.anomaly_thresholds['medium']:
                        severity = 'high' if z_score >= self.anomaly_thresholds['high'] else 'medium'
                        
                        anomaly = AnomalyResult(
                            device_id=device_id,
                            timestamp=timestamp,
                            power_w=float(power),
                            anomaly_score=float(z_score),
                            severity=severity,
                            type='seasonal',
                            confidence=min(0.9, z_score / 4.0),
                            explanation=f"Unusual consumption for {hour}:00 - {z_score:.1f} std devs from normal"
                        )
                        anomalies.append(anomaly)
        
        return anomalies
    
    def calculate_anomaly_score(
        self,
        current_power: float,
        historical_power: List[float],
        method: str = 'zscore'
    ) -> float:
        """Calculate anomaly score for a single data point"""
        
        if not historical_power or len(historical_power) < 5:
            return 0.0
        
        historical_array = np.array(historical_power)
        mean = np.mean(historical_array)
        std = np.std(historical_array)
        
        if std == 0:
            return 0.0
        
        if method == 'zscore':
            return abs(current_power - mean) / std
        elif method == 'modified_zscore':
            # Use median absolute deviation for more robust detection
            median = np.median(historical_array)
            mad = np.median(np.abs(historical_array - median))
            if mad == 0:
                return 0.0
            return 0.6745 * abs(current_power - median) / mad
        else:
            return 0.0
    
    def get_anomaly_explanation(
        self,
        anomaly: AnomalyResult,
        context: Dict[str, Any]
    ) -> str:
        """Generate human-readable explanation for an anomaly"""
        
        explanations = {
            'statistical': f"Power consumption is {anomaly.anomaly_score:.1f} standard deviations above normal levels",
            'trend': f"Sudden deviation from established usage trend",
            'seasonal': f"Unusual consumption pattern for this time of day"
        }
        
        base_explanation = explanations.get(anomaly.type, "Unusual energy consumption pattern detected")
        
        # Add context-specific information
        if context.get('device_type'):
            base_explanation += f" for {context['device_type']}"
        
        if context.get('time_of_day'):
            base_explanation += f" at {context['time_of_day']}"
        
        return base_explanation
    
    async def get_anomaly_recommendations(
        self,
        anomaly: AnomalyResult,
        device_context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on anomaly type"""
        
        recommendations = []
        
        if anomaly.type == 'statistical' and anomaly.severity == 'high':
            recommendations.append({
                'type': 'immediate_action',
                'title': 'Check for Malfunctioning Equipment',
                'description': 'High power consumption may indicate equipment malfunction',
                'action': 'Inspect major appliances and electrical systems',
                'priority': 'high'
            })
        
        elif anomaly.type == 'trend':
            recommendations.append({
                'type': 'monitoring',
                'title': 'Monitor Usage Patterns',
                'description': 'Track usage to identify the cause of trend change',
                'action': 'Check recent changes in usage habits or equipment',
                'priority': 'medium'
            })
        
        elif anomaly.type == 'seasonal':
            recommendations.append({
                'type': 'optimization',
                'title': 'Optimize Time-Based Usage',
                'description': 'Consider shifting high-energy activities to off-peak hours',
                'action': 'Schedule major appliances during lower-cost periods',
                'priority': 'low'
            })
        
        return recommendations
