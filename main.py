"""
EcoGridIQ Backend API
Cloud Run service for serving predictions, anomalies, and chat functionality
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import our custom modules
from bigquery_client import BigQueryClient
from vertex_client import VertexAIClient
from anomaly_detector import AnomalyDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="EcoGridIQ API",
    description="AI-powered energy analytics and recommendations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global clients
bigquery_client = None
vertex_client = None
anomaly_detector = None

# Pydantic models
class PredictionRequest(BaseModel):
    device_id: str
    horizon_hours: int = 24
    include_confidence: bool = True

class PredictionResponse(BaseModel):
    device_id: str
    predictions: List[Dict[str, Any]]
    model_version: str
    generated_at: str

class AnomalyRequest(BaseModel):
    device_id: Optional[str] = None
    since: Optional[str] = None
    severity: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    device_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    confidence: float
    sources: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]

# Dependency to get BigQuery client
def get_bigquery_client():
    global bigquery_client
    if bigquery_client is None:
        bigquery_client = BigQueryClient()
    return bigquery_client

# Dependency to get Vertex AI client
def get_vertex_client():
    global vertex_client
    if vertex_client is None:
        vertex_client = VertexAIClient()
    return vertex_client

# Dependency to get anomaly detector
def get_anomaly_detector():
    global anomaly_detector
    if anomaly_detector is None:
        anomaly_detector = AnomalyDetector()
    return anomaly_detector

@app.on_event("startup")
async def startup_event():
    """Initialize clients on startup"""
    logger.info("🚀 Starting EcoGridIQ API...")
    
    # Initialize clients
    global bigquery_client, vertex_client, anomaly_detector
    bigquery_client = BigQueryClient()
    vertex_client = VertexAIClient()
    anomaly_detector = AnomalyDetector()
    
    logger.info("✅ All clients initialized successfully")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "EcoGridIQ API",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "devices": "/devices",
            "predict": "/predict",
            "anomalies": "/anomalies",
            "chat": "/chat",
            "dashboard": "/dashboard"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test BigQuery connection
        bq_client = get_bigquery_client()
        bq_status = bq_client.test_connection()
        
        # Test Vertex AI connection
        vertex_client = get_vertex_client()
        vertex_status = vertex_client.test_connection()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "bigquery": bq_status,
                "vertex_ai": vertex_status
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/devices")
async def get_devices(bq_client: BigQueryClient = Depends(get_bigquery_client)):
    """Get list of devices with current status"""
    try:
        devices = await bq_client.get_devices()
        return {"devices": devices}
    except Exception as e:
        logger.error(f"Failed to get devices: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/devices/{device_id}/current")
async def get_current_usage(
    device_id: str,
    bq_client: BigQueryClient = Depends(get_bigquery_client)
):
    """Get current usage for a specific device"""
    try:
        usage = await bq_client.get_current_usage(device_id)
        if not usage:
            raise HTTPException(status_code=404, detail="Device not found")
        return usage
    except Exception as e:
        logger.error(f"Failed to get current usage for {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/devices/{device_id}/history")
async def get_usage_history(
    device_id: str,
    hours: int = Query(24, ge=1, le=168),  # 1 hour to 1 week
    bq_client: BigQueryClient = Depends(get_bigquery_client)
):
    """Get usage history for a specific device"""
    try:
        history = await bq_client.get_usage_history(device_id, hours)
        return {
            "device_id": device_id,
            "hours": hours,
            "data_points": len(history),
            "data": history
        }
    except Exception as e:
        logger.error(f"Failed to get history for {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict", response_model=PredictionResponse)
async def predict_consumption(
    request: PredictionRequest,
    bq_client: BigQueryClient = Depends(get_bigquery_client),
    vertex_client: VertexAIClient = Depends(get_vertex_client)
):
    """Get energy consumption predictions"""
    try:
        # Get historical data for the device
        historical_data = await bq_client.get_usage_history(
            request.device_id, 
            hours=168  # Last week
        )
        
        if not historical_data:
            raise HTTPException(status_code=404, detail="No historical data found for device")
        
        # Generate predictions using Vertex AI
        predictions = await vertex_client.predict_consumption(
            device_id=request.device_id,
            historical_data=historical_data,
            horizon_hours=request.horizon_hours,
            include_confidence=request.include_confidence
        )
        
        return PredictionResponse(
            device_id=request.device_id,
            predictions=predictions,
            model_version="1.0.0",
            generated_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Prediction failed for {request.device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/anomalies")
async def get_anomalies(
    device_id: Optional[str] = Query(None),
    since: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    bq_client: BigQueryClient = Depends(get_bigquery_client),
    anomaly_detector: AnomalyDetector = Depends(get_anomaly_detector)
):
    """Get detected anomalies"""
    try:
        # Parse since parameter
        since_dt = None
        if since:
            since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
        else:
            since_dt = datetime.now() - timedelta(hours=24)
        
        # Get anomalies from BigQuery
        anomalies = await bq_client.get_anomalies(
            device_id=device_id,
            since=since_dt,
            severity=severity
        )
        
        # Run real-time anomaly detection if no device_id specified
        if not device_id:
            realtime_anomalies = await anomaly_detector.detect_realtime_anomalies()
            anomalies.extend(realtime_anomalies)
        
        return {
            "anomalies": anomalies,
            "count": len(anomalies),
            "since": since_dt.isoformat(),
            "device_id": device_id
        }
        
    except Exception as e:
        logger.error(f"Failed to get anomalies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    request: ChatRequest,
    bq_client: BigQueryClient = Depends(get_bigquery_client),
    vertex_client: VertexAIClient = Depends(get_vertex_client)
):
    """Chat with the AI energy assistant"""
    try:
        # Get relevant context from BigQuery
        context_data = await bq_client.get_chat_context(
            device_id=request.device_id,
            query=request.message
        )
        
        # Generate response using Vertex AI
        response = await vertex_client.generate_chat_response(
            message=request.message,
            context=context_data,
            device_id=request.device_id
        )
        
        return ChatResponse(
            response=response["response"],
            confidence=response["confidence"],
            sources=response["sources"],
            recommendations=response["recommendations"]
        )
        
    except Exception as e:
        logger.error(f"Chat failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard")
async def get_dashboard_data(
    bq_client: BigQueryClient = Depends(get_bigquery_client)
):
    """Get dashboard summary data"""
    try:
        # Get overview data
        devices = await bq_client.get_devices()
        total_energy = await bq_client.get_total_energy_today()
        anomalies = await bq_client.get_anomalies(since=datetime.now() - timedelta(hours=24))
        
        # Get recent trends
        trends = await bq_client.get_usage_trends(hours=24)
        
        return {
            "summary": {
                "total_devices": len(devices),
                "total_energy_wh": total_energy,
                "anomalies_count": len(anomalies),
                "last_updated": datetime.now().isoformat()
            },
            "devices": devices,
            "trends": trends,
            "recent_anomalies": anomalies[:5]  # Last 5 anomalies
        }
        
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommendations/{device_id}")
async def get_recommendations(
    device_id: str,
    bq_client: BigQueryClient = Depends(get_bigquery_client),
    vertex_client: VertexAIClient = Depends(get_vertex_client)
):
    """Get AI-generated recommendations for a device"""
    try:
        # Get device data and patterns
        device_data = await bq_client.get_device_analysis(device_id)
        
        # Generate recommendations using Vertex AI
        recommendations = await vertex_client.generate_recommendations(
            device_id=device_id,
            device_data=device_data
        )
        
        return {
            "device_id": device_id,
            "recommendations": recommendations,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get recommendations for {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
