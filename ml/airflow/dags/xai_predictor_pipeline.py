"""
XAI Predictor ML Pipeline DAG
============================
Apache Airflow DAG for orchestrating the ML training pipeline:
1. ETL: Process OULAD data
2. Train: Train XGBoost model
3. Validate: Validate model performance
4. Deploy: Deploy model artifacts

Author: EduMind Team
"""

from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.trigger_rule import TriggerRule


# ============================================================
# CONFIGURATION
# ============================================================
ML_BASE_PATH = Path("/opt/airflow/ml")  # Mounted volume in Docker
MODEL_PATH = ML_BASE_PATH / "models" / "xai_predictor"
DATA_PATH = MODEL_PATH / "data"
SAVED_MODELS_PATH = MODEL_PATH / "saved_models"

# Minimum accuracy threshold for deployment
MIN_ACCURACY_THRESHOLD = 0.80

# DAG default arguments
default_args = {
    "owner": "edumind-ml",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(hours=1),
}


# ============================================================
# TASK FUNCTIONS
# ============================================================
def etl_process(**context):
    """
    Extract, Transform, Load OULAD data.
    Creates processed dataset for model training.
    """
    import pandas as pd
    import numpy as np
    
    print("=" * 60)
    print("STEP 1: ETL PROCESSING")
    print("=" * 60)
    
    # Load OULAD datasets
    student_info = pd.read_csv(DATA_PATH / "raw" / "OULAD" / "studentInfo.csv")
    student_assessment = pd.read_csv(DATA_PATH / "raw" / "OULAD" / "studentAssessment.csv")
    assessments = pd.read_csv(DATA_PATH / "raw" / "OULAD" / "assessments.csv")
    
    print(f"✓ Loaded {len(student_info):,} students")
    print(f"✓ Loaded {len(student_assessment):,} assessments")
    
    # Merge data
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
        .agg({"score": ["mean", "std", "count", "min", "max"], "date_submitted": "max"})
        .reset_index()
    )
    student_metrics.columns = [
        "id_student", "code_module", "code_presentation",
        "avg_score", "score_std", "num_assessments", "min_score", "max_score", "last_submission",
    ]
    
    # Merge and create features
    df = student_info.merge(
        student_metrics, on=["id_student", "code_module", "code_presentation"], how="left"
    )
    
    # Fill missing values
    for col in ["avg_score", "score_std", "num_assessments", "min_score", "max_score"]:
        df[col] = df[col].fillna(0)
    
    # Feature engineering
    # Track max_assessments for normalization
    max_assessments = df["num_assessments"].max()
    print(f"✓ Max assessments in dataset: {max_assessments}")
    
    df["avg_grade"] = df["avg_score"]
    df["grade_consistency"] = 100 - df["score_std"].fillna(0)
    df["grade_range"] = df["max_score"] - df["min_score"]
    df["low_performance"] = (df["avg_score"] < 40).astype(int)
    df["assessment_completion_rate"] = df["num_assessments"] / max_assessments
    df["low_engagement"] = (df["num_assessments"] < df["num_assessments"].median()).astype(int)
    df["has_previous_attempts"] = (df["num_of_prev_attempts"] > 0).astype(int)
    
    # Ensure studied_credits exists (it should be in student_info)
    if "studied_credits" not in df.columns:
        print("⚠️ Warning: studied_credits not found in data, using default value of 120")
        df["studied_credits"] = 120
    
    # Target variable
    df["is_at_risk"] = df["final_result"].apply(
        lambda x: 1 if x in ["Fail", "Withdrawn"] else 0
    )
    
    # Filter and save
    df_clean = df[df["final_result"].notna()].copy()
    
    # Save to processed directory
    processed_dir = DATA_PATH / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    output_path = processed_dir / "oulad_processed.csv"
    df_clean.to_csv(output_path, index=False)
    
    print(f"✓ Saved {len(df_clean):,} processed records to {output_path}")
    print(f"✓ At-risk ratio: {df_clean['is_at_risk'].mean():.2%}")
    
    # Push metrics to XCom
    context["ti"].xcom_push(key="total_samples", value=len(df_clean))
    context["ti"].xcom_push(key="at_risk_ratio", value=float(df_clean["is_at_risk"].mean()))
    context["ti"].xcom_push(key="max_assessments", value=float(max_assessments))
    
    return str(output_path)


