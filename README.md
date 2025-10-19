# Powerlytics - AI-Powered Energy Analytics Platform

## 🏠 Overview

Powerlytics helps homeowners and building managers reduce energy costs by learning usage patterns and providing AI-driven recommendations. The platform ingests IoT/smart meter data, performs forecasting and anomaly detection using Vertex AI, and provides a conversational assistant for actionable insights.

## 🏗️ Architecture

```
IoT Devices → Fivetran Connector → BigQuery → Vertex AI → Cloud Run → Next.js Dashboard
     ↓              ↓                ↓         ↓          ↓           ↓
Mock API      Custom Python      Data Lake   ML Models   Backend API  Frontend
```

## 🚀 Features

- **Data Ingestion**: Custom Fivetran connector for IoT energy readings
- **Time Series Analytics**: BigQuery-based data warehouse with feature engineering
- **AI Forecasting**: Vertex AI models for short-term consumption prediction
- **Anomaly Detection**: Statistical and ML-based anomaly flagging
- **Conversational Assistant**: RAG-powered chat interface for energy insights
- **Interactive Dashboard**: Real-time charts and recommendations

## 📁 Project Structure

```
/ecogrid-iq
├── /connector          # Fivetran custom connector
├── /backend           # Cloud Run API service
├── /frontend          # Next.js dashboard
├── /infrastructure    # Deployment configs
├── /notebooks         # Data analysis notebooks
└── /demo_assets       # Sample data and demo materials
```

## 🛠️ Quick Start

### Prerequisites

- Google Cloud Project with APIs enabled
- Python 3.9+
- Node.js 18+
- Docker (for containerization)

### Local Development

1. **Mock Device API**:
   ```bash
   cd connector
   pip install -r requirements.txt
   python mock_device_api.py
   ```

2. **Backend API**:
   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```

3. **Frontend Dashboard**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Google Cloud Deployment

1. **Enable APIs**:
   ```bash
   gcloud services enable bigquery.googleapis.com
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable run.googleapis.com
   ```

2. **Deploy Backend**:
   ```bash
   cd infrastructure
   ./deploy-backend.sh
   ```

3. **Deploy Frontend**:
   ```bash
   cd frontend
   npm run build
   npm run deploy
   ```

## 📊 Data Schema

### Raw Readings Table
```sql
CREATE TABLE `project.dataset.raw_readings` (
  device_id STRING,
  timestamp TIMESTAMP,
  power_w FLOAT64,
  energy_wh FLOAT64,
  voltage FLOAT64,
  occupancy BOOL,
  temp_c FLOAT64,
  source STRING,
  ingest_ts TIMESTAMP
)
PARTITION BY DATE(timestamp)
CLUSTER BY device_id
```

## 🤖 AI Models

- **Forecasting**: LSTM-based time series prediction for next 24-48 hours
- **Anomaly Detection**: Statistical z-score and ML-based reconstruction error
- **RAG Assistant**: Gemini-powered conversational interface with BigQuery context

## 📈 Demo Script (3 minutes)

1. **0:00-0:20**: Elevator pitch and platform overview
2. **0:20-0:45**: Dashboard showing current usage and predictions
3. **0:45-1:30**: Anomaly detection and evidence visualization
4. **1:30-2:10**: Chat assistant with actionable recommendations
5. **2:10-2:40**: Architecture overview
6. **2:40-3:00**: Metrics and next steps

## 🔧 Configuration

### Environment Variables

```bash
# Backend
GOOGLE_CLOUD_PROJECT=your-project-id
BIGQUERY_DATASET=ecogrid_dwh
VERTEX_AI_LOCATION=us-central1

# Frontend
NEXT_PUBLIC_API_URL=https://your-backend.run.app
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## 📞 Support

For questions or issues, please open a GitHub issue or contact the team.
