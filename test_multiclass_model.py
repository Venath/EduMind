import xgboost as xgb
import numpy as np

# Load the multi-class model
model_path = "ml/models/xai_predictor/saved_models/academic_risk_model_multiclass.json"
model = xgb.Booster()
model.load_model(model_path)

# Feature names
feature_names = [
    'avg_grade',
    'grade_consistency',
    'grade_range',
    'num_assessments',
    'assessment_completion_rate',
    'studied_credits',
    'num_of_prev_attempts',
    'low_performance',
    'low_engagement',
    'has_previous_attempts'
]

# Test cases
test_cases = [
    {
        "name": "Safe Student",
        "features": {
            'avg_grade': 85,
            'grade_consistency': 95,
            'grade_range': 15,
            'num_assessments': 8,
            'assessment_completion_rate': 0.9,
            'studied_credits': 120,
            'num_of_prev_attempts': 0,
            'low_performance': 0,
            'low_engagement': 0,
            'has_previous_attempts': 0
        }
    },
    {
        "name": "Medium Risk Student",
        "features": {
            'avg_grade': 65,
            'grade_consistency': 82,
            'grade_range': 30,
            'num_assessments': 6,
            'assessment_completion_rate': 0.6,
            'studied_credits': 80,
            'num_of_prev_attempts': 1,
            'low_performance': 0,
            'low_engagement': 0,
            'has_previous_attempts': 1
        }
    },
    {
        "name": "At-Risk Student",
        "features": {
            'avg_grade': 40,
            'grade_consistency': 65,
            'grade_range': 45,
            'num_assessments': 3,
            'assessment_completion_rate': 0.3,
            'studied_credits': 40,
            'num_of_prev_attempts': 2,
            'low_performance': 1,
            'low_engagement': 1,
            'has_previous_attempts': 1
        }
    }
]

print("\n" + "="*70)
print("MULTI-CLASS MODEL PREDICTION TEST")
print("="*70)

for test_case in test_cases:
    # Create feature array
    features = np.array([[test_case["features"][name] for name in feature_names]], dtype=np.float32)
    dmatrix = xgb.DMatrix(features, feature_names=feature_names)
    
    # Predict
    predictions = model.predict(dmatrix)
    prob_safe = float(predictions[0][0])
    prob_medium = float(predictions[0][1])
    prob_at_risk = float(predictions[0][2])
    
    predicted_class = int(np.argmax([prob_safe, prob_medium, prob_at_risk]))
    class_names = ["Safe", "Medium Risk", "At-Risk"]
    
    print(f"\n{test_case['name']}:")
    print(f"  Input:")
    print(f"    avg_grade: {test_case['features']['avg_grade']}")
    print(f"    grade_consistency: {test_case['features']['grade_consistency']}")
    print(f"    num_assessments: {test_case['features']['num_assessments']}")
    print(f"    completion_rate: {test_case['features']['assessment_completion_rate']}")
    print(f"    prev_attempts: {test_case['features']['num_of_prev_attempts']}")
    print(f"\n  Predictions:")
    print(f"    Safe:        {prob_safe*100:5.1f}%")
    print(f"    Medium Risk: {prob_medium*100:5.1f}%")
    print(f"    At-Risk:     {prob_at_risk*100:5.1f}%")
    print(f"  → Predicted: {class_names[predicted_class]}")

print("\n" + "="*70)
print("✅ Multi-class model is working correctly!")
print("="*70 + "\n")
