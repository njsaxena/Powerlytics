"""
Mock Device API for EcoGridIQ
Simulates IoT energy meter readings with realistic patterns and anomalies
"""

import json
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np

app = Flask(__name__)
CORS(app)

# Global state for device data
devices_data = {}
anomaly_events = []

class EnergyDevice:
    def __init__(self, device_id: str, base_power: float = 1000.0):
        self.device_id = device_id
        self.base_power = base_power
        self.energy_wh = 0.0
        self.last_reading = datetime.now()
        self.patterns = {
            'daily_cycle': True,
            'weekend_low': True,
            'seasonal': True
        }
    
    def generate_reading(self, timestamp: datetime) -> Dict:
        """Generate a realistic energy reading with patterns and occasional anomalies"""
        
        # Base power consumption with daily cycle
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        
        # Daily pattern (higher during day, lower at night)
        daily_factor = 0.3 + 0.7 * (0.5 + 0.5 * np.sin(2 * np.pi * (hour - 6) / 24))
        
        # Weekend pattern (lower consumption on weekends)
        weekend_factor = 0.7 if day_of_week >= 5 else 1.0
        
        # Seasonal pattern (higher in summer/winter for HVAC)
        month = timestamp.month
        seasonal_factor = 1.0 + 0.3 * abs(np.sin(2 * np.pi * (month - 1) / 12))
        
        # Random variation
        random_factor = 0.8 + 0.4 * random.random()
        
        # Calculate power
        power_w = self.base_power * daily_factor * weekend_factor * seasonal_factor * random_factor
        
        # Add occasional anomalies (5% chance)
        if random.random() < 0.05:
            anomaly_type = random.choice(['spike', 'drop', 'sustained_high'])
            if anomaly_type == 'spike':
                power_w *= random.uniform(2.0, 4.0)
                anomaly_events.append({
                    'device_id': self.device_id,
                    'timestamp': timestamp.isoformat(),
                    'type': 'power_spike',
                    'severity': 'high',
                    'original_power': power_w / random.uniform(2.0, 4.0),
                    'anomaly_power': power_w
                })
            elif anomaly_type == 'drop':
                power_w *= random.uniform(0.1, 0.3)
            elif anomaly_type == 'sustained_high':
                power_w *= random.uniform(1.5, 2.0)
        
        # Calculate energy increment (assuming 5-minute intervals)
        energy_increment = power_w * (5 / 60)  # 5 minutes in hours
        self.energy_wh += energy_increment
        
        reading = {
            'device_id': self.device_id,
            'timestamp': timestamp.isoformat(),
            'power_w': round(power_w, 2),
            'energy_wh': round(self.energy_wh, 2),
            'voltage': round(120 + random.uniform(-5, 5), 1),
            'occupancy': random.random() > 0.3,  # 70% chance occupied
            'temp_c': round(20 + random.uniform(-3, 3), 1),
            'source': 'mock_device',
            'ingest_ts': datetime.now().isoformat()
        }
        
        return reading

# Initialize devices
devices = {
    'device_001': EnergyDevice('device_001', 1200.0),  # Main house
    'device_002': EnergyDevice('device_002', 800.0),   # Garage/workshop
    'device_003': EnergyDevice('device_003', 600.0),   # HVAC system
    'device_004': EnergyDevice('device_004', 400.0),   # Kitchen appliances
    'device_005': EnergyDevice('device_005', 200.0),   # Lighting
}

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/devices', methods=['GET'])
def get_devices():
    """Get list of available devices"""
    device_list = []
    for device_id, device in devices.items():
        device_list.append({
            'device_id': device_id,
            'base_power_w': device.base_power,
            'last_reading': device.last_reading.isoformat(),
            'total_energy_wh': device.energy_wh
        })
    return jsonify({'devices': device_list})

