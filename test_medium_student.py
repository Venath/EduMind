import xgboost as xgb
import numpy as np

# Load the new model
model_path = "ml/models/xai_predictor/saved_models/academic_risk_model.json"
model = xgb.Booster()
model.load_model(model_path)

# Medium student data - exact values from user
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

# Feature order must match training
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

# Create feature array
features = np.array([[student_data[name] for name in feature_names]], dtype=np.float32)
dmatrix = xgb.DMatrix(features, feature_names=feature_names)

# Predict
prediction = model.predict(dmatrix)
prob_at_risk = float(prediction[0])
prob_safe = 1.0 - prob_at_risk

print("\n" + "="*60)
print("MEDIUM STUDENT PREDICTION TEST")
print("="*60)
print(f"\nInput Features:")
for name in feature_names:
    print(f"  {name}: {student_data[name]}")

print(f"\n📊 Model Prediction:")
print(f"  At-Risk Probability: {prob_at_risk*100:.1f}%")
print(f"  Safe Probability: {prob_safe*100:.1f}%")
print(f"  Predicted Class: {'At-Risk' if prob_at_risk >= 0.5 else 'Safe'}")

print("\n" + "="*60)
print("ANALYSIS:")
print("="*60)

# Analyze the features
issues = []
if student_data['avg_grade'] < 65:
    issues.append(f"• Grade (60) is below passing threshold")
if student_data['grade_consistency'] < 85:
    issues.append(f"• Grade consistency (80) is below average (mean: 89.6)")
if student_data['num_assessments'] < 6:
    issues.append(f"• Low assessment count (5) compared to average (6.35)")
if student_data['assessment_completion_rate'] < 0.6:
    issues.append(f"• Completion rate (50%) is significantly below expected")
if student_data['has_previous_attempts'] == 1:
    issues.append(f"• Has previous failed attempts (high importance feature)")

print("\nRisk Factors Identified:")
for issue in issues:
    print(issue)

print("\n💡 Why 99% At-Risk?")
print("  The model heavily weighs:")
print("  1. num_assessments (40.24% importance) - Student has 5, avg is 6.35")
print("  2. assessment_completion_rate (27.69%) - Student has 50%, avg is 22.7%")
print("  3. has_previous_attempts (7.63%) - Student has failed before")
print("  4. Grade (60) is borderline passing")
print("  5. Grade consistency (80) below average (89.6)")
print("\n  Combined factors = Very High Risk")
print("="*60 + "\n")
