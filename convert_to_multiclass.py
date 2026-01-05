#!/usr/bin/env python3
"""
Convert existing processed data to 3-tier classification
"""
import pandas as pd
import numpy as np
from pathlib import Path

# Paths
BASE_DIR = Path("/Users/ravinbandara/Desktop/Ravin/EduMind")
INPUT_FILE = BASE_DIR / "ml" / "models" / "xai_predictor" / "data" / "oulad_processed.csv"
OUTPUT_FILE = BASE_DIR / "ml" / "models" / "xai_predictor" / "data" / "oulad_processed_multiclass.csv"

def create_risk_category(row) -> int:
    """
    Create BALANCED 3-tier risk category.
    Returns: 0=Safe, 1=Medium Risk, 2=At-Risk
    Target: ~33% each class for balanced training
    """
    risk_score = 0
    
    # Grade-based risk (35% weight)
    avg_grade = row.get("avg_grade", 0)
    if avg_grade < 40:
        risk_score += 6
    elif avg_grade < 55:
        risk_score += 4
    elif avg_grade < 70:
        risk_score += 2
    elif avg_grade >= 80:
        risk_score -= 1
    
    # Assessment engagement (30% weight)
    num_assessments = row.get("num_assessments", 0)
    if num_assessments < 3:
        risk_score += 5
    elif num_assessments < 5:
        risk_score += 3
    elif num_assessments < 7:
        risk_score += 1
    elif num_assessments >= 9:
        risk_score -= 1
    
    # Completion rate (20% weight)
    completion = row.get("assessment_completion_rate", 0)
    if completion < 0.3:
        risk_score += 3
    elif completion < 0.6:
        risk_score += 1.5
    elif completion >= 0.85:
        risk_score -= 1
    
    # Previous attempts (10% weight)
    prev_attempts = row.get("num_of_prev_attempts", 0)
    if prev_attempts > 2:
        risk_score += 2
    elif prev_attempts == 1:
        risk_score += 1
    
    # Grade consistency (5% weight)
    grade_consistency = row.get("grade_consistency", 100)
    if grade_consistency < 70:
        risk_score += 1
    elif grade_consistency >= 90:
        risk_score -= 0.5
    
    # Check if actually failed
    is_at_risk = row.get("is_at_risk", 0)
    if is_at_risk == 1:
        risk_score += 3
    
    # BALANCED thresholds for ~33% distribution
    if risk_score >= 8:
        return 2  # At-Risk (critical intervention needed)
    elif risk_score >= 4:
        return 1  # Medium Risk (monitoring + support needed)
    else:
        return 0  # Safe (on track)


print("Loading processed data...")
df = pd.read_csv(INPUT_FILE)
print(f"✓ Loaded {len(df):,} records")

print("\nCreating 3-tier risk categories...")
df["risk_category"] = df.apply(create_risk_category, axis=1)

# Print distribution
print(f"\n📊 Risk Category Distribution:")
category_counts = df["risk_category"].value_counts().sort_index()
print(f"  Safe (0):        {category_counts.get(0, 0):,} ({category_counts.get(0, 0) / len(df) * 100:.1f}%)")
print(f"  Medium Risk (1): {category_counts.get(1, 0):,} ({category_counts.get(1, 0) / len(df) * 100:.1f}%)")
print(f"  At-Risk (2):     {category_counts.get(2, 0):,} ({category_counts.get(2, 0) / len(df) * 100:.1f}%)")

# Sample from each category
print("\n📋 Sample Records by Category:")
for cat in [0, 1, 2]:
    cat_name = ["Safe", "Medium Risk", "At-Risk"][cat]
    sample = df[df["risk_category"] == cat].head(1)
    if len(sample) > 0:
        print(f"\n{cat_name} Example:")
        print(f"  avg_grade: {sample.iloc[0]['avg_grade']:.1f}")
        print(f"  grade_consistency: {sample.iloc[0]['grade_consistency']:.1f}")
        print(f"  num_assessments: {sample.iloc[0]['num_assessments']}")
        print(f"  completion_rate: {sample.iloc[0]['assessment_completion_rate']:.2f}")
        print(f"  prev_attempts: {sample.iloc[0]['num_of_prev_attempts']}")

# Save
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False)
print(f"\n✓ Saved to: {OUTPUT_FILE}")
