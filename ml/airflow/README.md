# Apache Airflow - ML Pipeline

This directory contains the Apache Airflow setup for orchestrating EduMind's ML training pipelines.

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- At least 4GB RAM allocated to Docker

### Start Airflow

```bash
cd ml/airflow

# Set the Airflow user ID (important for permissions)
echo -e "AIRFLOW_UID=$(id -u)" > .env

# Start the services
docker-compose up -d

# Wait for initialization (about 1-2 minutes)
docker-compose logs -f airflow-init

# Check status
docker-compose ps
```

### Access Airflow UI
- **URL**: http://localhost:8080
- **Username**: airflow
- **Password**: airflow

## DAGs Available

### 1. `xai_predictor_training_pipeline`
Complete ML pipeline for the Academic Risk Predictor:

```
start → etl_process → train_model → validate_model → deploy_model → end
                                          ↓
                                  validation_failed
```

**Tasks:**
| Task | Description |
|------|-------------|
| `etl_process` | Process OULAD data and create features |
| `train_model` | Train XGBoost classifier |
| `validate_model` | Check model accuracy threshold |
| `deploy_model` | Copy model to backend service |

**Schedule**: Weekly (can be triggered manually)

## Project Structure

```
ml/airflow/
├── dags/
│   └── xai_predictor_pipeline.py   # Main training DAG
├── plugins/                         # Custom operators (future)
├── logs/                            # Airflow logs (auto-generated)
├── docker-compose.yml               # Airflow services
└── README.md                        # This file
```

## Common Commands

```bash
# Start Airflow
docker-compose up -d

# Stop Airflow
docker-compose down

# View logs
docker-compose logs -f airflow-scheduler
docker-compose logs -f airflow-webserver

# Trigger a DAG manually via CLI
docker-compose exec airflow-cli airflow dags trigger xai_predictor_training_pipeline

# List DAGs
docker-compose exec airflow-cli airflow dags list

# Test a specific task
docker-compose exec airflow-cli airflow tasks test xai_predictor_training_pipeline train_model 2024-01-01
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AIRFLOW_UID` | 50000 | User ID for Airflow processes |
| `_AIRFLOW_WWW_USER_USERNAME` | airflow | Web UI username |
| `_AIRFLOW_WWW_USER_PASSWORD` | airflow | Web UI password |

### Model Configuration

Edit `dags/xai_predictor_pipeline.py` to modify:
- `MIN_ACCURACY_THRESHOLD`: Minimum accuracy for deployment (default: 0.80)
- Model hyperparameters in the training function

## Monitoring

### Health Checks
- Webserver: http://localhost:8080/health
- Scheduler: Check via `docker-compose ps`

### Logs
Logs are stored in `./logs/` directory:
- `scheduler/` - Scheduler logs
- `dag_id/task_id/` - Individual task logs

## Troubleshooting

### DAG not appearing
```bash
# Check for import errors
docker-compose exec airflow-cli airflow dags list-import-errors
```

### Permission issues
```bash
# Reset permissions
sudo chown -R $(id -u):$(id -g) logs/ dags/ plugins/
```

### Database issues
```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

## Integration with CI/CD

The Airflow DAGs complement the GitHub Actions workflow:

```
GitHub Actions (CI)          Airflow (Scheduled Training)
        ↓                              ↓
 On code push               Weekly/On-demand
        ↓                              ↓
 Run tests                   ETL → Train → Validate
        ↓                              ↓
 Build artifacts             Deploy to service
```

## Next Steps

1. **Add more DAGs**:
   - `engagement_predictor_pipeline.py`
   - `learning_style_pipeline.py`

2. **Add monitoring**:
   - Integrate with Prometheus/Grafana
   - Set up email alerts for failures

3. **Production deployment**:
   - Use Kubernetes executor
   - Set up proper secrets management
   - Configure remote logging (S3/GCS)
