# Model Saving and Deployment Script
import json
import pickle

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight

print("=" * 60)
print("SAVING OULAD MODEL FOR DEPLOYMENT")
print("=" * 60)

# ============================================================
# STEP 1: LOAD DATA AND TRAIN MODEL
# ============================================================
print("\n1. Loading data and training model...")

INPUT_FILE = "/Users/ravinbandara/Desktop/Ravin/EduMind/ml/models/xai_predictor/data/oulad_processed.csv"
df = pd.read_csv(INPUT_FILE)

feature_cols = [
    "avg_grade",
    "grade_consistency",
    "grade_range",
    "num_assessments",
    "assessment_completion_rate",
    "studied_credits",
    "num_of_prev_attempts",
    "low_performance",
    "low_engagement",
    "has_previous_attempts",
]

X = df[feature_cols]
y = df["is_at_risk"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Train model
class_weights = compute_class_weight("balanced", classes=np.unique(y_train), y=y_train)
sample_weights = np.array([class_weights[int(y)] for y in y_train])

model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="binary:logistic",
    random_state=42,
)

model.fit(X_train, y_train, sample_weight=sample_weights, verbose=False)
print("✓ Model trained successfully!")

# ============================================================
# STEP 2: SAVE MODEL FILES
# ============================================================
print("\n2. Saving model files...")

MODEL_DIR = (
    "/Users/ravinbandara/Desktop/Ravin/EduMind/ml/models/xai_predictor/saved_models"
)
import os

os.makedirs(MODEL_DIR, exist_ok=True)

# Save XGBoost model (native format - best for XGBoost)
model_path = f"{MODEL_DIR}/academic_risk_model.json"
model.save_model(model_path)
print(f"✓ Model saved: {model_path}")

# Save as pickle (alternative format)
pickle_path = f"{MODEL_DIR}/academic_risk_model.pkl"
with open(pickle_path, "wb") as f:
    pickle.dump(model, f)
print(f"✓ Pickle saved: {pickle_path}")

# ============================================================
# STEP 3: SAVE FEATURE METADATA
# ============================================================
print("\n3. Saving feature metadata...")

metadata = {
    "feature_names": feature_cols,
    "feature_count": len(feature_cols),
    "model_type": "XGBClassifier",
    "classes": ["Safe", "At-Risk"],
    "training_samples": len(X_train),
    "test_accuracy": float((model.predict(X_test) == y_test).mean()),
    "feature_descriptions": {
        "avg_grade": "Average assessment score (0-100)",
        "grade_consistency": "Performance consistency (100 - std)",
        "grade_range": "Score variability (max - min)",
        "num_assessments": "Number of assessments completed",
        "assessment_completion_rate": "Completion rate (0-1)",
        "studied_credits": "Course credits enrolled",
        "num_of_prev_attempts": "Number of previous attempts",
        "low_performance": "Binary: grade < 40%",
        "low_engagement": "Binary: low assessment completion",
        "has_previous_attempts": "Binary: has failed before",
    },
}

metadata_path = f"{MODEL_DIR}/model_metadata.json"
with open(metadata_path, "w") as f:
    json.dump(metadata, f, indent=2)
print(f"✓ Metadata saved: {metadata_path}")

# ============================================================
# STEP 4: TEST MODEL LOADING
# ============================================================
print("\n4. Testing model loading...")

# Load model
loaded_model = xgb.XGBClassifier()
loaded_model.load_model(model_path)

# Test prediction
test_sample = X_test.iloc[0:1]
prediction = loaded_model.predict(test_sample)[0]
probability = loaded_model.predict_proba(test_sample)[0]

print(f"✓ Model loaded and tested successfully!")
print(f"  Test prediction: {'At-Risk' if prediction == 1 else 'Safe'}")
print(f"  Confidence: {probability[prediction]*100:.1f}%")

print("\n" + "=" * 60)
print("MODEL DEPLOYMENT PACKAGE READY!")
print("=" * 60)
print(f"\nSaved files:")
print(f"  1. Model: {model_path}")
print(f"  2. Pickle: {pickle_path}")
print(f"  3. Metadata: {metadata_path}")
print(f"\nModel accuracy: {metadata['test_accuracy']*100:.1f}%")
