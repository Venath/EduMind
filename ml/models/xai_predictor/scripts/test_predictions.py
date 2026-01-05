"""
Test Predictions Script
=======================
Interactive script to test the trained model with sample data.

This script demonstrates the proper way to format features for predictions.
Use the create_student_features() helper function for correct feature formatting.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from src.models.predictor import RiskPredictor, create_student_features
from config.settings import FEATURE_COLUMNS


def test_single_prediction():
    """Test prediction for a single student."""
    print("\n" + "="*60)
    print("Testing Single Student Prediction")
    print("="*60)
    
    # Initialize predictor
    predictor = RiskPredictor()
    max_assessments = predictor.max_assessments
    
    # Sample student data - HIGH RISK PROFILE
    # Using create_student_features helper for proper formatting
    high_risk_student = create_student_features(
        avg_grade=25.0,              # Very low grades
        score_std=30.0,              # High variance (grade_consistency will be 70)
        grade_range=50.0,
        num_assessments=2,           # Few assessments
        studied_credits=60,
        num_of_prev_attempts=3,
        low_performance=1,
        low_engagement=1,
        max_assessments=max_assessments,
    )
    
    print("\nHigh Risk Student Profile:")
    for feature, value in high_risk_student.items():
        print(f"  {feature}: {value}")
    
    result = predictor.predict(high_risk_student)
    print(f"\nPrediction Result:")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Predicted Class: {result['prediction']['label']}")
    print(f"  Is At-Risk: {result['prediction']['is_at_risk']}")
    print(f"  At-Risk Probability: {result['probability']['at_risk']:.2%}")
    print(f"  Safe Probability: {result['probability']['safe']:.2%}")
    print(f"  Confidence: {result['confidence']:.2%}")
    
    # Sample student data - LOW RISK PROFILE
    print("\n" + "-"*60)
    
    low_risk_student = create_student_features(
        avg_grade=82.0,              # High grades
        score_std=5.0,               # Low variance (grade_consistency will be 95)
        grade_range=12.0,
        num_assessments=12,          # Many assessments
        studied_credits=90,
        num_of_prev_attempts=0,
        low_performance=0,
        low_engagement=0,
        max_assessments=max_assessments,
    )
    
    print("\nLow Risk Student Profile:")
    for feature, value in low_risk_student.items():
        print(f"  {feature}: {value}")
    
    result = predictor.predict(low_risk_student)
    print(f"\nPrediction Result:")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Predicted Class: {result['prediction']['label']}")
    print(f"  Is At-Risk: {result['prediction']['is_at_risk']}")
    print(f"  At-Risk Probability: {result['probability']['at_risk']:.2%}")
    print(f"  Safe Probability: {result['probability']['safe']:.2%}")
    print(f"  Confidence: {result['confidence']:.2%}")


def test_batch_predictions():
    """Test predictions for multiple students."""
    print("\n" + "="*60)
    print("Testing Batch Predictions")
    print("="*60)
    
    # Initialize predictor
    predictor = RiskPredictor()
    max_assessments = predictor.max_assessments
    
    # Multiple students with properly formatted features
    students = [
        create_student_features(  # Student 1 - Moderate Risk
            avg_grade=55.0,
            score_std=18.0,          # grade_consistency = 82
            grade_range=30.0,
            num_assessments=5,
            studied_credits=60,
            num_of_prev_attempts=1,
            low_performance=0,
            low_engagement=0,
            max_assessments=max_assessments,
        ),
        create_student_features(  # Student 2 - High Performer
            avg_grade=85.0,
            score_std=6.0,           # grade_consistency = 94
            grade_range=15.0,
            num_assessments=12,
            studied_credits=90,
            num_of_prev_attempts=0,
            low_performance=0,
            low_engagement=0,
            max_assessments=max_assessments,
        ),
        create_student_features(  # Student 3 - Struggling
            avg_grade=15.0,
            score_std=35.0,          # grade_consistency = 65
            grade_range=30.0,
            num_assessments=1,
            studied_credits=30,
            num_of_prev_attempts=2,
            low_performance=1,
            low_engagement=1,
            max_assessments=max_assessments,
        ),
    ]
    
    results = predictor.predict(students)
    
    print(f"\nPredictions for {len(students)} students:")
    for i, result in enumerate(results, 1):
        print(f"\nStudent {i}:")
        print(f"  Risk Level: {result['risk_level']}")
        print(f"  Predicted Class: {result['prediction']['label']}")
        print(f"  Is At-Risk: {result['prediction']['is_at_risk']}")
        print(f"  At-Risk Probability: {result['probability']['at_risk']:.2%}")
        print(f"  Confidence: {result['confidence']:.2%}")


def test_custom_prediction():
    """Interactive custom prediction."""
    print("\n" + "="*60)
    print("Custom Student Prediction")
    print("="*60)
    print("\nEnter student data (or press Enter to skip):")
    
    student_data = {}
    
    # Get max_assessments from predictor
    predictor = RiskPredictor()
    max_assessments = predictor.max_assessments
    
    # Simple defaults for quick testing
    defaults = {
        'avg_grade': 70.0,
        'score_std': 12.0,           # Will become grade_consistency = 88
        'grade_range': 25.0,
        'num_assessments': 6,
        'studied_credits': 90,
        'num_of_prev_attempts': 0,
    }
    
    print("\n(Press Enter to use default values)")
    print("Enter raw values (score_std, num_assessments will be auto-converted):")
    
    # Collect inputs
    inputs = {}
    for key, default_val in defaults.items():
        user_input = input(f"{key} [{default_val}]: ").strip()
        inputs[key] = float(user_input) if user_input else default_val
    
    # Create properly formatted features
    student_data = create_student_features(
        avg_grade=inputs['avg_grade'],
        score_std=inputs['score_std'],
        grade_range=inputs['grade_range'],
        num_assessments=int(inputs['num_assessments']),
        studied_credits=int(inputs['studied_credits']),
        num_of_prev_attempts=int(inputs['num_of_prev_attempts']),
        max_assessments=max_assessments,
    )
    
    # Make prediction
    result = predictor.predict(student_data)
    print("\n" + "-"*60)
    print("Prediction Result:")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Predicted Class: {result['prediction']['label']}")
    print(f"  Is At-Risk: {result['prediction']['is_at_risk']}")
    print(f"  At-Risk Probability: {result['probability']['at_risk']:.2%}")
    print(f"  Safe Probability: {result['probability']['safe']:.2%}")
    print(f"  Confidence: {result['confidence']:.2%}")


def main():
    """Run all prediction tests."""
    print("\n" + "="*60)
    print("XAI Predictor - Testing Predictions")
    print("="*60)
    
    try:
        # Test 1: Single predictions
        test_single_prediction()
        
        # Test 2: Batch predictions
        test_batch_predictions()
        
        # Test 3: Custom prediction (optional)
        print("\n" + "="*60)
        response = input("\nWould you like to test a custom prediction? (y/n): ").strip().lower()
        if response == 'y':
            test_custom_prediction()
        
        print("\n" + "="*60)
        print("✓ All tests completed successfully!")
        print("="*60 + "\n")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease train the model first:")
        print("  python -m scripts.run_pipeline --step train")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
