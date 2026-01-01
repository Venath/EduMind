# %% ETL for OULAD Dataset - Academic Risk Prediction
import os

import numpy as np
import pandas as pd

print("=" * 60)
print("OULAD DATASET - ACADEMIC PERFORMANCE ETL")
print("=" * 60)

# Data directory
DATA_DIR = "/Users/ravinbandara/Desktop/Ravin/EduMind/ml/models/xai_predictor/data"

# Load OULAD datasets
print("\nLoading OULAD datasets...")
student_info = pd.read_csv(f"{DATA_DIR}/studentInfo.csv")
student_assessment = pd.read_csv(f"{DATA_DIR}/studentAssessment.csv")
assessments = pd.read_csv(f"{DATA_DIR}/assessments.csv")

print(f"✓ Student Info: {len(student_info):,} records")
print(f"✓ Student Assessments: {len(student_assessment):,} records")
print(f"✓ Assessment Details: {len(assessments):,} records")

print("\n" + "=" * 60)
print("FEATURE ENGINEERING")
print("=" * 60)

# Calculate academic performance metrics per student
print("\n1. Calculating assessment scores...")

# First merge student_assessment with student_info to get module/presentation
assessment_data = student_assessment.merge(
    student_info[["id_student", "code_module", "code_presentation"]],
    on="id_student",
    how="left",
)

# Then merge with assessment details
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
    "id_student",
    "code_module",
    "code_presentation",
    "avg_score",
    "score_std",
    "num_assessments",
    "min_score",
    "max_score",
    "last_submission",
]

print(f"✓ Calculated metrics for {len(student_metrics):,} student-course combinations")

# Merge with student info
print("\n2. Merging with student information...")
df = student_info.merge(
    student_metrics, on=["id_student", "code_module", "code_presentation"], how="left"
)

# Fill missing assessment data (students who didn't submit any assessments)
df["avg_score"] = df["avg_score"].fillna(0)
df["score_std"] = df["score_std"].fillna(0)
df["num_assessments"] = df["num_assessments"].fillna(0)
df["min_score"] = df["min_score"].fillna(0)
df["max_score"] = df["max_score"].fillna(0)

print(f"✓ Combined dataset: {len(df):,} students")

# === ACADEMIC PERFORMANCE FEATURES ===
print("\n3. Engineering academic performance features...")

# Grade-related features
df["avg_grade"] = df["avg_score"]  # Average assessment score (0-100)
df["grade_consistency"] = 100 - df["score_std"].fillna(0)  # Lower std = more consistent
df["grade_range"] = df["max_score"] - df["min_score"]  # Performance variability
df["low_performance"] = (df["avg_score"] < 40).astype(int)  # Below 40% is poor

# Attendance proxy (number of assessments submitted)
df["assessment_completion_rate"] = df["num_assessments"] / df["num_assessments"].max()
df["low_engagement"] = (df["num_assessments"] < df["num_assessments"].median()).astype(
    int
)

# Study credits as workload indicator
df["high_credits"] = (df["studied_credits"] > df["studied_credits"].median()).astype(
    int
)

# Previous attempts (failures)
df["has_previous_attempts"] = (df["num_of_prev_attempts"] > 0).astype(int)

# === BINARY RISK ASSIGNMENT ===
print("\n4. Assigning risk levels...")


def assign_academic_risk(row):
    """
    Binary classification based on final_result
    At-Risk (1): Fail or Withdrawn
    Safe (0): Pass or Distinction
    """
    if row["final_result"] in ["Fail", "Withdrawn"]:
        return 1  # At-Risk
    else:
        return 0  # Safe (Pass or Distinction)


df["is_at_risk"] = df.apply(assign_academic_risk, axis=1)

# === SELECT FEATURES (ACADEMIC ONLY) ===
feature_cols = [
    "avg_grade",  # Average assessment score
    "grade_consistency",  # Performance consistency
    "grade_range",  # Score variability
    "num_assessments",  # Number of assessments completed
    "assessment_completion_rate",  # Completion rate
    "studied_credits",  # Course credits
    "num_of_prev_attempts",  # Previous failures
    "low_performance",  # Binary: low grades
    "low_engagement",  # Binary: low assessment completion
    "has_previous_attempts",  # Binary: has failed before
]

# Filter out students with missing critical data
df_clean = df[df["final_result"].notna()].copy()

print(f"✓ Clean dataset: {len(df_clean):,} students with complete data")

# === SAVE PROCESSED DATA ===
output_cols = (
    [
        "id_student",
        "code_module",
        "code_presentation",
        "gender",
        "region",
        "highest_education",
        "age_band",
        "final_result",
    ]
    + feature_cols
    + ["is_at_risk"]
)

output_df = df_clean[output_cols]
output_path = f"{DATA_DIR}/oulad_processed.csv"
output_df.to_csv(output_path, index=False)

print("\n" + "=" * 60)
print("PROCESSED DATA SUMMARY")
print("=" * 60)
print(f"Total students: {len(output_df):,}")
print(
    f"Safe students (Pass/Distinction): {sum(output_df['is_at_risk']==0):,} ({sum(output_df['is_at_risk']==0)/len(output_df)*100:.1f}%)"
)
print(
    f"At-risk students (Fail/Withdrawn): {sum(output_df['is_at_risk']==1):,} ({sum(output_df['is_at_risk']==1)/len(output_df)*100:.1f}%)"
)

print(f"\nBy final result:")
result_dist = output_df.groupby("final_result").size().sort_values(ascending=False)
for result, count in result_dist.items():
    print(f"  {result}: {count:,} ({count/len(output_df)*100:.1f}%)")

print(f"\nFeatures ({len(feature_cols)}):")
for i, col in enumerate(feature_cols, 1):
    print(f"  {i:2d}. {col}")

print(f"\nFeature statistics:")
print(output_df[feature_cols].describe().round(2))

print(f"\nData saved to: {output_path}")
print(f"\nReady for model training with {len(output_df):,} students!")