def train_model(**context):
    """
    Train XGBoost model on processed data.
    """
    import pandas as pd
    import numpy as np
    import xgboost as xgb
    import json
    import pickle
    from sklearn.model_selection import train_test_split
    from sklearn.utils.class_weight import compute_class_weight
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    
    print("=" * 60)
    print("STEP 2: MODEL TRAINING")
    print("=" * 60)
    
    # Load processed data
    processed_file = DATA_PATH / "processed" / "oulad_processed.csv"
    if not processed_file.exists():
        # Fallback to root data directory
        processed_file = DATA_PATH / "oulad_processed.csv"
    
    df = pd.read_csv(processed_file)
    print(f"✓ Loaded {len(df):,} samples from {processed_file}")
    
    # Load processed data
    df = pd.read_csv(DATA_PATH / "oulad_processed.csv")
    
    feature_cols = [
        "avg_grade", "grade_consistency", "grade_range", "num_assessments",
        "assessment_completion_rate", "studied_credits", "num_of_prev_attempts",
        "low_performance", "low_engagement", "has_previous_attempts",
    ]
    
    X = df[feature_cols]
    y = df["is_at_risk"]
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"✓ Training samples: {len(X_train):,}")
    print(f"✓ Test samples: {len(X_test):,}")
    
    # Class weights for imbalanced data
    class_weights = compute_class_weight("balanced", classes=np.unique(y_train), y=y_train)
    sample_weights = np.array([class_weights[int(y)] for y in y_train])
    
    # Train model
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="binary:logistic",
        random_state=42,
        use_label_encoder=False,
        eval_metric="logloss",
    )
    
    model.fit(X_train, y_train, sample_weight=sample_weights, verbose=False)
    print("✓ Model trained successfully!")
    
    # Evaluate
    y_pred = model.predict(X_test)
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred)),
        "recall": float(recall_score(y_test, y_pred)),
        "f1": float(f1_score(y_test, y_pred)),
    }
    
    print(f"\nModel Performance:")
    print(f"  Accuracy:  {metrics['accuracy']:.4f}")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall:    {metrics['recall']:.4f}")
    print(f"  F1 Score:  {metrics['f1']:.4f}")
    
    # Save model artifacts
    SAVED_MODELS_PATH.mkdir(parents=True, exist_ok=True)
    
    model_path = SAVED_MODELS_PATH / "academic_risk_model.json"
    # Get max_assessments from XCom
    max_assessments = context["ti"].xcom_pull(task_ids="etl_process", key="max_assessments")
    
    # Calculate feature ranges for validation
    feature_ranges = {}
    for col in feature_cols:
        if col in X_train.columns:
            feature_ranges[col] = {
                "min": float(X_train[col].min()),
                "max": float(X_train[col].max()),
                "mean": float(X_train[col].mean()),
                "std": float(X_train[col].std()),
            }
    
    # Save metadata
    metadata = {
        "feature_names": feature_cols,
        "feature_count": len(feature_cols),
        "model_type": "XGBClassifier",
        "classes": ["Safe", "At-Risk"],
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "metrics": metrics,
        "trained_at": datetime.now().isoformat(),
        "min_accuracy_threshold": MIN_ACCURACY_THRESHOLD,
        "max_assessments": max_assessments,
        "feature_ranges": feature_ranges,
    }
    
    metadata_path = SAVED_MODELS_PATH / "model_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✓ Model saved to {model_path}")
    print(f"✓ Metadata saved to {metadata_path}")
    
    # Push metrics to XCom
    context["ti"].xcom_push(key="accuracy", value=metrics["accuracy"])
    context["ti"].xcom_push(key="metrics", value=metrics)
    
    return metrics["accuracy"]


def validate_model(**context):
    """
    Validate model meets deployment criteria.
    Returns task_id for branching.
    """
    print("=" * 60)
    print("STEP 3: MODEL VALIDATION")
    print("=" * 60)
    
    accuracy = context["ti"].xcom_pull(task_ids="train_model", key="accuracy")
    
    print(f"Model Accuracy: {accuracy:.4f}")
    print(f"Threshold: {MIN_ACCURACY_THRESHOLD:.4f}")
    
    if accuracy >= MIN_ACCURACY_THRESHOLD:
        print("✓ Model PASSED validation - proceeding to deployment")
        return "deploy_model"
    else:
        print("✗ Model FAILED validation - accuracy too low")
        return "validation_failed"


def deploy_model(**context):
    """
    Deploy model to the backend service.
    """
    import shutil
    
    print("=" * 60)
    print("STEP 4: MODEL DEPLOYMENT")
    print("=" * 60)
    
    # Source and destination paths
    source_dir = SAVED_MODELS_PATH
    dest_dir = ML_BASE_PATH.parent / "backend" / "services" / "service-xai-prediction" / "app" / "model"
    
    # Copy model files
    for file_name in ["academic_risk_model.json", "model_metadata.json"]:
        src = source_dir / file_name
        dst = dest_dir / file_name
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"✓ Deployed: {file_name}")
    
    metrics = context["ti"].xcom_pull(task_ids="train_model", key="metrics")
    print(f"\nDeployment complete with accuracy: {metrics['accuracy']:.4f}")
    
    return "success"


def notify_failure(**context):
    """
    Handle validation failure notification.
    """
    accuracy = context["ti"].xcom_pull(task_ids="train_model", key="accuracy")
    print(f"⚠️ Model validation failed. Accuracy: {accuracy:.4f} < {MIN_ACCURACY_THRESHOLD}")
    print("Please review training data and model parameters.")


# ============================================================
# DAG DEFINITION
# ============================================================
with DAG(
    dag_id="xai_predictor_training_pipeline",
    description="ML Pipeline for XAI Academic Risk Predictor",
    default_args=default_args,
    schedule_interval="@weekly",  # Run weekly
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["ml", "xai", "training", "edumind"],
    doc_md=__doc__,
) as dag:
    
    # Start task
    start = DummyOperator(task_id="start")
    
    # ETL task
    etl_task = PythonOperator(
        task_id="etl_process",
        python_callable=etl_process,
        provide_context=True,
    )
    
    # Training task
    train_task = PythonOperator(
        task_id="train_model",
        python_callable=train_model,
        provide_context=True,
    )
    
    # Validation branch
    validate_task = BranchPythonOperator(
        task_id="validate_model",
        python_callable=validate_model,
        provide_context=True,
    )
    
    # Deploy task (only if validation passes)
    deploy_task = PythonOperator(
        task_id="deploy_model",
        python_callable=deploy_model,
        provide_context=True,
    )
    
    # Validation failed notification
    failed_task = PythonOperator(
        task_id="validation_failed",
        python_callable=notify_failure,
        provide_context=True,
    )
    
    # End task
    end = DummyOperator(
        task_id="end",
        trigger_rule=TriggerRule.ONE_SUCCESS,
    )
    
    # Define task dependencies
    start >> etl_task >> train_task >> validate_task
    validate_task >> [deploy_task, failed_task]
    [deploy_task, failed_task] >> end
