#!/bin/bash

# Powerlytics BigQuery Setup Script
set -e

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"powerlytics"}
DATASET_ID="powerlytics_dwh"

echo "🗄️  Setting up BigQuery dataset and tables..."

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install it first."
    exit 1
fi

# Check if bq is installed
if ! command -v bq &> /dev/null; then
    echo "❌ bq CLI not found. Please install it first."
    exit 1
fi

# Set project
echo "📋 Setting project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Enable BigQuery API
echo "🔧 Enabling BigQuery API..."
gcloud services enable bigquery.googleapis.com

# Create dataset
echo "📊 Creating BigQuery dataset..."
bq mk --dataset \
    --description "Powerlytics Energy Analytics Data Warehouse" \
    --location US \
    $PROJECT_ID:$DATASET_ID

# Replace project ID placeholder in SQL files
echo "📝 Preparing SQL scripts..."
sed "s/{project_id}/$PROJECT_ID/g" ./infrastructure/bigquery_schema.sql > /tmp/schema.sql
sed "s/{project_id}/$PROJECT_ID/g" ./infrastructure/feature_engineering.sql > /tmp/features.sql

# Run schema creation
echo "🏗️  Creating tables..."
bq query --use_legacy_sql=false < /tmp/schema.sql

# Run feature engineering
echo "⚙️  Setting up feature engineering..."
bq query --use_legacy_sql=false < /tmp/features.sql

# Verify tables were created
echo "✅ Verifying table creation..."
TABLES=$(bq ls $PROJECT_ID:$DATASET_ID | grep -v "tableId" | wc -l)
echo "📊 Created $TABLES tables in dataset $DATASET_ID"

# List tables
echo "📋 Tables created:"
bq ls $PROJECT_ID:$DATASET_ID

echo ""
echo "🎉 BigQuery setup complete!"
echo "Dataset: $PROJECT_ID:$DATASET_ID"
echo ""
echo "Next steps:"
echo "1. Deploy backend: ./deploy-backend.sh"
echo "2. Start mock device API: cd connector && python mock_device_api.py"
echo "3. Deploy frontend: ./deploy-frontend.sh"
