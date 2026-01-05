#!/usr/bin/env python3
"""
XAI Predictor Training Script
=============================
Unified training script for the Academic Risk Prediction model.
This script is designed to work both locally and in CI/CD pipelines.

Usage:
    python train.py                     # Run full pipeline
    python train.py --step etl          # Run ETL only
    python train.py --step train        # Run training only
    python train.py --step validate     # Run validation only

Author: EduMind Team
"""

import argparse
import json
import os
import pickle
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight


# ============================================================
# CONFIGURATION
# ============================================================
# Use relative paths from this script's location
SCRIPT_DIR = Path(__file__).parent.resolve()
DATA_DIR = SCRIPT_DIR / "data"
OULAD_DIR = DATA_DIR / "OULAD"
SAVED_MODELS_DIR = SCRIPT_DIR / "saved_models"

# Model configuration
FEATURE_COLS = [
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

MODEL_PARAMS = {
    "n_estimators": 200,
    "max_depth": 5,
    "learning_rate": 0.1,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "objective": "binary:logistic",
    "random_state": 42,
    "use_label_encoder": False,
    "eval_metric": "logloss",
}

MIN_ACCURACY_THRESHOLD = 0.80


# ============================================================
# ETL FUNCTIONS
# ============================================================
def run_etl() -> Path:
    """
    Extract, Transform, Load OULAD data.
    Returns path to processed CSV file.
    """
    print("=" * 60)
    print("STEP 1: ETL PROCESSING")
    print("=" * 60)
    
    # Check for raw data
    if not OULAD_DIR.exists():
        print(f"Error: OULAD directory not found at {OULAD_DIR}")
        print("Please download OULAD data from: https://analyse.kmi.open.ac.uk/open_dataset")
        sys.exit(1)
    
    # Load datasets
    print("\nLoading OULAD datasets...")
    student_info = pd.read_csv(OULAD_DIR / "studentInfo.csv")
    student_assessment = pd.read_csv(OULAD_DIR / "studentAssessment.csv")
    assessments = pd.read_csv(OULAD_DIR / "assessments.csv")
    
    print(f"✓ Student Info: {len(student_info):,} records")
    print(f"✓ Student Assessments: {len(student_assessment):,} records")
    print(f"✓ Assessment Details: {len(assessments):,} records")
    
    # Merge data
    print("\nProcessing data...")
    assessment_data = student_assessment.merge(
        student_info[["id_student", "code_module", "code_presentation"]],
        on="id_student",
        how="left",
    )
    assessment_data = assessment_data.merge(
        assessments[["id_assessment", "assessment_type", "weight"]],
        on="id_assessment",
        how="left",
    )
    
    # Calculate per-student metrics
    student_metrics = (
        assessment_data.groupby(["id_student", "code_module", "code_presentation"])
        .agg({
            "score": ["mean", "std", "count", "min", "max"],
            "date_submitted": "max"
        })
        .reset_index()
    )
    student_metrics.columns = [
        "id_student", "code_module", "code_presentation",
        "avg_score", "score_std", "num_assessments", 
        "min_score", "max_score", "last_submission",
    ]
    
    # Merge with student info
    df = student_info.merge(
        student_metrics,
        on=["id_student", "code_module", "code_presentation"],
        how="left",
    )
    
    # Fill missing values
    for col in ["avg_score", "score_std", "num_assessments", "min_score", "max_score"]:
        df[col] = df[col].fillna(0)
    
    # Feature engineering
    print("\nEngineering features...")
    df["avg_grade"] = df["avg_score"]
    df["grade_consistency"] = 100 - df["score_std"].fillna(0)
    df["grade_range"] = df["max_score"] - df["min_score"]
    df["low_performance"] = (df["avg_score"] < 40).astype(int)
    df["assessment_completion_rate"] = df["num_assessments"] / df["num_assessments"].max()
    df["low_engagement"] = (df["num_assessments"] < df["num_assessments"].median()).astype(int)
    df["has_previous_attempts"] = (df["num_of_prev_attempts"] > 0).astype(int)
    
    # Target variable
    df["is_at_risk"] = df["final_result"].apply(
        lambda x: 1 if x in ["Fail", "Withdrawn"] else 0
    )
    
    # Filter clean data
    df_clean = df[df["final_result"].notna()].copy()
    
    # Select output columns
    output_cols = (
        ["id_student", "code_module", "code_presentation", "gender", 
         "region", "highest_education", "age_band", "final_result"]
        + FEATURE_COLS
        + ["is_at_risk"]
    )
    output_df = df_clean[output_cols]
    
    # Save processed data
    output_path = DATA_DIR / "oulad_processed.csv"
    output_df.to_csv(output_path, index=False)
    
    print(f"\n✓ Processed {len(output_df):,} student records")
    print(f"  - Safe: {sum(output_df['is_at_risk'] == 0):,} ({sum(output_df['is_at_risk'] == 0) / len(output_df) * 100:.1f}%)")
    print(f"  - At-Risk: {sum(output_df['is_at_risk'] == 1):,} ({sum(output_df['is_at_risk'] == 1) / len(output_df) * 100:.1f}%)")
    print(f"✓ Saved to: {output_path}")
    
    return output_path


# ============================================================
# TRAINING FUNCTIONS
# ============================================================
def run_training() -> dict:
    """
    Train XGBoost model on processed data.
    Returns model metrics dictionary.
    """
    print("\n" + "=" * 60)
    print("STEP 2: MODEL TRAINING")
    print("=" * 60)
    
    # Load processed data
    data_path = DATA_DIR / "oulad_processed.csv"
    if not data_path.exists():
        print(f"Error: Processed data not found at {data_path}")
        print("Please run ETL first: python train.py --step etl")
        sys.exit(1)
    
    df = pd.read_csv(data_path)
    print(f"\n✓ Loaded {len(df):,} records from {data_path}")
    
    X = df[FEATURE_COLS]
    y = df["is_at_risk"]
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"✓ Training samples: {len(X_train):,}")
    print(f"✓ Test samples: {len(X_test):,}")
    
    # Class weights for imbalanced data
    class_weights = compute_class_weight("balanced", classes=np.unique(y_train), y=y_train)
    sample_weights = np.array([class_weights[int(label)] for label in y_train])
    
    # Train model
    print("\nTraining XGBoost model...")
    model = xgb.XGBClassifier(**MODEL_PARAMS)
    model.fit(X_train, y_train, sample_weight=sample_weights, verbose=False)
    print("✓ Model trained successfully!")
    
    # Evaluate
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)
    
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred)),
        "recall": float(recall_score(y_test, y_pred)),
        "f1": float(f1_score(y_test, y_pred)),
    }
    
    print(f"\n📊 Model Performance:")
    print(f"   Accuracy:  {metrics['accuracy']:.4f}")
    print(f"   Precision: {metrics['precision']:.4f}")
    print(f"   Recall:    {metrics['recall']:.4f}")
    print(f"   F1 Score:  {metrics['f1']:.4f}")
    
    print("\n📈 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Safe", "At-Risk"]))
    
    print("🔢 Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"   TN={cm[0][0]}, FP={cm[0][1]}")
    print(f"   FN={cm[1][0]}, TP={cm[1][1]}")
    
    # Feature importance
    print("\n🎯 Feature Importance (Top 5):")
    importance = dict(zip(FEATURE_COLS, model.feature_importances_))
    sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    for i, (feat, imp) in enumerate(sorted_importance[:5], 1):
        print(f"   {i}. {feat}: {imp:.4f}")
    
    # Save model artifacts
    SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save XGBoost native format
    model_path = SAVED_MODELS_DIR / "academic_risk_model.json"
    model.save_model(str(model_path))
    print(f"\n✓ Model saved: {model_path}")
    
    # Save pickle format
    pickle_path = SAVED_MODELS_DIR / "academic_risk_model.pkl"
    with open(pickle_path, "wb") as f:
        pickle.dump(model, f)
    print(f"✓ Pickle saved: {pickle_path}")
    
    # Save metadata
    metadata = {
        "feature_names": FEATURE_COLS,
        "feature_count": len(FEATURE_COLS),
        "model_type": "XGBClassifier",
        "classes": ["Safe", "At-Risk"],
        "training_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "metrics": metrics,
        "feature_importance": {k: float(v) for k, v in importance.items()},
        "model_params": MODEL_PARAMS,
        "trained_at": datetime.now().isoformat(),
        "python_version": sys.version,
        "xgboost_version": xgb.__version__,
    }
    
    metadata_path = SAVED_MODELS_DIR / "model_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Metadata saved: {metadata_path}")
    
    return metrics


