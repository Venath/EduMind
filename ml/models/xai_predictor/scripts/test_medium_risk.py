"""
Test Medium Risk Profile
=========================
Quick test to demonstrate medium-risk prediction (50-79% at-risk probability).
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from src.models.predictor import RiskPredictor, create_student_features


def test_medium_risk_profile():
    """Test a student with borderline characteristics."""
    print("\n" + "="*60)
    print("Testing Medium Risk Profile")
    print("="*60)
    
    predictor = RiskPredictor()
    max_assessments = predictor.max_assessments
    
    # MEDIUM RISK PROFILE - Borderline student
    medium_risk_student = create_student_features(
        avg_grade=58.0,              # Borderline passing (just above 55)
        score_std=20.0,              # Inconsistent (grade_consistency = 80)
        grade_range=35.0,            # High variance
        num_assessments=5,           # Below average engagement
        studied_credits=60,          # Moderate credit load
        num_of_prev_attempts=1,      # One previous attempt (warning sign)
        low_performance=0,           # Not flagged as low (>40)
        low_engagement=0,            # Not critically low
        max_assessments=max_assessments,
    )
    
    print("\nMedium Risk Student Profile:")
    print("  Raw Input Values:")
    print(f"    avg_grade: 58.0 (borderline passing)")
    print(f"    score_std: 20.0 (inconsistent)")
    print(f"    num_assessments: 5 (below average)")
    print(f"    studied_credits: 60 (moderate)")
    print(f"    num_of_prev_attempts: 1 (one failed attempt)")
    
    print("\n  Calculated Features:")
    for feature, value in medium_risk_student.items():
        print(f"    {feature}: {value}")
    
    result = predictor.predict(medium_risk_student)
    
    print("\n" + "-"*60)
    print("Prediction Result:")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Predicted Class: {result['prediction']['label']}")
    print(f"  Is At-Risk: {result['prediction']['is_at_risk']}")
    print(f"  At-Risk Probability: {result['probability']['at_risk']:.2%}")
    print(f"  Safe Probability: {result['probability']['safe']:.2%}")
    print(f"  Confidence: {result['confidence']:.2%}")
    
    # Explain the result
    print("\n" + "-"*60)
    print("Interpretation:")
    if result['risk_level'] == 'medium':
        print("✓ This student shows MEDIUM RISK characteristics:")
        print("  - Borderline grades that could go either way")
        print("  - Below-average engagement but not critically low")
        print("  - Has one previous failed attempt (concerning)")
        print("  - Inconsistent performance (high variance)")
        print("\n  Recommendation: Proactive intervention recommended")
        print("  This student needs support to avoid falling into high risk.")
    elif result['risk_level'] == 'high':
        print("⚠ Actually predicted as HIGH RISK")
        print("  The combination of factors pushed this to high risk.")
    else:
        print("✓ Actually predicted as LOW RISK")
        print("  The model is more optimistic about this profile.")


if __name__ == "__main__":
    try:
        test_medium_risk_profile()
        print("\n" + "="*60)
        print("✓ Test completed!")
        print("="*60 + "\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
