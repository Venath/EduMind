"""
Test script for ML Classification API endpoints
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8003/api/v1"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health():
    """Test health endpoint"""
    print_section("1. Testing Health Endpoint")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_model_info():
    """Test model info endpoint"""
    print_section("2. Testing Model Info Endpoint")
    response = requests.get(f"{BASE_URL}/ml/model-info")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Model Version: {data.get('model_version')}")
        print(f"Model Type: {data.get('model_type')}")
        print(f"Training Date: {data.get('training_date')}")
        print(f"Accuracy: {data.get('accuracy')}")
        print(f"Total Features: {data.get('total_features')}")
    else:
        print(f"Response: {response.text}")
    return response.status_code == 200

def test_classify_student():
    """Test single student classification"""
    print_section("3. Testing Single Student Classification")
    
    # Get a student ID from the database
    students_response = requests.get(f"{BASE_URL}/students?limit=5")
    if students_response.status_code != 200:
        print("Failed to get students")
        return False
    
    students = students_response.json()
    if not students:
        print("No students found in database")
        return False
    
    student_id = students[0]['student_id']
    print(f"\nTesting with Student ID: {student_id}")
    
    # Use POST instead of GET
    response = requests.post(f"{BASE_URL}/ml/classify/{student_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nPredicted Learning Style: {data.get('predicted_style')}")
        print(f"Confidence: {data.get('confidence', 0)*100:.1f}%")
        print(f"\nProbabilities:")
        for style, prob in data.get('probabilities', {}).items():
            print(f"  {style}: {prob*100:.1f}%")
    elif response.status_code == 400:
        print(f"\nInsufficient data: {response.json()}")
    else:
        print(f"Response: {response.text}")
    
    return response.status_code in [200, 400]  # 400 is expected if not enough data

def test_batch_classify():
    """Test batch classification"""
    print_section("4. Testing Batch Classification")
    
    print("\nRunning batch classification on all students...")
    
    response = requests.post(f"{BASE_URL}/ml/classify-batch?min_days=7")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nBatch Classification Results:")
        print(f"  Total Students: {data.get('total_students')}")
        print(f"  Successfully Classified: {data.get('classified')}")
        print(f"  Insufficient Data: {data.get('insufficient_data')}")
        print(f"  Errors: {data.get('errors')}")
        
        # Show first 5 predictions
        predictions = data.get('predictions', [])
        if predictions:
            print(f"\nSample Predictions (first 5):")
            for pred in predictions[:5]:
                print(f"  {pred.get('student_id')}: {pred.get('style')} ({pred.get('confidence', 0)*100:.1f}%)")
    else:
        print(f"Response: {response.text}")
    
    return response.status_code == 200

def test_integration():
    """Test integration with existing profile"""
    print_section("5. Testing Integration with Learning Profile")
    
    # Get a student
    students_response = requests.get(f"{BASE_URL}/students?limit=1")
    if students_response.status_code != 200:
        print("Failed to get students")
        return False
    
    students = students_response.json()
    if not students:
        print("No students found")
        return False
    
    student_id = students[0]['student_id']
    print(f"\nStudent ID: {student_id}")
    
    # Get current profile
    profile_response = requests.get(f"{BASE_URL}/students/{student_id}")
    if profile_response.status_code == 200:
        profile = profile_response.json()
        print(f"Current Profile Style: {profile.get('learning_style')}")
    
    # Get ML prediction (use POST)
    ml_response = requests.post(f"{BASE_URL}/ml/classify/{student_id}")
    if ml_response.status_code == 200:
        ml_data = ml_response.json()
        print(f"ML Predicted Style: {ml_data.get('predicted_style')}")
        print(f"Confidence: {ml_data.get('confidence', 0)*100:.1f}%")
        
        # Compare
        if profile.get('learning_style') == ml_data.get('predicted_style'):
            print("\n+ Match: Profile and ML prediction agree!")
        else:
            print("\n+ Difference: Profile and ML prediction differ")
            print("  This is normal - ML learns from behavior, profile may be manually set")
    elif ml_response.status_code == 400:
        print(f"\nInsufficient data for ML prediction")
        print(f"Details: {ml_response.json()}")
    
    return True

def main():
    print("\n" + "="*60)
    print("  LEARNING STYLE ML CLASSIFIER - API TEST SUITE")
    print("="*60)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    try:
        results['health'] = test_health()
        results['model_info'] = test_model_info()
        results['classify_student'] = test_classify_student()
        results['batch_classify'] = test_batch_classify()
        results['integration'] = test_integration()
        
        # Summary
        print_section("TEST SUMMARY")
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for test_name, passed_test in results.items():
            status = "PASSED" if passed_test else "FAILED"
            print(f"{test_name}: {status}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\nAll tests passed successfully!")
        else:
            print("\nSome tests failed. Check the output above for details.")
            
    except requests.exceptions.ConnectionError:
        print("\nERROR: Could not connect to API server")
        print("Make sure the server is running on http://localhost:8003")
    except Exception as e:
        print(f"\nERROR: {str(e)}")

if __name__ == "__main__":
    main()

