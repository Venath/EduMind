"""
Test Personalized Recommendations
===================================
Demonstrates the recommendation engine with different student profiles.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from src.models.predictor import RiskPredictor, create_student_features


def test_high_risk_recommendations():
    """Test recommendations for a high-risk student."""
    print("\n" + "="*70)
    print("HIGH RISK STUDENT - Comprehensive Intervention Plan")
    print("="*70)
    
    predictor = RiskPredictor()
    max_assessments = predictor.max_assessments
    
    # High-risk profile: Poor grades, low engagement, multiple attempts
    student = create_student_features(
        avg_grade=32.0,              # Failing
        score_std=35.0,              # Very inconsistent (consistency = 65)
        grade_range=45.0,
        num_assessments=1,           # Critically low
        studied_credits=30,          # Very low load
        num_of_prev_attempts=2,      # Multiple failed attempts
        low_performance=1,
        low_engagement=1,
        max_assessments=max_assessments,
    )
    
    print("\nStudent Profile:")
    print(f"  Average Grade: 32% (FAILING)")
    print(f"  Grade Consistency: 65 (very inconsistent)")
    print(f"  Assessments Completed: 1 out of {int(max_assessments)}")
    print(f"  Enrolled Credits: 30 (part-time)")
    print(f"  Previous Attempts: 2")
    
    # Get prediction with recommendations
    result = predictor.predict_with_recommendations(student)
    
    # Display prediction
    pred = result['prediction']
    print(f"\n📊 PREDICTION:")
    print(f"  Risk Level: {pred['risk_level'].upper()}")
    print(f"  At-Risk Probability: {pred['probability']['at_risk']:.1%}")
    print(f"  Confidence: {pred['confidence']:.1%}")
    
    # Display recommendations
    print(f"\n{result['plan_text']}")


def test_medium_risk_recommendations():
    """Test recommendations for a medium-risk student."""
    print("\n" + "="*70)
    print("MEDIUM RISK STUDENT - Proactive Intervention Plan")
    print("="*70)
    
    predictor = RiskPredictor()
    max_assessments = predictor.max_assessments
    
    # Medium-risk profile: Borderline performance
    student = create_student_features(
        avg_grade=58.0,              # Borderline passing
        score_std=18.0,              # Inconsistent (consistency = 82)
        grade_range=32.0,
        num_assessments=5,           # Below average
        studied_credits=60,          # Moderate load
        num_of_prev_attempts=1,      # One previous attempt
        low_performance=0,
        low_engagement=0,
        max_assessments=max_assessments,
    )
    
    print("\nStudent Profile:")
    print(f"  Average Grade: 58% (borderline)")
    print(f"  Grade Consistency: 82 (inconsistent)")
    print(f"  Assessments Completed: 5 out of {int(max_assessments)}")
    print(f"  Enrolled Credits: 60")
    print(f"  Previous Attempts: 1")
    
    # Get prediction with recommendations
    result = predictor.predict_with_recommendations(student)
    
    # Display prediction
    pred = result['prediction']
    print(f"\n📊 PREDICTION:")
    print(f"  Risk Level: {pred['risk_level'].upper()}")
    print(f"  At-Risk Probability: {pred['probability']['at_risk']:.1%}")
    print(f"  Confidence: {pred['confidence']:.1%}")
    
    # Display recommendations
    print(f"\n{result['plan_text']}")


def test_low_risk_recommendations():
    """Test recommendations for a low-risk (safe) student."""
    print("\n" + "="*70)
    print("LOW RISK STUDENT - Maintenance & Growth Plan")
    print("="*70)
    
    predictor = RiskPredictor()
    max_assessments = predictor.max_assessments
    
    # Low-risk profile: Strong performance
    student = create_student_features(
        avg_grade=85.0,              # Strong grades
        score_std=4.0,               # Very consistent (consistency = 96)
        grade_range=10.0,
        num_assessments=14,          # High engagement
        studied_credits=90,          # Full-time
        num_of_prev_attempts=0,      # First attempt
        low_performance=0,
        low_engagement=0,
        max_assessments=max_assessments,
    )
    
    print("\nStudent Profile:")
    print(f"  Average Grade: 85% (strong)")
    print(f"  Grade Consistency: 96 (very consistent)")
    print(f"  Assessments Completed: 14 out of {int(max_assessments)}")
    print(f"  Enrolled Credits: 90 (full-time)")
    print(f"  Previous Attempts: 0 (first attempt)")
    
    # Get prediction with recommendations
    result = predictor.predict_with_recommendations(student)
    
    # Display prediction
    pred = result['prediction']
    print(f"\n📊 PREDICTION:")
    print(f"  Risk Level: {pred['risk_level'].upper()}")
    print(f"  At-Risk Probability: {pred['probability']['at_risk']:.1%}")
    print(f"  Confidence: {pred['confidence']:.1%}")
    
    # Display recommendations
    print(f"\n{result['plan_text']}")


def test_custom_student():
    """Interactive test with custom student data."""
    print("\n" + "="*70)
    print("CUSTOM STUDENT - Personalized Plan")
    print("="*70)
    
    predictor = RiskPredictor()
    max_assessments = predictor.max_assessments
    
    print("\nEnter student data (press Enter for defaults):")
    
    defaults = {
        'avg_grade': 65.0,
        'score_std': 15.0,
        'grade_range': 28.0,
        'num_assessments': 7,
        'studied_credits': 75,
        'num_of_prev_attempts': 0,
    }
    
    inputs = {}
    for key, default_val in defaults.items():
        user_input = input(f"  {key} [{default_val}]: ").strip()
        inputs[key] = float(user_input) if user_input else default_val
    
    student = create_student_features(
        avg_grade=inputs['avg_grade'],
        score_std=inputs['score_std'],
        grade_range=inputs['grade_range'],
        num_assessments=int(inputs['num_assessments']),
        studied_credits=int(inputs['studied_credits']),
        num_of_prev_attempts=int(inputs['num_of_prev_attempts']),
        max_assessments=max_assessments,
    )
    
    # Get prediction with recommendations
    result = predictor.predict_with_recommendations(student)
    
    # Display prediction
    pred = result['prediction']
    print(f"\n📊 PREDICTION:")
    print(f"  Risk Level: {pred['risk_level'].upper()}")
    print(f"  At-Risk Probability: {pred['probability']['at_risk']:.1%}")
    print(f"  Confidence: {pred['confidence']:.1%}")
    
    # Display recommendations
    print(f"\n{result['plan_text']}")


def main():
    """Run all recommendation tests."""
    print("\n" + "="*70)
    print("PERSONALIZED RECOMMENDATION ENGINE - DEMO")
    print("="*70)
    print("\nThis demonstrates how the system generates personalized")
    print("intervention plans based on student risk profiles.")
    
    try:
        # Test 1: High-risk student
        test_high_risk_recommendations()
        input("\n\nPress Enter to continue to medium-risk example...")
        
        # Test 2: Medium-risk student
        test_medium_risk_recommendations()
        input("\n\nPress Enter to continue to low-risk example...")
        
        # Test 3: Low-risk student
        test_low_risk_recommendations()
        
        # Test 4: Custom student (optional)
        print("\n" + "="*70)
        response = input("\nWould you like to test with custom student data? (y/n): ").strip().lower()
        if response == 'y':
            test_custom_student()
        
        print("\n" + "="*70)
        print("✓ All recommendation tests completed!")
        print("="*70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
