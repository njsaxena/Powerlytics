"""
EcoGridIQ Fivetran Custom Connector
Extracts energy readings from IoT devices and sends to Fivetran pipeline
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EcoGridConnector:
    """
    Fivetran Custom Connector for EcoGridIQ energy data
    """
    
    def __init__(self):
        self.api_base_url = None
        self.api_key = None
        self.session = requests.Session()
    
    def spec(self) -> Dict[str, Any]:
        """
        Return connector specification for Fivetran
        """
        return {
            "documentation_url": "https://github.com/ecogrid-iq/connector",
            "supported_destination_sync_modes": ["append"],
            "connection_specification": {
                "type": "object",
                "properties": {
                    "api_base_url": {
                        "type": "string",
                        "title": "API Base URL",
                        "description": "Base URL for the energy device API",
                        "default": "http://localhost:5000"
                    },
                    "api_key": {
                        "type": "string",
                        "title": "API Key",
                        "description": "Optional API key for authentication",
                        "airbyte_secret": True
                    },
                    "sync_frequency": {
                        "type": "string",
                        "title": "Sync Frequency",
                        "description": "How often to sync data",
                        "enum": ["5min", "15min", "1hour", "6hour", "1day"],
                        "default": "15min"
                    }
                },
                "required": ["api_base_url"]
            }
        }
    
    def check(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test connection to the energy device API
        """
        try:
            self.api_base_url = config['api_base_url']
            self.api_key = config.get('api_key', '')
            
            # Test connection with health check
            headers = {}
            if self.api_key:
                headers['x-api-key'] = self.api_key
            
            response = self.session.get(
                f"{self.api_base_url}/health",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("✅ Connection test successful")
                return {"status": "SUCCESS", "message": "Connection established"}
            else:
                logger.error(f"❌ Connection test failed: {response.status_code}")
                return {"status": "FAILED", "message": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Connection test error: {str(e)}")
            return {"status": "FAILED", "message": str(e)}
    
    def discover(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Discover available data streams and their schemas
        """
        return {
            "streams": [
                {
                    "name": "readings",
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "device_id": {
                                "type": "string",
                                "description": "Unique device identifier"
                            },
                            "timestamp": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Reading timestamp in ISO format"
                            },
                            "power_w": {
                                "type": "number",
                                "description": "Instantaneous power consumption in watts"
                            },
                            "energy_wh": {
                                "type": "number",
                                "description": "Cumulative energy consumption in watt-hours"
                            },
                            "voltage": {
                                "type": "number",
                                "description": "Voltage reading in volts"
                            },
                            "occupancy": {
                                "type": "boolean",
                                "description": "Occupancy status"
                            },
                            "temp_c": {
                                "type": "number",
                                "description": "Temperature in Celsius"
                            },
                            "source": {
                                "type": "string",
                                "description": "Data source identifier"
                            },
                            "ingest_ts": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Data ingestion timestamp"
                            }
                        },
                        "required": ["device_id", "timestamp", "power_w", "energy_wh"]
                    },
                    "supported_sync_modes": ["incremental"],
                    "source_defined_cursor": True,
                    "default_cursor_field": ["timestamp"]
                },
                {
                    "name": "anomalies",
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "device_id": {
                                "type": "string",
                                "description": "Device identifier"
                            },
                            "timestamp": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Anomaly detection timestamp"
                            },
                            "type": {
                                "type": "string",
                                "description": "Type of anomaly detected"
                            },
                            "severity": {
                                "type": "string",
                                "description": "Anomaly severity level"
                            },
                            "original_power": {
                                "type": "number",
                                "description": "Original power reading before anomaly"
                            },
                            "anomaly_power": {
                                "type": "number",
                                "description": "Anomalous power reading"
                            }
                        },
                        "required": ["device_id", "timestamp", "type", "severity"]
                    },
                    "supported_sync_modes": ["incremental"],
                    "source_defined_cursor": True,
                    "default_cursor_field": ["timestamp"]
                }
            ]
        }
    
    def read(self, config: Dict[str, Any], stream_name: str, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Read data from the specified stream
        """
        try:
            self.api_base_url = config['api_base_url']
            self.api_key = config.get('api_key', '')
            
            headers = {}
            if self.api_key:
                headers['x-api-key'] = self.api_key
            
            if stream_name == "readings":
                return self._read_readings(headers, state)
            elif stream_name == "anomalies":
                return self._read_anomalies(headers, state)
            else:
                logger.error(f"Unknown stream: {stream_name}")
                return []
                
        except Exception as e:
            logger.error(f"Error reading stream {stream_name}: {str(e)}")
            return []
    
    def _read_readings(self, headers: Dict[str, str], state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Read energy readings with incremental sync
        """
        # Get last sync timestamp
        last_sync = state.get("readings", {}).get("last_sync")
        if not last_sync:
            # First sync - get last 24 hours
            start_time = (datetime.now() - timedelta(hours=24)).isoformat()
        else:
            start_time = last_sync
        
        end_time = datetime.now().isoformat()
        
        # Fetch data from API
        response = self.session.get(
            f"{self.api_base_url}/readings",
            params={
                'start': start_time,
                'end': end_time,
                'limit': 10000  # Adjust based on API limits
            },
            headers=headers,
            timeout=60
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch readings: {response.status_code}")
            return []
        
        data = response.json()
        readings = data.get('data', [])
        
        logger.info(f"Fetched {len(readings)} readings from {start_time} to {end_time}")
        
        # Update state
        if readings:
            latest_timestamp = max(reading['timestamp'] for reading in readings)
            state["readings"] = {"last_sync": latest_timestamp}
        
        return readings
    
    def _read_anomalies(self, headers: Dict[str, str], state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Read anomaly detections with incremental sync
        """
        # Get last sync timestamp
        last_sync = state.get("anomalies", {}).get("last_sync")
        if not last_sync:
            # First sync - get last 7 days
            start_time = (datetime.now() - timedelta(days=7)).isoformat()
        else:
            start_time = last_sync
        
        # Fetch anomalies from API
        response = self.session.get(
            f"{self.api_base_url}/anomalies",
            params={'since': start_time},
            headers=headers,
            timeout=60
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch anomalies: {response.status_code}")
            return []
        
        data = response.json()
        anomalies = data.get('anomalies', [])
        
        logger.info(f"Fetched {len(anomalies)} anomalies since {start_time}")
        
        # Update state
        if anomalies:
            latest_timestamp = max(anomaly['timestamp'] for anomaly in anomalies)
            state["anomalies"] = {"last_sync": latest_timestamp}
        
        return anomalies

# Fivetran connector entry point
def main():
    """
    Main entry point for Fivetran connector
    """
    import sys
    import json
    
    if len(sys.argv) != 2:
        print("Usage: python connector.py <command>")
        sys.exit(1)
    
    command = sys.argv[1]
    connector = EcoGridConnector()
    
    try:
        if command == "spec":
            result = connector.spec()
        elif command == "check":
            config = json.loads(sys.stdin.read())
            result = connector.check(config)
        elif command == "discover":
            config = json.loads(sys.stdin.read())
            result = connector.discover(config)
        elif command == "read":
            # Read config and state from stdin
            input_data = json.loads(sys.stdin.read())
            config = input_data['config']
            stream_name = input_data['stream_name']
            state = input_data.get('state', {})
            
            records = connector.read(config, stream_name, state)
            result = {
                'records': records,
                'state': state
            }
        else:
            result = {"error": f"Unknown command: {command}"}
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        error_result = {"error": str(e)}
        print(json.dumps(error_result, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