@app.route('/readings', methods=['GET'])
def get_readings():
    """Get energy readings for a specific device and time range"""
    device_id = request.args.get('device_id')
    start_time = request.args.get('start')
    end_time = request.args.get('end')
    limit = int(request.args.get('limit', 100))
    
    if not device_id or device_id not in devices:
        return jsonify({'error': 'Invalid device_id'}), 400
    
    # Parse time range
    if start_time:
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    else:
        start_dt = datetime.now() - timedelta(hours=24)
    
    if end_time:
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    else:
        end_dt = datetime.now()
    
    # Generate readings
    readings = []
    current_time = start_dt
    device = devices[device_id]
    
    while current_time <= end_dt and len(readings) < limit:
        reading = device.generate_reading(current_time)
        readings.append(reading)
        current_time += timedelta(minutes=5)  # 5-minute intervals
    
    return jsonify({
        'device_id': device_id,
        'start_time': start_dt.isoformat(),
        'end_time': end_dt.isoformat(),
        'count': len(readings),
        'data': readings
    })

@app.route('/readings/latest', methods=['GET'])
def get_latest_readings():
    """Get latest readings for all devices"""
    latest_readings = []
    current_time = datetime.now()
    
    for device_id, device in devices.items():
        reading = device.generate_reading(current_time)
        latest_readings.append(reading)
        device.last_reading = current_time
    
    return jsonify({
        'timestamp': current_time.isoformat(),
        'readings': latest_readings
    })

@app.route('/anomalies', methods=['GET'])
def get_anomalies():
    """Get detected anomalies"""
    device_id = request.args.get('device_id')
    since = request.args.get('since')
    
    filtered_anomalies = anomaly_events.copy()
    
    if device_id:
        filtered_anomalies = [a for a in filtered_anomalies if a['device_id'] == device_id]
    
    if since:
        since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
        filtered_anomalies = [a for a in filtered_anomalies 
                            if datetime.fromisoformat(a['timestamp']) >= since_dt]
    
    return jsonify({
        'anomalies': filtered_anomalies,
        'count': len(filtered_anomalies)
    })

@app.route('/simulate/anomaly', methods=['POST'])
def simulate_anomaly():
    """Simulate an anomaly for testing purposes"""
    data = request.get_json()
    device_id = data.get('device_id', random.choice(list(devices.keys())))
    anomaly_type = data.get('type', 'spike')
    severity = data.get('severity', 'high')
    
    device = devices[device_id]
    timestamp = datetime.now()
    
    # Generate anomaly
    if anomaly_type == 'spike':
        multiplier = 3.0 if severity == 'high' else 2.0
        device.base_power *= multiplier
        anomaly_events.append({
            'device_id': device_id,
            'timestamp': timestamp.isoformat(),
            'type': 'simulated_spike',
            'severity': severity,
            'multiplier': multiplier
        })
    
    return jsonify({
        'message': f'Simulated {anomaly_type} anomaly for {device_id}',
        'device_id': device_id,
        'timestamp': timestamp.isoformat()
    })

@app.route('/data/export', methods=['GET'])
def export_data():
    """Export all data for a time range (for Fivetran connector)"""
    start_time = request.args.get('start')
    end_time = request.args.get('end')
    
    if not start_time:
        start_time = (datetime.now() - timedelta(days=7)).isoformat()
    if not end_time:
        end_time = datetime.now().isoformat()
    
    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    
    all_readings = []
    for device_id, device in devices.items():
        current_time = start_dt
        while current_time <= end_dt:
            reading = device.generate_reading(current_time)
            all_readings.append(reading)
            current_time += timedelta(minutes=5)
    
    return jsonify({
        'export_timestamp': datetime.now().isoformat(),
        'start_time': start_dt.isoformat(),
        'end_time': end_dt.isoformat(),
        'total_records': len(all_readings),
        'data': all_readings
    })

if __name__ == '__main__':
    print("🔌 Starting Mock Device API...")
    print("📊 Available devices:", list(devices.keys()))
    print("🌐 API running on http://localhost:5000")
    print("📖 API Documentation:")
    print("  GET  /devices - List all devices")
    print("  GET  /readings?device_id=X&start=Y&end=Z - Get readings")
    print("  GET  /readings/latest - Get latest readings")
    print("  GET  /anomalies - Get detected anomalies")
    print("  POST /simulate/anomaly - Simulate anomaly")
    print("  GET  /data/export - Export all data")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
