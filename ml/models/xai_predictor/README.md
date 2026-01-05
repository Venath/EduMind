# XAI Academic Risk Predictor

An explainable AI model for predicting student academic risk using the OULAD dataset.

## 🎯 Overview

This package provides:
- **Binary Classification**: Predicts if a student is at-risk (Fail/Withdrawn) or safe (Pass/Distinction)
- **Explainability**: SHAP-based explanations for individual predictions
- **86%+ Accuracy**: Trained on 32,000+ student records from Open University

## 📁 Project Structure

```
xai_predictor/
├── README.md                    # This file
├── pyproject.toml               # Project configuration
├── config/
│   ├── __init__.py
│   └── settings.py              # Centralized configuration
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── etl.py               # ETL pipeline
│   │   └── preprocessing.py     # Feature engineering
│   ├── models/
│   │   ├── __init__.py
│   │   ├── trainer.py           # Model training
│   │   ├── predictor.py         # Inference
│   │   └── explainer.py         # SHAP explanations
│   └── utils/
│       ├── __init__.py
│       └── metrics.py           # Custom metrics
├── tests/
│   ├── __init__.py
│   ├── test_etl.py
│   ├── test_trainer.py
│   └── test_predictor.py
├── notebooks/                   # Jupyter experiments
│   └── exploration.ipynb
├── data/                        # Data files (git-ignored)
│   ├── raw/                     # Original OULAD data
│   └── processed/               # Transformed data
├── artifacts/
│   ├── models/                  # Trained model files
│   └── metrics/                 # Evaluation results
└── scripts/
    └── run_pipeline.py          # CLI entrypoint
```

## 🚀 Quick Start

### Installation

```bash
cd ml/models/xai_predictor
pip install -e .
```

### Training

```bash
# Full pipeline (ETL + Train + Validate)
python -m scripts.run_pipeline

# Individual steps
python -m scripts.run_pipeline --step etl
python -m scripts.run_pipeline --step train
python -m scripts.run_pipeline --step validate
```

### Prediction

```python
from src.models.predictor import RiskPredictor

predictor = RiskPredictor()

# Single prediction
result = predictor.predict({
    "avg_grade": 65.0,
    "grade_consistency": 85.0,
    "num_assessments": 5,
    "assessment_completion_rate": 0.8,
    "studied_credits": 60,
    "num_of_prev_attempts": 0,
})

print(f"Risk Level: {result['risk_level']}")
print(f"Probability: {result['probability']:.2%}")
```

### Explanations

```python
from src.models.explainer import RiskExplainer

explainer = RiskExplainer()
explanation = explainer.explain(student_features)

print(explanation['top_factors'])
# [('assessment_completion_rate', -0.15), ('avg_grade', 0.08), ...]
```

## 📊 Model Details

| Metric | Value |
|--------|-------|
| Algorithm | XGBoost Classifier |
| Accuracy | 86.2% |
| Precision | 91.6% |
| Recall | 81.3% |
| F1 Score | 86.2% |

### Features (10)

| Feature | Description |
|---------|-------------|
| `avg_grade` | Average assessment score (0-100) |
| `grade_consistency` | Performance consistency (100 - std) |
| `grade_range` | Score variability (max - min) |
| `num_assessments` | Number of assessments completed |
| `assessment_completion_rate` | Completion rate (0-1) |
| `studied_credits` | Course credits enrolled |
| `num_of_prev_attempts` | Number of previous attempts |
| `low_performance` | Binary: grade < 40% |
| `low_engagement` | Binary: low assessment completion |
| `has_previous_attempts` | Binary: has failed before |

## 🔬 Explainability

The model uses SHAP (SHapley Additive exPlanations) to provide:

1. **Feature Importance**: Which features matter most globally
2. **Individual Explanations**: Why a specific student was classified
3. **Counterfactual Analysis**: What changes would alter the prediction

## 📈 Data Source

[OULAD - Open University Learning Analytics Dataset](https://analyse.kmi.open.ac.uk/open_dataset)

- 32,593 student records
- 7 courses over 2 years
- Assessment and VLE interaction data

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 🔄 Migration Guide

If you're upgrading from the legacy flat structure:

### Update Imports

```python
# Old (legacy)
from train import train_model
import xgboost as xgb
model = xgb.XGBClassifier()
model.load_model("saved_models/model.json")

# New (restructured)
from src.models.trainer import Trainer
from src.models.predictor import RiskPredictor

predictor = RiskPredictor()  # Handles model loading automatically
```

### Update CLI Commands

```bash
# Old
python train.py --step all

# New  
python -m scripts.run_pipeline --step all
```

### Legacy File Compatibility

The `saved_models/` directory is still supported for backward compatibility.
New models will be saved there unless configured otherwise in `config/settings.py`.

## 📝 License

MIT License - EduMind Team
