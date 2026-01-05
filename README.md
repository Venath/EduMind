## System Architecture

![EduMind GCP Cloud Native Architecture](Docs/edumind_gcp_architecture.png)

### Tech Stack

| Component/Layer | Technology | Justification/Role | Alternatives Considered |
|-----------------|------------|-------------------|------------------------|
| **Cloud Provider** | Google Cloud Platform (GCP) | Superior managed AI/ML services (Vertex AI), mature Kubernetes engine (GKE), cost-effective pricing for research workloads | AWS, Microsoft Azure |
| **Container Orchestration** | Google Kubernetes Engine (GKE) | Most mature and automated managed Kubernetes service, robust scalable foundation for MLOps lifecycle | AWS EKS, Azure AKS |
| **Containerization** | Docker | Industry-standard containerization for microservices, ensures consistency across dev/prod environments | Podman, containerd |
| **Ingress/Gateway** | Nginx | High-performance API gateway and load balancer, handles SSL termination and routing | Traefik, Kong, Istio |
| **CI/CD Orchestration** | GitHub Actions | Source control integration, workflow triggering, seamless GitHub ecosystem integration | GitLab CI, Jenkins, AWS CodePipeline |
| **Data Version Control** | DVC | Versioning datasets alongside code in Git, reproducible ML experiments | Git LFS, Pachyderm |
| **ML Pipeline Orchestration** | Apache Airflow | Orchestrating complex, containerized ML tasks, DAG-based workflow management | Kubeflow, Prefect, Luigi |
| **Model & Artifact Storage** | Google Cloud Storage (GCS) | Scalable, secure storage of datasets and model artifacts (.joblib) | Amazon S3, Azure Blob Storage |
| **Container Registry** | Docker Registry (GCR) | Centralized container image storage and versioning | Docker Hub, ECR, ACR |
| **System Observability - Logs** | Loki | Log aggregation optimized for Kubernetes, Grafana-native | ELK Stack, Splunk |
| **System Observability - Metrics** | Mimir (Prometheus) | Scalable metrics storage, PromQL compatible | InfluxDB, Datadog |
| **System Observability - Traces** | Tempo | Distributed tracing, Grafana-native integration | Jaeger, Zipkin |
| **System Observability - Dashboards** | Grafana | Unified visualization for logs, metrics, and traces | Kibana, Datadog |
| **Relational Database** | PostgreSQL | High data integrity (ACID compliance), complex queries, robust feature set for structured student data | MySQL, MariaDB |
| **Time-Series Database** | TimescaleDB | PostgreSQL extension for time-series data, high-performance engagement log ingestion, SQL joins with relational data | InfluxDB, Prometheus |
| **Backend API Framework** | FastAPI | Modern, high-performance, async Python framework for ML model-serving APIs, automatic validation & docs | Django REST, Flask |
| **Frontend Framework** | React | Industry-leading ecosystem, data visualization libraries (Recharts, Nivo), mature state management | Vue.js, Angular |
| **Frontend Language** | TypeScript | Type safety, better developer experience, reduced runtime errors | JavaScript |
| **Frontend Build Tool** | Vite | Fast HMR, modern ES modules, optimized production builds | Webpack, Parcel |
| **Core ML Library** | Scikit-learn | Robust, user-friendly for classification/regression on structured data, rapid model development | PyTorch, TensorFlow |
| **XAI Library - Global** | SHAP | Model-agnostic global and local explanations, Shapley values for feature importance | InterpretML |
| **XAI Library - Local** | LIME | Local interpretable model-agnostic explanations, instance-level predictions | Captum |
| **Model Format** | Joblib | Efficient serialization for scikit-learn models | Pickle, ONNX |

# EduMind

> AI-powered educational platform with explainable predictions for student academic risk.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)

---

## Overview

EduMind is a cloud-native educational analytics platform that leverages machine learning to predict student academic risk and provide explainable insights. The platform uses **SHAP** and **LIME** for model interpretability, enabling educators to understand *why* a student might be at risk and take proactive interventions.

### Key Features

- **Predictive Analytics** - ML-powered academic risk prediction
- **Explainable AI (XAI)** - SHAP & LIME for transparent predictions
- **Learning Style Recognition** - Personalized learning recommendations
- **Engagement Tracking** - Real-time student engagement monitoring
- **Interactive Dashboards** - React-based visualizations with Recharts & Nivo
- **Cloud-Native** - Kubernetes-orchestrated microservices on GCP

---

## Project Structure

