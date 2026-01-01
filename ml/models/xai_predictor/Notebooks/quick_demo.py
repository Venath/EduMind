# Quick Demo: OULAD Academic Risk Prediction
# Run this in your Jupyter notebook to see the complete system in action

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import shap
import xgboost as xgb
from sklearn.metrics import (classification_report, confusion_matrix,
                             roc_auc_score)
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight

# Set display options
pd.set_option("display.max_columns", None)
plt.style.use("seaborn-v0_8-darkgrid")

print("=" * 70)
print("OULAD ACADEMIC RISK PREDICTION - QUICK DEMO")
print("=" * 70)

# ============================================================
# STEP 1: LOAD DATA
# ============================================================
print("\n📂 STEP 1: Loading OULAD processed data...")

INPUT_FILE = "/Users/ravinbandara/Desktop/Ravin/EduMind/ml/models/xai_predictor/data/oulad_processed.csv"
df = pd.read_csv(INPUT_FILE)

print(f"✓ Loaded {len(df):,} students")
print(f"✓ Safe: {sum(df['is_at_risk']==0):,} | At-Risk: {sum(df['is_at_risk']==1):,}")

# ============================================================
# STEP 2: PREPARE FEATURES
# ============================================================
print("\n🔧 STEP 2: Preparing academic features...")

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

print(f"✓ {len(feature_cols)} academic features selected")

# ============================================================
# STEP 3: TRAIN-TEST SPLIT
# ============================================================
print("\n✂️ STEP 3: Splitting data...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"✓ Training: {len(X_train):,} | Testing: {len(X_test):,}")

# ============================================================
# STEP 4: TRAIN MODEL
# ============================================================
print("\n🤖 STEP 4: Training XGBoost model...")

# Compute class weights
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
)

model.fit(X_train, y_train, sample_weight=sample_weights, verbose=False)
print("✓ Model trained successfully!")

# ============================================================
# STEP 5: EVALUATE MODEL
# ============================================================
print("\n📊 STEP 5: Evaluating model performance...")

y_pred = model.predict(X_test)
y_pred_proba = model.predict_proba(X_test)[:, 1]

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["Safe", "At-Risk"]))

roc_auc = roc_auc_score(y_test, y_pred_proba)
print(f"ROC-AUC Score: {roc_auc:.3f}")

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=["Safe", "At-Risk"],
    yticklabels=["Safe", "At-Risk"],
)
plt.title("Confusion Matrix", fontsize=14, fontweight="bold")
plt.ylabel("Actual")
plt.xlabel("Predicted")
plt.tight_layout()
plt.show()

# ============================================================
# STEP 6: SHAP ANALYSIS (SAMPLE)
# ============================================================
print("\n🔍 STEP 6: Calculating SHAP values (sample of 1000 students)...")

# Use sample for faster computation
sample_size = 1000
X_test_sample = X_test.iloc[:sample_size]
y_test_sample = y_test.iloc[:sample_size]

explainer = shap.Explainer(model, X_train.sample(100))
shap_values = explainer(X_test_sample)

print("✓ SHAP analysis complete!")

# SHAP Summary Plot
plt.figure(figsize=(10, 6))
shap.summary_plot(shap_values, X_test_sample, feature_names=feature_cols, show=False)
plt.title("SHAP Feature Importance", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.show()

# ============================================================
# STEP 7: PERSONALIZED RECOMMENDATIONS
# ============================================================
print("\n💡 STEP 7: Generating personalized recommendations...")


def show_student_guidance(student_idx):
    """Show personalized guidance for a student"""
    student_features = X_test_sample.iloc[[student_idx]]
    student_values = X_test_sample.iloc[student_idx]
    predicted_risk = model.predict(student_features)[0]
    probabilities = model.predict_proba(student_features)[0]
    student_shap = shap_values.values[student_idx]

    risk_name = "At-Risk" if predicted_risk == 1 else "Safe"

    print("\n" + "=" * 70)
    print(f"STUDENT #{student_idx} - {risk_name}")
    print("=" * 70)
    print(f"Confidence: Safe={probabilities[0]:.1%} | At-Risk={probabilities[1]:.1%}")

    print("\n🔍 Top Risk Factors:")
    feature_impact = list(zip(feature_cols, student_shap, student_values))
    feature_impact.sort(key=lambda x: abs(x[1]), reverse=True)

    for i, (feature, shap_val, value) in enumerate(feature_impact[:3], 1):
        direction = "⬆" if shap_val > 0 else "⬇"
        print(f"  {i}. {feature}: {value:.2f} {direction}")

    print("\n💡 Recommendations:")
    if predicted_risk == 1:
        print("  🚨 INTERVENTION NEEDED:")
        if student_values["avg_grade"] < 50:
            print(
                f"    • Low grade ({student_values['avg_grade']:.1f}%) - Seek tutoring"
            )
        if student_values["num_assessments"] < 5:
            print(
                f"    • Only {student_values['num_assessments']:.0f} assessments - Complete all work"
            )
        if student_values["has_previous_attempts"] == 1:
            print("    • Previous failures - Address knowledge gaps")
        print("    • Contact academic advisor immediately")
    else:
        print("  ✅ KEEP UP THE GOOD WORK:")
        print(f"    • Current grade: {student_values['avg_grade']:.1f}%")
        print("    • Maintain consistent performance")
        print("    • Help struggling peers")


# Show examples
print("\n" + "=" * 70)
print("EXAMPLE STUDENTS")
print("=" * 70)

# Find one at-risk and one safe student
at_risk_idx = [i for i, pred in enumerate(model.predict(X_test_sample)) if pred == 1][0]
safe_idx = [i for i, pred in enumerate(model.predict(X_test_sample)) if pred == 0][0]

show_student_guidance(at_risk_idx)
show_student_guidance(safe_idx)

print("\n" + "=" * 70)
print("✅ DEMO COMPLETE!")
print("=" * 70)
print(f"\nModel trained on {len(X_train):,} students")
print(f"Tested on {len(X_test):,} students")
print(f"Accuracy: {(y_pred == y_test).mean()*100:.1f}%")
print(f"ROC-AUC: {roc_auc:.3f}")
print("\n🎯 System ready to predict student dropout risk and provide guidance!")
