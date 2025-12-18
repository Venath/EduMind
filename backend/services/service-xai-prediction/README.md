# XAI Prediction Service

Explainable AI microservice for predicting student academic outcomes with interpretable explanations.

## Overview

This service provides machine learning-based predictions for student academic outcomes (Pass, Fail, Distinction, Withdrawn) with transparent, explainable AI capabilities using SHAP (SHapley Additive exPlanations) values.

## Features

- **Student Outcome Prediction**: Predicts academic outcomes with probability scores
- **SHAP Explainability**: Provides SHAP values showing feature contributions
- **Feature Importance Analysis**: Identifies and ranks key factors influencing predictions
- **Risk Assessment**: Categorizes students by risk level (Low, Medium, High, Critical)
- **Natural Language Explanations**: Generates human-readable prediction explanations
- **RESTful API**: Fast async API with automatic OpenAPI documentation

## Technology Stack

- **Framework**: FastAPI 0.104.1
- **ML Models**: XGBoost with SHAP explainability
- **ML Libraries**: scikit-learn, pandas, numpy
- **Python Version**: 3.9+
- **Containerization**: Docker & Docker Compose

## Prerequisites

- Python 3.9 or higher
- pip package manager
- Docker (optional, for containerized deployment)
- Trained ML models in `../../../ml/models/xai_predictor/`

## Installation

### Local Development

1. Navigate to the service directory:

```bash
cd backend/services/service-xai-prediction
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the service:

```bash
uvicorn app.main:app --reload --port 8000
```

### Docker Deployment

Using Docker Compose (recommended):

```bash
docker-compose up
```

Or build and run manually:

```bash
docker build -t edumind-xai-service .
docker run -p 8000:8000 \
  -v $(pwd)/../../../ml/models/xai_predictor:/app/models:ro \
  edumind-xai-service
```

## API Endpoints

### Service Information

#### GET /

- Returns service metadata and status
- Response: Service name, version, status, environment

#### GET /health

- Basic health check endpoint
- Response: Health status and model loading state

### Predictions

#### GET /api/v1/health

- Detailed health check with model status
- Response: Service health, version, model loaded status

#### GET /api/v1/model/info

- Retrieve ML model information
- Response: Model type, feature count, feature names, target classes, metadata

#### POST /api/v1/predict

- Make prediction with explainable AI
- Request Body: `PredictionRequest` (student_id, features dictionary)
- Response: `PredictionResponse` (prediction result with explanation)

## API Usage Examples

### Health Check

```bash
curl http://localhost:8000/health
```

Response:

```json
{
  "status": "healthy",
  "service": "XAI Prediction Service",
  "version": "1.0.0",
  "model_loaded": true,
  "environment": "development"
}
```

### Get Model Information

```bash
curl http://localhost:8000/api/v1/model/info
```

### Make Prediction

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "123e4567-e89b-12d3-a456-426614174000",
    "features": {
      "code_module": 0,
      "code_presentation": 1,
      "gender": 0,
      "region": 5,
      "highest_education": 2,
      "imd_band": 50,
      "age_band": 2,
      "num_of_prev_attempts": 0,
      "studied_credits": 120,
      "disability": 0
    }
  }'
```

Response:

```json
{
  "prediction": {
    "id": "uuid",
    "request_id": "uuid",
    "student_id": "uuid",
    "predicted_class": "Pass",
    "probability": 0.85,
    "probabilities": {
      "Pass": 0.85,
      "Fail": 0.10,
      "Distinction": 0.03,
      "Withdrawn": 0.02
    },
    "risk_level": "low",
    "created_at": "2024-12-05T10:30:00"
  },
  "explanation": {
    "id": "uuid",
    "prediction_result_id": "uuid",
    "shap_values": {
      "studied_credits": 0.25,
      "num_of_prev_attempts": -0.15,
      "age_band": 0.10
    },
    "top_features": [
      {
        "feature_name": "studied_credits",
        "importance": 0.25,
        "shap_value": 0.25,
        "contribution": "positive"
      }
    ],
    "natural_language_explanation": "The student is predicted to Pass with high confidence (85% probability). Key positive factors: High studied credits, No previous attempts, Appropriate age range.",
    "confidence_factors": [
      "High studied credits (120)",
      "No previous failed attempts"
    ],
    "risk_factors": [],
    "created_at": "2024-12-05T10:30:00"
  }
}
```

## Configuration

Configuration is managed through environment variables defined in `.env`:

```env
# Environment
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO

# Server
HOST=0.0.0.0
PORT=8000

# ML Models Path (optional - auto-detected if not set)
ML_MODELS_PATH=/path/to/models

# Database (optional)
DATABASE_URL=

# Redis (optional)
REDIS_URL=
```

