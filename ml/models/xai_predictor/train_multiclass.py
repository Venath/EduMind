#!/usr/bin/env python3
"""
XAI Predictor Multi-Class Training Script
=========================================
Training script for 3-tier Academic Risk Prediction model: Safe, Medium Risk, At-Risk

Usage:
    python train_multiclass.py                     # Run full pipeline
    python train_multiclass.py --step etl          # Run ETL only
    python train_multiclass.py --step train        # Run training only
    python train_multiclass.py --step validate     # Run validation only

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
    "max_depth": 6,
    "learning_rate": 0.1,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "objective": "multi:softprob",  # Multi-class classification
    "num_class": 3,  # 3 classes: Safe, Medium, At-Risk
    "random_state": 42,
    "use_label_encoder": False,
    "eval_metric": "mlogloss",
}

MIN_ACCURACY_THRESHOLD = 0.75  # Lower threshold for multi-class

# Risk thresholds for creating 3 tiers
RISK_THRESHOLDS = {
    "safe": {
        "avg_grade": 70,          # >= 70 is good
        "num_assessments": 6,      # >= 6 is engaged
        "completion_rate": 0.6,    # >= 60% completion
        "has_failures": False,     # No previous failures
    },
    "at_risk": {
        "avg_grade": 55,          # < 55 is failing
        "num_assessments": 4,      # < 4 is disengaged
        "completion_rate": 0.4,    # < 40% completion
        "has_failures": True,      # Has previous failures
    }
}


# ============================================================
# ETL FUNCTIONS
# ============================================================
def create_risk_category(row) -> int:
    """
    Create 3-tier risk category based on multiple factors.
    Returns: 0=Safe, 1=Medium Risk, 2=At-Risk
    """
    # Check if explicitly failed or withdrawn
    if row["final_result"] in ["Fail", "Withdrawn"]:
        base_at_risk = True
    else:
        base_at_risk = False
    
    # Calculate risk score based on features
    risk_score = 0
    
    # Grade-based risk (40% weight)
    if row["avg_grade"] < 55:
        risk_score += 4
    elif row["avg_grade"] < 65:
        risk_score += 2
    elif row["avg_grade"] >= 75:
        risk_score -= 1
    
    # Assessment engagement (30% weight)
    if row["num_assessments"] < 4:
        risk_score += 3
    elif row["num_assessments"] < 6:
        risk_score += 1
    elif row["num_assessments"] >= 8:
        risk_score -= 1
    
    # Completion rate (15% weight)
    completion = row["assessment_completion_rate"]
    if completion < 0.3:
        risk_score += 2
    elif completion < 0.5:
        risk_score += 1
    elif completion >= 0.7:
        risk_score -= 1
    
    # Previous attempts (15% weight)
    if row["num_of_prev_attempts"] > 1:
        risk_score += 2
    elif row["num_of_prev_attempts"] == 1:
        risk_score += 1
    
    # Grade consistency
    if row["grade_consistency"] < 70:
        risk_score += 1
    elif row["grade_consistency"] >= 90:
        risk_score -= 1
    
    # Determine final category
    if base_at_risk or risk_score >= 5:
        return 2  # At-Risk
    elif risk_score >= 2:
        return 1  # Medium Risk
    else:
        return 0  # Safe


def run_etl() -> Path:
    """
    Extract, Transform, Load OULAD data with 3-tier risk categories.
    Returns path to processed CSV file.
    """
    print("=" * 60)
    print("STEP 1: ETL PROCESSING (Multi-Class)")
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
    
    # Create 3-tier risk category
    print("\nCreating 3-tier risk categories...")
    df["risk_category"] = df.apply(create_risk_category, axis=1)
    
    # Filter clean data
    df_clean = df[df["final_result"].notna()].copy()
    
    # Select output columns
    output_cols = (
        ["id_student", "code_module", "code_presentation", "gender", 
         "region", "highest_education", "age_band", "final_result"]
        + FEATURE_COLS
        + ["risk_category"]
    )
    output_df = df_clean[output_cols]
    
    # Save processed data
    output_path = DATA_DIR / "oulad_processed_multiclass.csv"
    output_df.to_csv(output_path, index=False)
    
    # Print distribution
    print(f"\n✓ Processed {len(output_df):,} student records")
    category_counts = output_df["risk_category"].value_counts().sort_index()
    print(f"  - Safe (0): {category_counts.get(0, 0):,} ({category_counts.get(0, 0) / len(output_df) * 100:.1f}%)")
    print(f"  - Medium Risk (1): {category_counts.get(1, 0):,} ({category_counts.get(1, 0) / len(output_df) * 100:.1f}%)")
    print(f"  - At-Risk (2): {category_counts.get(2, 0):,} ({category_counts.get(2, 0) / len(output_df) * 100:.1f}%)")
    print(f"✓ Saved to: {output_path}")
    
    return output_path


# ============================================================
# TRAINING FUNCTIONS
# ============================================================
def run_training() -> dict:
    """
    Train XGBoost multi-class model on processed data.
    Returns model metrics dictionary.
    """
    print("\n" + "=" * 60)
    print("STEP 2: MULTI-CLASS MODEL TRAINING")
    print("=" * 60)
    
    # Load processed data
    data_path = DATA_DIR / "oulad_processed_multiclass.csv"
    if not data_path.exists():
        print(f"Error: Processed data not found at {data_path}")
        print("Please run ETL first: python train_multiclass.py --step etl")
        sys.exit(1)
    
    df = pd.read_csv(data_path)
    print(f"\n✓ Loaded {len(df):,} records from {data_path}")
    
    X = df[FEATURE_COLS]
    y = df["risk_category"]
    
    # Print class distribution
    print("\nClass Distribution:")
    for cls in sorted(y.unique()):
        count = sum(y == cls)
        print(f"  Class {cls}: {count:,} ({count / len(y) * 100:.1f}%)")
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n✓ Training samples: {len(X_train):,}")
    print(f"✓ Test samples: {len(X_test):,}")
    
    # Class weights for imbalanced data
    class_weights = compute_class_weight("balanced", classes=np.unique(y_train), y=y_train)
    sample_weights = np.array([class_weights[int(label)] for label in y_train])
    
    print(f"\nClass weights: {dict(enumerate(class_weights))}")
    
    # Train model
    print("\nTraining XGBoost multi-class model...")
    model = xgb.XGBClassifier(**MODEL_PARAMS)
    model.fit(X_train, y_train, sample_weight=sample_weights, verbose=False)
    print("✓ Model trained successfully!")
    
    # Evaluate
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)
    
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision_macro": float(precision_score(y_test, y_pred, average="macro")),
        "recall_macro": float(recall_score(y_test, y_pred, average="macro")),
        "f1_macro": float(f1_score(y_test, y_pred, average="macro")),
        "precision_weighted": float(precision_score(y_test, y_pred, average="weighted")),
        "recall_weighted": float(recall_score(y_test, y_pred, average="weighted")),
        "f1_weighted": float(f1_score(y_test, y_pred, average="weighted")),
    }
    
    print(f"\n📊 Model Performance:")
    print(f"   Accuracy:          {metrics['accuracy']:.4f}")
    print(f"   Precision (macro): {metrics['precision_macro']:.4f}")
    print(f"   Recall (macro):    {metrics['recall_macro']:.4f}")
    print(f"   F1 Score (macro):  {metrics['f1_macro']:.4f}")
    
    print("\n📈 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Safe", "Medium Risk", "At-Risk"]))
    
    print("🔢 Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print("     Predicted:")
    print("           Safe  Medium  At-Risk")
    print(f"Safe      {cm[0][0]:4d}   {cm[0][1]:4d}    {cm[0][2]:4d}")
    print(f"Medium    {cm[1][0]:4d}   {cm[1][1]:4d}    {cm[1][2]:4d}")
    print(f"At-Risk   {cm[2][0]:4d}   {cm[2][1]:4d}    {cm[2][2]:4d}")
    
    # Feature importance
    print("\n🎯 Feature Importance:")
    importance = dict(zip(FEATURE_COLS, model.feature_importances_))
    sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    for i, (feat, imp) in enumerate(sorted_importance, 1):
        print(f"   {i:2d}. {feat:35s}: {imp:.4f} ({imp*100:.1f}%)")
    
    # Save model artifacts
    SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save XGBoost native format
    model_path = SAVED_MODELS_DIR / "academic_risk_model_multiclass.json"
    model.save_model(str(model_path))
    print(f"\n✓ Model saved: {model_path}")
    
    # Save pickle format
    pickle_path = SAVED_MODELS_DIR / "academic_risk_model_multiclass.pkl"
    with open(pickle_path, "wb") as f:
        pickle.dump(model, f)
    print(f"✓ Pickle saved: {pickle_path}")
    
    # Calculate feature statistics from training data
    feature_stats = {}
    for feat in FEATURE_COLS:
        feature_stats[feat] = {
            "min": float(X_train[feat].min()),
            "max": float(X_train[feat].max()),
            "mean": float(X_train[feat].mean()),
            "std": float(X_train[feat].std()),
        }
    
    # Save metadata
    metadata = {
        "feature_names": FEATURE_COLS,
        "feature_count": len(FEATURE_COLS),
        "model_type": "XGBClassifier",
        "objective": "multi:softprob",
        "num_classes": 3,
        "classes": ["Safe", "Medium Risk", "At-Risk"],
        "class_labels": {0: "Safe", 1: "Medium Risk", 2: "At-Risk"},
        "training_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "metrics": metrics,
        "feature_importance": {k: float(v) for k, v in importance.items()},
        "feature_ranges": feature_stats,
        "model_params": MODEL_PARAMS,
        "trained_at": datetime.now().isoformat(),
        "python_version": sys.version,
        "xgboost_version": xgb.__version__,
    }
    
    metadata_path = SAVED_MODELS_DIR / "model_metadata_multiclass.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Metadata saved: {metadata_path}")
    
    return metrics


# ============================================================
# VALIDATION FUNCTIONS
# ============================================================
def run_validation() -> bool:
    """
    Validate the trained model meets minimum requirements.
    Returns True if validation passes.
    """
    print("\n" + "=" * 60)
    print("STEP 3: MODEL VALIDATION")
    print("=" * 60)
    
    metadata_path = SAVED_MODELS_DIR / "model_metadata_multiclass.json"
    if not metadata_path.exists():
        print(f"Error: Metadata not found at {metadata_path}")
        print("Please run training first: python train_multiclass.py --step train")
        return False
    
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
    
    accuracy = metadata["metrics"]["accuracy"]
    print(f"\n✓ Model Accuracy: {accuracy:.4f}")
    print(f"  Minimum Required: {MIN_ACCURACY_THRESHOLD:.4f}")
    
    if accuracy >= MIN_ACCURACY_THRESHOLD:
        print("\n✅ VALIDATION PASSED!")
        print(f"   Model exceeds minimum accuracy threshold")
        return True
    else:
        print("\n❌ VALIDATION FAILED!")
        print(f"   Model accuracy ({accuracy:.4f}) below threshold ({MIN_ACCURACY_THRESHOLD:.4f})")
        return False


# ============================================================
# MAIN
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="Train XAI Multi-Class Predictor")
    parser.add_argument(
        "--step",
        choices=["etl", "train", "validate", "all"],
        default="all",
        help="Which step to run (default: all)",
    )
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("XAI MULTI-CLASS PREDICTOR TRAINING PIPELINE")
    print("=" * 60)
    print(f"Step: {args.step}")
    print(f"Working Directory: {SCRIPT_DIR}")
    print("=" * 60)
    
    try:
        if args.step in ["etl", "all"]:
            run_etl()
        
        if args.step in ["train", "all"]:
            metrics = run_training()
        
        if args.step in ["validate", "all"]:
            validation_passed = run_validation()
            if not validation_passed:
                sys.exit(1)
        
        print("\n" + "=" * 60)
        print("✅ PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Pipeline failed with error:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