```
/EduMind
├── /apps
│   └── /web                          # Frontend (React + TypeScript + Vite)
├── /backend
│   ├── /services                     # FastAPI Microservices
│   │   ├── /user-service             # Authentication & user profiles
│   │   ├── /course-service           # Course management
│   │   ├── /assessment-service       # Quizzes & assessments
│   │   ├── /service-engagement-tracker   # Student engagement logs
│   │   ├── /service-learning-style   # Learning style prediction
│   │   └── /service-xai-prediction   # XAI risk prediction engine
│   └── /shared                       # Shared backend utilities
├── /ml
│   ├── /airflow                      # Apache Airflow DAGs
│   ├── /models                       # Trained ML models
│   │   ├── /engagement_predictor
│   │   ├── /learning_style_recognizer
│   │   └── /xai_predictor
│   └── /pipelines                    # Training pipelines
├── /packages                         # Shared packages (monorepo)
│   ├── /backend-common               # Python shared utilities
│   ├── /tsconfig                     # TypeScript configurations
│   └── /utils                        # Shared JS/TS utilities
├── /platform
│   ├── /infrastructure               # GCP infrastructure configs
│   │   ├── /database
│   │   ├── /gcs
│   │   └── /gke
│   └── /kubernetes                   # K8s manifests
│       ├── /monitoring               # LGTM stack configs
│       └── /services                 # Service deployments
├── /data                             # Datasets (DVC tracked)
└── /docs                             # Documentation & diagrams
```

---

## Getting Started

### Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Node.js | 18+ | Frontend runtime |
| Python | 3.11+ | Backend & ML |
| Docker | Latest | Containerization |
| Docker Compose | Latest | Local orchestration |
| pnpm | 8+ | Package manager (recommended) |
| kubectl | Latest | Kubernetes CLI (for deployment) |

### Quick Start (Docker Compose)

```bash
# Clone the repository
git clone https://github.com/VoidEngineers/EduMind.git
cd EduMind

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Backend Setup (Development)

```bash
# Navigate to backend
cd backend

# Start all services with Docker
docker-compose up -d

# Or run individual service manually
cd services/service-xai-prediction
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

### Frontend Setup (Development)

```bash
# Navigate to frontend
cd apps/web

# Install dependencies
pnpm install

# Start development server
pnpm dev

# Build for production
pnpm build
```

### ML Pipeline Setup

```bash
# Navigate to ML directory
cd ml

# Install dependencies
pip install -r requirements.txt

# Start Airflow (for ML pipelines)
cd airflow
docker-compose up -d

# Or train model manually
cd models/xai_predictor
python save_model.py
```

---

## Testing

### Backend Tests

```bash
# Run all backend tests
cd backend
pytest

# Run specific service tests
cd services/service-xai-prediction
pytest --cov=app --cov-report=html
```

### Frontend Tests

```bash
cd apps/web
pnpm test

# Run with coverage
pnpm test:coverage
```

### Integration Tests

```bash
# Ensure services are running
docker-compose up -d

# Run integration tests
pytest tests/integration/
```

---

## Microservices

| Service | Port | Description | Health Check |
|---------|------|-------------|--------------|
| `user-service` | 8001 | User authentication & profile management | `/health` |
| `course-service` | 8002 | Course CRUD operations | `/health` |
| `service-xai-prediction` | 8003 | XAI-powered academic risk prediction | `/health` |
| `assessment-service` | 8004 | Quizzes, tests & assessments | `/health` |
| `service-engagement-tracker` | 8005 | Real-time engagement tracking | `/health` |
| `service-learning-style` | 8006 | Learning style recognition (VARK) | `/health` |

### API Documentation

Each service exposes Swagger/OpenAPI documentation:
- User Service: `http://localhost:8001/docs`
- Course Service: `http://localhost:8002/docs`
- XAI Prediction: `http://localhost:8003/docs`
- Assessment Service: `http://localhost:8004/docs`
- Engagement Tracker: `http://localhost:8005/docs`
- Learning Style: `http://localhost:8006/docs`

---

## ML Models

### 1. Academic Risk Predictor (XAI Engine)
- **Algorithm**: XGBoost / Random Forest
- **Dataset**: OULAD (Open University Learning Analytics Dataset)
- **Output**: Pass/Fail probability with risk factors
- **Explainability**: SHAP (global) + LIME (local)

### 2. Engagement Tracker
- **Algorithm**: Time-series analysis
- **Features**: Click patterns, session duration, activity frequency
- **Output**: Engagement score (0-100)

### 3. Learning Style Recognizer
- **Algorithm**: Classification model
- **Framework**: VARK (Visual, Auditory, Read/Write, Kinesthetic)
- **Output**: Learning style profile with recommendations

---

## Observability (LGTM Stack)

| Component | Purpose | Access |
|-----------|---------|--------|
| **Grafana** | Dashboards & visualization | `http://localhost:3000` |
| **Loki** | Log aggregation | Via Grafana |
| **Tempo** | Distributed tracing | Via Grafana |
| **Mimir** | Metrics (Prometheus) | Via Grafana |

---

## Team

**VoidEngineers** - 4 Members

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.
