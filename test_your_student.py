import xgboost as xgb
import numpy as np

# Load the model
model_path = "ml/models/xai_predictor/saved_models/academic_risk_model_multiclass.json"
model = xgb.Booster()
model.load_model(model_path)

# Your medium student data
student_data = {
    'avg_grade': 60,
    'grade_consistency': 80,
    'grade_range': 25,
    'num_assessments': 5,
    'assessment_completion_rate': 0.5,
    'studied_credits': 60,
    'num_of_prev_attempts': 1,
    'low_performance': 0,
    'low_engagement': 0,
    'has_previous_attempts': 1
}

feature_names = [
    'avg_grade', 'grade_consistency', 'grade_range', 'num_assessments',
    'assessment_completion_rate', 'studied_credits', 'num_of_prev_attempts',
    'low_performance', 'low_engagement', 'has_previous_attempts'
]

# Create feature array
features = np.array([[student_data[name] for name in feature_names]], dtype=np.float32)
dmatrix = xgb.DMatrix(features, feature_names=feature_names)

# Predict
predictions = model.predict(dmatrix)
prob_safe = float(predictions[0][0])
prob_medium = float(predictions[0][1])
prob_at_risk = float(predictions[0][2])

predicted_class = int(np.argmax([prob_safe, prob_medium, prob_at_risk]))
class_names = ["Safe", "Medium Risk", "At-Risk"]

print("\n" + "="*70)
print("YOUR MEDIUM RISK STUDENT PREDICTION")
print("="*70)
print(f"\nInput Features:")
print(f"  avg_grade: {student_data['avg_grade']}")
print(f"  grade_consistency: {student_data['grade_consistency']}")
print(f"  num_assessments: {student_data['num_assessments']}")
print(f"  completion_rate: {student_data['assessment_completion_rate']}")
print(f"  prev_attempts: {student_data['num_of_prev_attempts']}")

print(f"\n📊 Model Predictions:")
print(f"  Safe:        {prob_safe*100:5.1f}%")
print(f"  Medium Risk: {prob_medium*100:5.1f}%")
print(f"  At-Risk:     {prob_at_risk*100:5.1f}%")
print(f"\n🎯 Predicted: {class_names[predicted_class]}")
print("="*70 + "\n")
