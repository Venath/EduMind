"""
Interactive Student Assessment System
======================================
Complete workflow: Test predictions → Custom student → Get recommendations

This script provides a full interactive experience:
1. View sample predictions (high/medium/low risk)
2. Test custom student prediction
3. Generate personalized intervention plan
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from src.models.predictor import RiskPredictor, create_student_features


def show_sample_predictions(predictor, max_assessments):
    """Show predictions for sample high, medium, and low risk students."""
    print("\n" + "="*70)
    print("SAMPLE PREDICTIONS - Understanding Risk Levels")
    print("="*70)
    
    samples = [
        {
            'name': 'High Risk Student',
            'icon': '🚨',
            'profile': create_student_features(
                avg_grade=25.0,
                score_std=30.0,
                grade_range=50.0,
                num_assessments=2,
                studied_credits=60,
                num_of_prev_attempts=3,
                low_performance=1,
                low_engagement=1,
                max_assessments=max_assessments,
            ),
            'description': 'Very low grades (25%), minimal engagement (2 assessments), 3 previous attempts'
        },
        {
            'name': 'Medium Risk Student',
            'icon': '⚠️',
            'profile': create_student_features(
                avg_grade=58.0,
                score_std=18.0,
                grade_range=32.0,
                num_assessments=5,
                studied_credits=60,
                num_of_prev_attempts=1,
                low_performance=0,
                low_engagement=0,
                max_assessments=max_assessments,
            ),
            'description': 'Borderline grades (58%), below-average engagement (5 assessments), 1 previous attempt'
        },
        {
            'name': 'Low Risk Student',
            'icon': '✅',
            'profile': create_student_features(
                avg_grade=82.0,
                score_std=5.0,
                grade_range=12.0,
                num_assessments=12,
                studied_credits=90,
                num_of_prev_attempts=0,
                low_performance=0,
                low_engagement=0,
                max_assessments=max_assessments,
            ),
            'description': 'High grades (82%), good engagement (12 assessments), first attempt'
        },
    ]
    
    for sample in samples:
        print(f"\n{'-'*70}")
        print(f"{sample['icon']} {sample['name']}")
        print(f"{'-'*70}")
        print(f"Profile: {sample['description']}")
        
        result = predictor.predict(sample['profile'])
        
        print(f"\nPrediction:")
        print(f"  Risk Level: {result['risk_level'].upper()}")
        print(f"  At-Risk Probability: {result['probability']['at_risk']:.1%}")
        print(f"  Confidence: {result['confidence']:.1%}")


def get_custom_student_input(max_assessments):
    """Interactive input for custom student data."""
    print("\n" + "="*70)
    print("CUSTOM STUDENT ASSESSMENT")
    print("="*70)
    print("\nEnter student information (press Enter for default values):")
    print("Tip: Use realistic values based on the samples above\n")
    
    defaults = {
        'avg_grade': 70.0,
        'score_std': 12.0,
        'grade_range': 25.0,
        'num_assessments': 6,
        'studied_credits': 90,
        'num_of_prev_attempts': 0,
    }
    
    descriptions = {
        'avg_grade': 'Average grade percentage (0-100)',
        'score_std': 'Grade standard deviation - lower = more consistent (0-40)',
        'grade_range': 'Range between highest and lowest grades (0-100)',
        'num_assessments': f'Number of assessments completed (0-{int(max_assessments)})',
        'studied_credits': 'Total credits enrolled (30-120)',
        'num_of_prev_attempts': 'Number of previous failed attempts (0-5)',
    }
    
    inputs = {}
    for key, default_val in defaults.items():
        desc = descriptions[key]
        print(f"\n{desc}")
        user_input = input(f"  {key} [{default_val}]: ").strip()
        inputs[key] = float(user_input) if user_input else default_val
    
    return inputs


def show_prediction(predictor, student_features):
    """Display prediction results."""
    print("\n" + "="*70)
    print("PREDICTION RESULTS")
    print("="*70)
    
    result = predictor.predict(student_features)
    
    # Risk level with visual indicator
    risk_icons = {
        'high': '🚨',
        'medium': '⚠️',
        'low': '✅'
    }
    icon = risk_icons.get(result['risk_level'], '📊')
    
    print(f"\n{icon} Risk Level: {result['risk_level'].upper()}")
    print(f"   Prediction: {result['prediction']['label']}")
    print(f"   At-Risk Probability: {result['probability']['at_risk']:.1%}")
    print(f"   Safe Probability: {result['probability']['safe']:.1%}")
    print(f"   Confidence: {result['confidence']:.1%}")
    
    return result


def show_recommendations(predictor, student_features):
    """Generate and display personalized recommendations."""
    print("\n" + "="*70)
    print("GENERATING PERSONALIZED INTERVENTION PLAN...")
    print("="*70)
    
    result = predictor.predict_with_recommendations(student_features)
    
    # Display the formatted plan
    print(f"\n{result['plan_text']}")
    
    return result


def main_workflow():
    """Main interactive workflow."""
    print("\n" + "="*70)
    print("🎓 INTERACTIVE STUDENT RISK ASSESSMENT SYSTEM")
    print("="*70)
    print("\nThis system will help you:")
    print("  1. Understand different risk levels")
    print("  2. Assess a specific student")
    print("  3. Generate personalized intervention plans")
    
    try:
        # Initialize predictor
        predictor = RiskPredictor()
        max_assessments = predictor.max_assessments
        
        # Step 1: Show sample predictions
        print("\n" + "="*70)
        print("STEP 1: Understanding Risk Levels")
        print("="*70)
        response = input("\nWould you like to see sample predictions first? (y/n) [y]: ").strip().lower()
        
        if response in ['', 'y', 'yes']:
            show_sample_predictions(predictor, max_assessments)
            input("\n\nPress Enter to continue to custom assessment...")
        
        # Step 2: Get custom student input
        print("\n" + "="*70)
        print("STEP 2: Custom Student Assessment")
        print("="*70)
        
        inputs = get_custom_student_input(max_assessments)
        
        # Create student features
        student_features = create_student_features(
            avg_grade=inputs['avg_grade'],
            score_std=inputs['score_std'],
            grade_range=inputs['grade_range'],
            num_assessments=int(inputs['num_assessments']),
            studied_credits=int(inputs['studied_credits']),
            num_of_prev_attempts=int(inputs['num_of_prev_attempts']),
            max_assessments=max_assessments,
        )
        
        # Show calculated features
        print("\n" + "-"*70)
        print("Calculated Features:")
        print("-"*70)
        print(f"  Grade Consistency: {student_features['grade_consistency']:.1f} (100 - std)")
        print(f"  Assessment Completion Rate: {student_features['assessment_completion_rate']:.1%}")
        print(f"  Low Performance Flag: {student_features['low_performance']}")
        print(f"  Low Engagement Flag: {student_features['low_engagement']}")
        print(f"  Has Previous Attempts: {student_features['has_previous_attempts']}")
        
        # Step 3: Show prediction
        print("\n" + "="*70)
        print("STEP 3: Risk Prediction")
        print("="*70)
        
        prediction = show_prediction(predictor, student_features)
        
        # Step 4: Ask if user wants recommendations
        print("\n" + "="*70)
        print("STEP 4: Personalized Intervention Plan")
        print("="*70)
        response = input("\nWould you like to generate personalized recommendations? (y/n) [y]: ").strip().lower()
        
        if response in ['', 'y', 'yes']:
            recommendations = show_recommendations(predictor, student_features)
            
            # Optional: Ask if they want to save the plan
            print("\n" + "-"*70)
            response = input("\nWould you like to save this plan to a file? (y/n) [n]: ").strip().lower()
            
            if response in ['y', 'yes']:
                filename = input("Enter filename [student_plan.txt]: ").strip() or "student_plan.txt"
                output_path = Path(filename)
                
                with open(output_path, 'w') as f:
                    f.write("="*70 + "\n")
                    f.write("STUDENT RISK ASSESSMENT & INTERVENTION PLAN\n")
                    f.write("="*70 + "\n\n")
                    
                    f.write("INPUT PARAMETERS:\n")
                    f.write("-"*70 + "\n")
                    for key, value in inputs.items():
                        f.write(f"  {key}: {value}\n")
                    
                    f.write(f"\n{recommendations['plan_text']}")
                
                print(f"\n✓ Plan saved to: {output_path.absolute()}")
        
        # Ask if user wants to assess another student
        print("\n" + "="*70)
        response = input("\nWould you like to assess another student? (y/n) [n]: ").strip().lower()
        
        if response in ['y', 'yes']:
            main_workflow()  # Recursive call for another assessment
        else:
            print("\n" + "="*70)
            print("✓ Assessment session completed!")
            print("="*70)
            print("\nThank you for using the Student Risk Assessment System.")
            print("For more information, visit the documentation or contact support.\n")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Assessment interrupted by user.")
        print("Your progress was not saved.\n")
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main_workflow()