# ============================================================
# VALIDATION FUNCTIONS
# ============================================================
def run_validation() -> bool:
    """
    Validate model meets deployment criteria.
    Returns True if validation passes.
    """
    print("\n" + "=" * 60)
    print("STEP 3: MODEL VALIDATION")
    print("=" * 60)
    
    # Load metadata
    metadata_path = SAVED_MODELS_DIR / "model_metadata.json"
    if not metadata_path.exists():
        print(f"Error: Model metadata not found at {metadata_path}")
        print("Please run training first: python train.py --step train")
        sys.exit(1)
    
    with open(metadata_path) as f:
        metadata = json.load(f)
    
    # Handle both old and new metadata formats
    if "metrics" in metadata:
        accuracy = metadata["metrics"]["accuracy"]
    else:
        accuracy = metadata.get("accuracy", 0.0)
    
    print(f"\nModel Accuracy: {accuracy:.4f}")
    print(f"Threshold: {MIN_ACCURACY_THRESHOLD:.4f}")
    
    # Validation checks
    checks = {
        "accuracy_threshold": accuracy >= MIN_ACCURACY_THRESHOLD,
        "model_file_exists": (SAVED_MODELS_DIR / "academic_risk_model.json").exists(),
        "pickle_file_exists": (SAVED_MODELS_DIR / "academic_risk_model.pkl").exists(),
        "metadata_file_exists": metadata_path.exists(),
        "feature_count_correct": len(metadata.get("feature_names", [])) == len(FEATURE_COLS),
    }
    
    print("\n📋 Validation Checks:")
    all_passed = True
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"   {status} {check.replace('_', ' ').title()}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ Model PASSED all validation checks!")
        return True
    else:
        print("\n❌ Model FAILED validation")
        return False


# ============================================================
# MAIN ENTRY POINT
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="XAI Predictor Training Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python train.py                  Run full pipeline (ETL + Train + Validate)
  python train.py --step etl       Run ETL only
  python train.py --step train     Run training only
  python train.py --step validate  Run validation only
        """
    )
    parser.add_argument(
        "--step",
        choices=["etl", "train", "validate", "all"],
        default="all",
        help="Pipeline step to run (default: all)",
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("XAI PREDICTOR TRAINING PIPELINE")
    print(f"Started at: {datetime.now().isoformat()}")
    print("=" * 60)
    
    success = True
    
    if args.step in ["etl", "all"]:
        run_etl()
    
    if args.step in ["train", "all"]:
        metrics = run_training()
    
    if args.step in ["validate", "all"]:
        success = run_validation()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ PIPELINE COMPLETED SUCCESSFULLY")
    else:
        print("❌ PIPELINE FAILED")
    print("=" * 60)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
