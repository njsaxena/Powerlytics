# Powerlytics

Powerlytics is an AI-powered energy analytics platform that ingests IoT energy data, performs real-time anomaly detection, forecasting, and provides conversational AI recommendations.

This repository contains the full-stack demo: a Next.js frontend, FastAPI backend (Cloud Run), BigQuery data warehouse, Vertex AI integrations, and supporting infrastructure (Terraform + Cloud Build).

## What changed
- This project was previously branded as "EcoGridIQ". All internal references have been renamed to "Powerlytics" (project defaults, dataset IDs, buckets, service names, package names, and documentation). If you have external resources (Cloud Storage buckets, Cloud Run services, DNS, or GitHub repository names) that used the old names, update them accordingly.

## Quickstart (local)

Prerequisites:
- Python 3.10+ (backend & connector)
- Node.js 18+ (frontend)
- Google Cloud SDK + authenticated gcloud account (for BigQuery and deployments)
- bq CLI (for BigQuery)

1. Start the mock device API (simulates IoT devices):

```bash
cd connector
python mock_device_api.py
```

2. Run backend locally:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
UVICORN_LOG_LEVEL=info uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

3. Run frontend locally:

```bash
cd frontend
npm ci
NEXT_PUBLIC_API_URL=http://localhost:8080 npm run dev
```

## Deploy (high level)

The repository contains helper scripts and CI configuration to deploy to Google Cloud:

- `infrastructure/setup-bigquery.sh` — creates dataset and runs SQL schema scripts (updates `{project_id}` placeholders automatically).
- `infrastructure/deploy-backend.sh` — builds Docker image and deploys the backend to Cloud Run.
- `infrastructure/deploy-frontend.sh` — builds the Next.js app and uploads static export to a GCS bucket for hosting.
- `infrastructure/cloudbuild.yaml` — Cloud Build pipeline for CI/CD (builds backend, deploys Cloud Run, builds frontend, uploads to GCS, and runs BigQuery schema).
- `infrastructure/terraform/` — Terraform configuration for creating the BigQuery dataset, Cloud Storage bucket, Cloud Run service, and service account. Review and run with terraform init/plan/apply as usual.

Important: default project names and dataset IDs were updated to `powerlytics` / `powerlytics_dwh`. If you rely on previous names, update GCP resources accordingly.

## BigQuery
- Schema and sample data are in `infrastructure/bigquery_schema.sql` (uses `{project_id}` placeholder).
- Feature engineering SQL is in `infrastructure/feature_engineering.sql`.

To apply schema locally (with `bq`):

```bash
# replace PROJECT_ID
export PROJECT_ID=your-gcp-project-id
gcloud config set project $PROJECT_ID
sed "s/{project_id}/$PROJECT_ID/g" infrastructure/bigquery_schema.sql > /tmp/schema.sql
bq query --use_legacy_sql=false < /tmp/schema.sql
```

## Notes about the rename
- I updated strings, comments, dataset IDs, bucket names, Terraform resource names, and package names across the repository to use Powerlytics.
- External resources (GCS buckets, Cloud Run services, GitHub repo names, docker image tags) must be renamed manually in those external systems if you want them to match the new names.

## Next steps I can help with
- Run local builds and lints and fix any environment-specific issues.
- Create a git branch and commit all changes with a tidy commit message.
- Prepare a PR description and changelog for the rename.
- Update external cloud resources (I can provide exact commands to run locally).

If you'd like any of the next steps, tell me which one and I'll prepare precise commands or make the change here.
