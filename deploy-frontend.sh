#!/bin/bash

# EcoGridIQ Frontend Deployment Script
set -e

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"ecogrid-iq"}
BUCKET_NAME="$PROJECT_ID-ecogrid-frontend"
BACKEND_URL=${BACKEND_URL:-"https://ecogrid-backend-uc.a.run.app"}

echo "🌐 Deploying EcoGridIQ Frontend..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install it first."
    exit 1
fi

# Check if node is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install it first."
    exit 1
fi

# Set project
echo "📋 Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable storage.googleapis.com

# Create storage bucket if it doesn't exist
echo "🪣 Creating storage bucket..."
if ! gsutil ls gs://$BUCKET_NAME > /dev/null 2>&1; then
    gsutil mb gs://$BUCKET_NAME
    echo "✅ Bucket created: gs://$BUCKET_NAME"
else
    echo "✅ Bucket already exists: gs://$BUCKET_NAME"
fi

# Configure bucket for web hosting
echo "🌐 Configuring bucket for web hosting..."
gsutil web set -m index.html -e 404.html gs://$BUCKET_NAME

# Install dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm ci

# Build frontend
echo "🔨 Building frontend..."
NEXT_PUBLIC_API_URL=$BACKEND_URL npm run build

# Upload to Cloud Storage
echo "📤 Uploading to Cloud Storage..."
gsutil -m cp -r out/* gs://$BUCKET_NAME/

# Set public access
echo "🔓 Setting public access..."
gsutil iam ch allUsers:objectViewer gs://$BUCKET_NAME

# Get the website URL
WEBSITE_URL="https://storage.googleapis.com/$BUCKET_NAME"

echo "✅ Frontend deployed successfully!"
echo "🌐 Website URL: $WEBSITE_URL"
echo "🔗 Backend API: $BACKEND_URL"

# Test the deployment
echo "🧪 Testing deployment..."
if curl -f "$WEBSITE_URL" > /dev/null 2>&1; then
    echo "✅ Website is accessible!"
else
    echo "⚠️  Website test failed. Check the bucket configuration."
fi

echo ""
echo "🎉 Frontend deployment complete!"
echo ""
echo "📋 Deployment Summary:"
echo "  Frontend URL: $WEBSITE_URL"
echo "  Backend URL: $BACKEND_URL"
echo "  Storage Bucket: gs://$BUCKET_NAME"
echo ""
echo "Next steps:"
echo "1. Start mock device API: cd connector && python mock_device_api.py"
echo "2. Test the full application"
echo "3. Set up monitoring and alerts"
