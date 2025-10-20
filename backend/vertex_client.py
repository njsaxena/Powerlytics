"""
Vertex AI Client for Powerlytics
Handles ML model predictions and chat functionality
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

try:
    from google.cloud import aiplatform
    from google.cloud.aiplatform.gapic.schema import predict
    from vertexai.preview.language_models import TextGenerationModel
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    logging.warning("Vertex AI libraries not available. Using mock responses.")

logger = logging.getLogger(__name__)

class VertexAIClient:
    """Client for Vertex AI operations"""
    
    def __init__(self):
    self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "powerlytics")
        self.location = os.getenv("VERTEX_AI_LOCATION", "us-central1")
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        if VERTEX_AI_AVAILABLE:
            try:
                aiplatform.init(project=self.project_id, location=self.location)
                self.text_model = TextGenerationModel.from_pretrained("text-bison@001")
                self.forecast_endpoint = None  # Will be set when model is deployed
                self.anomaly_endpoint = None
            except Exception as e:
                logger.error(f"Failed to initialize Vertex AI: {str(e)}")
                self.text_model = None
        else:
            self.text_model = None
    
    async def _run_async(self, func, *args, **kwargs):
        """Run a function asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args, **kwargs)
    
    def test_connection(self) -> bool:
        """Test Vertex AI connection"""
        if not VERTEX_AI_AVAILABLE or not self.text_model:
            return False
        
        try:
            # Simple test query
            response = self.text_model.predict("Test connection")
            return response is not None
        except Exception as e:
            logger.error(f"Vertex AI connection test failed: {str(e)}")
            return False
    
    async def predict_consumption(
        self,
        device_id: str,
        historical_data: List[Dict[str, Any]],
        horizon_hours: int = 24,
        include_confidence: bool = True
    ) -> List[Dict[str, Any]]:
        """Predict energy consumption using ML model"""
        
        if not VERTEX_AI_AVAILABLE or not self.forecast_endpoint:
            # Fallback to simple statistical prediction
            return await self._statistical_prediction(
                device_id, historical_data, horizon_hours, include_confidence
            )
        
        try:
            # Prepare features for ML model
            features = self._prepare_forecast_features(historical_data)
            
            # Call Vertex AI endpoint
            predictions = await self._call_forecast_endpoint(features, horizon_hours)
            
            return predictions
            
        except Exception as e:
            logger.error(f"ML prediction failed for {device_id}: {str(e)}")
            # Fallback to statistical prediction
            return await self._statistical_prediction(
                device_id, historical_data, horizon_hours, include_confidence
            )
    
    async def _statistical_prediction(
        self,
        device_id: str,
        historical_data: List[Dict[str, Any]],
        horizon_hours: int,
        include_confidence: bool
    ) -> List[Dict[str, Any]]:
        """Fallback statistical prediction method"""
        
        if not historical_data:
            return []
        
        # Calculate baseline patterns
        hourly_patterns = {}
        for i in range(24):
            hourly_data = [d for d in historical_data if d['timestamp'].hour == i]
            if hourly_data:
                hourly_patterns[i] = sum(d['power_w'] for d in hourly_data) / len(hourly_data)
        
        # Generate predictions
        predictions = []
        current_time = datetime.now()
        
        for i in range(horizon_hours):
            prediction_time = current_time + timedelta(hours=i)
            hour = prediction_time.hour
            
            # Use hourly pattern if available, otherwise use overall average
            if hour in hourly_patterns:
                predicted_power = hourly_patterns[hour]
            else:
                predicted_power = sum(d['power_w'] for d in historical_data) / len(historical_data)
            
            # Add some randomness for realistic variation
            import random
            variation = random.uniform(0.8, 1.2)
            predicted_power *= variation
            
            prediction = {
                "timestamp": prediction_time.isoformat(),
                "predicted_power_w": round(predicted_power, 2),
                "method": "statistical"
            }
            
            if include_confidence:
                # Simple confidence based on data availability
                confidence = min(0.9, len(historical_data) / 100)
                prediction["confidence"] = round(confidence, 2)
                prediction["confidence_interval_lower"] = round(predicted_power * 0.8, 2)
                prediction["confidence_interval_upper"] = round(predicted_power * 1.2, 2)
            
            predictions.append(prediction)
        
        return predictions
    
    def _prepare_forecast_features(self, historical_data: List[Dict[str, Any]]) -> List[float]:
        """Prepare features for ML model"""
        if not historical_data:
            return []
        
        # Extract power values and create time-based features
        features = []
        for i, data_point in enumerate(historical_data[-24:]):  # Last 24 hours
            timestamp = data_point['timestamp']
            features.extend([
                data_point['power_w'],
                timestamp.hour,
                timestamp.day_of_week,
                timestamp.month,
                1 if timestamp.weekday() >= 5 else 0,  # Weekend
                data_point.get('temp_c', 20),
                1 if data_point.get('occupancy', False) else 0
            ])
        
        return features
    
    async def _call_forecast_endpoint(self, features: List[float], horizon_hours: int) -> List[Dict[str, Any]]:
        """Call Vertex AI forecast endpoint"""
        # This would be implemented when the ML model is deployed
        # For now, return empty list
        return []
    
    async def generate_chat_response(
        self,
        message: str,
        context: Dict[str, Any],
        device_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate chat response using Vertex AI"""
        
        if not VERTEX_AI_AVAILABLE or not self.text_model:
            return await self._mock_chat_response(message, context, device_id)
        
        try:
            # Prepare context for the LLM
            context_str = self._prepare_chat_context(context, device_id)
            
            # Create prompt
            prompt = f"""
You are an AI energy assistant for Powerlytics. Help users understand their energy consumption and provide actionable recommendations.

Context:
{context_str}

User Question: {message}

Please provide a helpful, accurate response based on the energy data. Include specific recommendations when possible.
"""
            
            # Generate response
            response = await self._run_async(
                self.text_model.predict,
                prompt,
                max_output_tokens=512,
                temperature=0.7
            )
            
            # Parse response and extract recommendations
            response_text = response.text if hasattr(response, 'text') else str(response)
            recommendations = self._extract_recommendations(response_text, context)
            
            return {
                "response": response_text,
                "confidence": 0.85,  # Placeholder confidence
                "sources": self._extract_sources(context),
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Chat generation failed: {str(e)}")
            return await self._mock_chat_response(message, context, device_id)
    
    async def _mock_chat_response(
        self,
        message: str,
        context: Dict[str, Any],
        device_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mock chat response when Vertex AI is not available"""
        
        # Simple keyword-based responses
        message_lower = message.lower()
        
        if "high" in message_lower and "usage" in message_lower:
            response = "I can see your energy usage has been elevated recently. Based on the data, this could be due to increased HVAC usage or additional appliances running. Consider checking your thermostat settings and unplugging unused devices."
            recommendations = [
                {
                    "type": "energy_saving",
                    "title": "Check Thermostat Settings",
                    "description": "Lower your thermostat by 2-3 degrees to reduce HVAC energy consumption",
                    "potential_savings": "$15-25/month"
                }
            ]
        elif "anomaly" in message_lower or "spike" in message_lower:
            response = "I detected an energy spike in your consumption. This could indicate a malfunctioning appliance or unusual usage pattern. I recommend checking your major appliances and monitoring for any unusual behavior."
            recommendations = [
                {
                    "type": "maintenance",
                    "title": "Check Major Appliances",
                    "description": "Inspect your refrigerator, HVAC system, and water heater for any issues",
                    "potential_savings": "$20-40/month"
                }
            ]
        elif "cost" in message_lower or "save" in message_lower:
            response = "Based on your current usage patterns, I can suggest several ways to reduce your energy costs. The biggest opportunities are optimizing your HVAC usage and shifting high-energy activities to off-peak hours."
            recommendations = [
                {
                    "type": "cost_optimization",
                    "title": "Shift High-Energy Activities",
                    "description": "Run dishwasher and laundry during off-peak hours (after 8 PM)",
                    "potential_savings": "$10-20/month"
                }
            ]
        else:
            response = "I can help you understand your energy consumption patterns and provide recommendations for optimization. What specific aspect of your energy usage would you like to know more about?"
            recommendations = []
        
        return {
            "response": response,
            "confidence": 0.75,
            "sources": self._extract_sources(context),
            "recommendations": recommendations
        }
    
    def _prepare_chat_context(self, context: Dict[str, Any], device_id: Optional[str]) -> str:
        """Prepare context string for chat"""
        context_parts = []
        
        # Add device information
        if device_id and context.get("device_info"):
            device_info = context["device_info"]
            context_parts.append(f"Device: {device_info.get('device_name', device_id)} ({device_info.get('device_type', 'unknown')})")
            context_parts.append(f"Current Power: {device_info.get('current_power', 'N/A')}W")
        
        # Add recent anomalies
        if context.get("recent_anomalies"):
            anomalies = context["recent_anomalies"][:3]  # Last 3 anomalies
            context_parts.append("Recent Anomalies:")
            for anomaly in anomalies:
                context_parts.append(f"- {anomaly.get('type', 'unknown')} at {anomaly.get('timestamp', 'unknown')}")
        
        # Add usage patterns
        if context.get("usage_patterns", {}).get("stats"):
            stats = context["usage_patterns"]["stats"]
            context_parts.append(f"Average Power: {stats.get('avg_power', 'N/A')}W")
            context_parts.append(f"Peak Power: {stats.get('max_power', 'N/A')}W")
        
        # Add cost information
        if context.get("cost_analysis"):
            cost = context["cost_analysis"]
            context_parts.append(f"Monthly Cost: ${cost.get('total_cost_usd', 'N/A')}")
            context_parts.append(f"Carbon Footprint: {cost.get('total_carbon_kg', 'N/A')} kg CO2")
        
        return "\n".join(context_parts) if context_parts else "No specific context available."
    
    def _extract_recommendations(self, response_text: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract recommendations from response text"""
        # This would parse the LLM response to extract structured recommendations
        # For now, return empty list
        return []
    
    def _extract_sources(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract source information from context"""
        sources = []
        
        if context.get("recent_anomalies"):
            sources.append({
                "type": "anomaly_data",
                "description": "Recent anomaly detection data",
                "timestamp": datetime.now().isoformat()
            })
        
        if context.get("usage_patterns"):
            sources.append({
                "type": "usage_analysis",
                "description": "Energy usage pattern analysis",
                "timestamp": datetime.now().isoformat()
            })
        
        return sources
    
    async def generate_recommendations(
        self,
        device_id: str,
        device_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered recommendations for a device"""
        
        recommendations = []
        
        # Analyze device data and generate recommendations
        if device_data.get("stats"):
            stats = device_data["stats"]
            avg_power = stats.get("avg_power", 0)
            max_power = stats.get("max_power", 0)
            
            # High usage recommendation
            if avg_power > 2000:  # High threshold
                recommendations.append({
                    "type": "energy_efficiency",
                    "priority": "high",
                    "title": "High Energy Consumption Detected",
                    "description": f"Your device is consuming {avg_power:.0f}W on average, which is above normal levels.",
                    "action": "Consider scheduling an energy audit or checking for malfunctioning components.",
                    "potential_savings": "$30-50/month"
                })
            
            # Peak usage recommendation
            if max_power > avg_power * 2:
                recommendations.append({
                    "type": "load_management",
                    "priority": "medium",
                    "title": "Peak Usage Optimization",
                    "description": "Your device shows significant peak usage patterns that could be optimized.",
                    "action": "Consider spreading high-energy activities throughout the day.",
                    "potential_savings": "$15-25/month"
                })
        
        # Add general recommendations
        recommendations.extend([
            {
                "type": "maintenance",
                "priority": "low",
                "title": "Regular Maintenance",
                "description": "Schedule regular maintenance to ensure optimal efficiency.",
                "action": "Clean filters, check connections, and update firmware if available.",
                "potential_savings": "$10-20/month"
            },
            {
                "type": "monitoring",
                "priority": "low",
                "title": "Enhanced Monitoring",
                "description": "Consider installing additional sensors for better visibility.",
                "action": "Add temperature and occupancy sensors to optimize usage patterns.",
                "potential_savings": "$5-15/month"
            }
        ])
        
        return recommendations
