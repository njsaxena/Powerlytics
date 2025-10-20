#!/bin/bash

# EcoGridIQ Setup Script
# This script helps you set up the complete EcoGridIQ platform

set -e

echo "🚀 EcoGridIQ Setup Script"
echo "========================="
echo ""

# Check if running on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
else
    echo "❌ Unsupported operating system: $OSTYPE"
    exit 1
fi

echo "📋 Detected OS: $OS"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "✅ Python 3: $PYTHON_VERSION"
else
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js: $NODE_VERSION"
else
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Check Docker
if command_exists docker; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    echo "✅ Docker: $DOCKER_VERSION"
else
    echo "❌ Docker not found. Please install Docker"
    exit 1
fi

# Check gcloud
if command_exists gcloud; then
    GCLOUD_VERSION=$(gcloud version --format="value(Google Cloud SDK)" | head -1)
    echo "✅ Google Cloud SDK: $GCLOUD_VERSION"
else
    echo "❌ Google Cloud SDK not found. Please install gcloud CLI"
    exit 1
fi

echo ""

# Set up Python virtual environment
echo "🐍 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip

# Backend dependencies
echo "  Installing backend dependencies..."
pip install -r backend/requirements.txt

# Connector dependencies
echo "  Installing connector dependencies..."
pip install -r connector/requirements.txt

echo "✅ Python dependencies installed"

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
cd ..
echo "✅ Node.js dependencies installed"

# Set up environment variables
echo "⚙️  Setting up environment variables..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# EcoGridIQ Environment Variables
GOOGLE_CLOUD_PROJECT=your-project-id
BIGQUERY_DATASET=ecogrid_dwh
VERTEX_AI_LOCATION=us-central1
NEXT_PUBLIC_API_URL=http://localhost:8080
EOF
    echo "✅ Environment file created (.env)"
    echo "⚠️  Please update .env with your Google Cloud project ID"
else
    echo "✅ Environment file already exists"
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x infrastructure/*.sh
chmod +x setup.sh
echo "✅ Scripts made executable"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p data
echo "✅ Directories created"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update .env with your Google Cloud project ID"
echo "2. Set up Google Cloud project:"
echo "   gcloud config set project YOUR_PROJECT_ID"
echo "3. Enable required APIs:"
echo "   ./infrastructure/setup-bigquery.sh"
echo "4. Start the mock device API:"
echo "   cd connector && python mock_device_api.py"
echo "5. Start the backend API:"
echo "   cd backend && python main.py"
echo "6. Start the frontend:"
echo "   cd frontend && npm run dev"
echo ""
echo "🌐 Once running, visit:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8080"
echo "  Mock Device API: http://localhost:5000"
echo ""
echo "📚 For more information, see README.md"
