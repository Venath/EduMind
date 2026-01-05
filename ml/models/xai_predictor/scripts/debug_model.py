"""
Debug Model Predictions
========================
Investigate why the model predicts all students as at-risk.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import xgboost as xgb
from config.settings import FEATURE_COLUMNS, get_model_path, get_processed_data_path

def main():
    print("="*60)
    print("Model Debugging")
    print("="*60)
    
    # Load model
    model_path = get_model_path(use_legacy=True)
    print(f"\nLoading model from: {model_path}")
    
    model = xgb.XGBClassifier()
    model.load_model(str(model_path))
    
    print(f"Model classes: {model.classes_}")
    print(f"Number of features: {model.n_features_in_}")
    
    # Load training data to check a few samples
    data_path = get_processed_data_path(use_legacy=True)
    df = pd.read_csv(data_path)
    
    print(f"\n✓ Loaded {len(df):,} records")
    print(f"\nTarget distribution:")
    print(df['is_at_risk'].value_counts())
    print(f"\nTarget percentages:")
    print(df['is_at_risk'].value_counts(normalize=True) * 100)
    
    # Test with actual data from the dataset
    print("\n" + "="*60)
    print("Testing with ACTUAL data from training set")
    print("="*60)
    
    # Get some safe students (Pass/Distinction)
    safe_students = df[df['is_at_risk'] == 0].head(3)
    print("\n📗 Safe Students (should predict class=0):")
    for idx, row in safe_students.iterrows():
        features = row[FEATURE_COLUMNS].values.reshape(1, -1)
        pred = model.predict(features)[0]
        proba = model.predict_proba(features)[0]
        print(f"\nStudent {row['id_student']}:")
        print(f"  avg_grade: {row['avg_grade']:.1f}, studied_credits: {row['studied_credits']}")
        print(f"  actual: {int(row['is_at_risk'])} (Safe)")
        print(f"  predicted: {int(pred)} (proba: {proba})")
    
    # Get some at-risk students
    at_risk_students = df[df['is_at_risk'] == 1].head(3)
    print("\n📕 At-Risk Students (should predict class=1):")
    for idx, row in at_risk_students.iterrows():
        features = row[FEATURE_COLUMNS].values.reshape(1, -1)
        pred = model.predict(features)[0]
        proba = model.predict_proba(features)[0]
        print(f"\nStudent {row['id_student']}:")
        print(f"  avg_grade: {row['avg_grade']:.1f}, studied_credits: {row['studied_credits']}")
        print(f"  actual: {int(row['is_at_risk'])} (At-Risk)")
        print(f"  predicted: {int(pred)} (proba: {proba})")
    
    # Test with synthetic extreme cases
    print("\n" + "="*60)
    print("Testing with SYNTHETIC extreme cases")
    print("="*60)
    
    perfect_student = pd.DataFrame([{
        'avg_grade': 95.0,
        'grade_consistency': 2.0,
        'grade_range': 5.0,
        'num_assessments': 10,
        'assessment_completion_rate': 1.0,
        'studied_credits': 180,
        'num_of_prev_attempts': 0,
        'low_performance': 0,
        'low_engagement': 0,
        'has_previous_attempts': 0,
    }])
    
    failing_student = pd.DataFrame([{
        'avg_grade': 10.0,
        'grade_consistency': 50.0,
        'grade_range': 20.0,
        'num_assessments': 1,
        'assessment_completion_rate': 0.1,
        'studied_credits': 30,
        'num_of_prev_attempts': 5,
        'low_performance': 1,
        'low_engagement': 1,
        'has_previous_attempts': 1,
    }])
    
    print("\n📘 Perfect Student:")
    pred = model.predict(perfect_student)[0]
    proba = model.predict_proba(perfect_student)[0]
    print(f"  Predicted: {int(pred)} (proba: {proba})")
    
    print("\n📙 Failing Student:")
    pred = model.predict(failing_student)[0]
    proba = model.predict_proba(failing_student)[0]
    print(f"  Predicted: {int(pred)} (proba: {proba})")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
