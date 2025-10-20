#!/bin/bash

# Powerlytics Backend Deployment Script
set -e

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"powerlytics"}
REGION="us-central1"
SERVICE_NAME="powerlytics-backend"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 Deploying Powerlytics Backend to Cloud Run..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install it first."
    exit 1
fi

# Set project
echo "📋 Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com

# Build Docker image
echo "🐳 Building Docker image..."
docker build -t $IMAGE_NAME ./backend

# Push to Container Registry
echo "📤 Pushing image to Container Registry..."
docker push $IMAGE_NAME

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,BIGQUERY_DATASET=powerlytics_dwh,VERTEX_AI_LOCATION=$REGION"

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')

echo "✅ Backend deployed successfully!"
echo "🌐 Service URL: $SERVICE_URL"
echo "📊 Health check: $SERVICE_URL/health"

# Test the deployment
echo "🧪 Testing deployment..."
if curl -f "$SERVICE_URL/health" > /dev/null 2>&1; then
    echo "✅ Health check passed!"
else
    echo "⚠️  Health check failed. Check the logs:"
    echo "gcloud logs tail --service=$SERVICE_NAME --region=$REGION"
fi

echo ""
echo "🎉 Deployment complete!"
echo "Next steps:"
echo "1. Set up BigQuery dataset: ./setup-bigquery.sh"
echo "2. Deploy frontend: ./deploy-frontend.sh"
echo "3. Start mock device API: cd connector && python mock_device_api.py"