## Project Structure

```text
service-xai-prediction/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py            # API endpoint definitions
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration management
│   │   ├── logging.py           # Logging setup
│   │   └── middleware.py        # Custom middleware
│   ├── models/
│   │   ├── __init__.py
│   │   └── XaiModels.py         # Legacy data models
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── Prediction.py        # Prediction request/response schemas
│   │   └── Health.py            # Health check schemas
│   └── Services/
│       └── ml_service.py        # ML prediction logic
├── tests/
│   ├── __init__.py
│   ├── test_api.py              # API endpoint tests
│   ├── test_prediction.py       # Prediction logic tests
│   └── test_ml_service.py       # ML service tests
├── Dockerfile                    # Container definition
├── docker-compose.yml            # Local development setup
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
├── .dockerignore                 # Docker build exclusions
├── .gitignore                    # Git exclusions
├── Makefile                      # Common commands
└── README.md                     # This file
```

## Development

### Running Tests

```bash
# Run all tests
make test

# Or use pytest directly
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=app --cov-report=html
```

### Code Formatting

```bash
# Format code
make format

# Or manually
black app/
isort app/
```

### Linting

```bash
# Run linter
make lint

# Or manually
flake8 app/
```

### Common Commands

The Makefile provides shortcuts for common operations:

```bash
make help          # Show available commands
make install       # Install dependencies
make run           # Run service locally
make test          # Run tests with coverage
make docker-build  # Build Docker image
make docker-run    # Run with Docker Compose
make clean         # Clean cache files
make format        # Format code
make lint          # Run linter
```

## API Documentation

Interactive API documentation is automatically generated and available at:

- **Swagger UI**: <http://localhost:8000/api/v1/docs>
- **ReDoc**: <http://localhost:8000/api/v1/redoc>

## Model Information

The service uses pre-trained machine learning models:

- **Primary Model**: XGBoost Classifier (Calibrated)
- **Model Accuracy**: Approximately 88% (from metadata)
- **Target Classes**: Pass, Fail, Distinction, Withdrawn
- **Feature Count**: 33 features (varies based on training data)
- **Explainability**: SHAP TreeExplainer for feature importance

Required model artifacts:

- `student_model_best.joblib` - Trained model
- `scaler_best.joblib` - Feature scaler
- `label_encoder_best.joblib` - Label encoder
- `model_features_best.joblib` - Feature names list
- `model_metadata_best.joblib` - Model metadata

## Error Handling

The service implements comprehensive error handling:

- **400 Bad Request**: Invalid input data
- **422 Unprocessable Entity**: Validation errors
- **500 Internal Server Error**: Server-side errors

All errors return JSON responses with descriptive messages.

## Logging

Logging is configured with the following levels:

- **INFO**: General operational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages with stack traces
- **DEBUG**: Detailed debug information (when DEBUG=True)

Logs include timestamps, logger names, and contextual information.

## Performance Considerations

- Async/await patterns for non-blocking I/O
- Model loaded once at startup (singleton pattern)
- SHAP explainer initialized once and reused
- Feature scaling vectorized for efficiency
- Stateless prediction service for horizontal scaling

## Security

- CORS configured with allowed origins
- Input validation using Pydantic schemas
- Error messages sanitized in production
- Environment variables for sensitive configuration
- Non-root user in Docker container

## Monitoring

Health check endpoints provide:

- Service availability status
- Model loading status
- Version information
- Environment information

## Troubleshooting

### Model Loading Issues

If models fail to load:

1. Check model files exist in `ml/models/xai_predictor/`
2. Verify file permissions
3. Check ML_MODELS_PATH environment variable
4. Review startup logs for specific errors

### Prediction Errors

If predictions fail:

1. Verify all required features are provided
2. Check feature names match training data
3. Ensure feature values are numeric
4. Review error messages for validation issues

### Docker Issues

If Docker container fails:

1. Verify models are mounted correctly
2. Check container logs: `docker logs <container-id>`
3. Ensure port 8000 is not in use
4. Verify environment variables are set

## Contributing

When contributing to this service:

1. Follow PEP 8 style guidelines
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass
5. Format code with black and isort

## License

Part of the EduMind project.

## Support

For issues or questions:

- Check existing issues in the repository
- Review API documentation
- Check service logs
- Contact the development team

## Version History

**1.0.0** (2025-12-05): Initial release

- Student outcome prediction
- SHAP explainability
- Risk level assessment
- RESTful API with FastAPI
- Docker support
