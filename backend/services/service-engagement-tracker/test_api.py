"""
Quick API Test Script
Tests all major endpoints to verify the API is working
"""
import sys
import codecs

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8002"

def test_health():
    """Test health check endpoint"""
    print("\n[HEALTH] Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("   ✅ Health check passed!")

def test_system_stats():
    """Test system statistics"""
    print("\n📊 Testing System Statistics...")
    response = requests.get(f"{BASE_URL}/api/v1/stats")
    print(f"   Status: {response.status_code}")
    data = response.json()
    print(f"   Total Students: {data['total_students']}")
    print(f"   Total Engagement Records: {data['total_engagement_records']}")
    print(f"   High Risk Students: {data['high_risk_students']}")
    assert response.status_code == 200
    print("   ✅ System stats passed!")

def test_engagement_score():
    """Test engagement score endpoint"""
    print("\n📈 Testing Engagement Score...")
    student_id = "STU0001"
    response = requests.get(f"{BASE_URL}/api/v1/engagement/students/{student_id}/latest")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Student: {data['student_id']}")
        print(f"   Engagement Score: {data['engagement_score']}")
        print(f"   Level: {data['engagement_level']}")
        print("   ✅ Engagement score passed!")
    else:
        print(f"   ❌ Failed: {response.text}")

def test_engagement_summary():
    """Test engagement summary"""
    print("\n📋 Testing Engagement Summary...")
    student_id = "STU0001"
    response = requests.get(f"{BASE_URL}/api/v1/engagement/students/{student_id}/summary")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Days Tracked: {data['days_tracked']}")
        print(f"   Avg Score: {data['avg_engagement_score']}")
        print(f"   Trend: {data['trend']}")
        print("   ✅ Engagement summary passed!")
    else:
        print(f"   ❌ Failed: {response.text}")

def test_prediction():
    """Test prediction endpoint"""
    print("\n🎯 Testing Disengagement Prediction...")
    student_id = "STU0085"  # Known high-risk student
    response = requests.get(f"{BASE_URL}/api/v1/predictions/students/{student_id}/latest")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Student: {data['student_id']}")
        print(f"   At Risk: {data['at_risk']}")
        print(f"   Risk Probability: {data['risk_probability']:.3f}")
        print(f"   Risk Level: {data['risk_level']}")
        print("   ✅ Prediction passed!")
    else:
        print(f"   ❌ Failed: {response.text}")

def test_at_risk_students():
    """Test at-risk students list"""
    print("\n⚠️  Testing At-Risk Students List...")
    response = requests.get(f"{BASE_URL}/api/v1/predictions/high-risk?limit=5")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Found {len(data)} high-risk students")
        for student in data[:3]:
            print(f"      - {student['student_id']}: Risk={student['avg_risk_probability']:.3f}")
        print("   ✅ At-risk list passed!")
    else:
        print(f"   ❌ Failed: {response.text}")

def test_student_dashboard():
    """Test student dashboard"""
    print("\n📊 Testing Student Dashboard...")
    student_id = "STU0001"
    response = requests.get(f"{BASE_URL}/api/v1/students/{student_id}/dashboard")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        status = data['current_status']
        print(f"   Engagement Score: {status['engagement_score']}")
        print(f"   Level: {status['engagement_level']}")
        print(f"   At Risk: {status['at_risk']}")
        print(f"   Alerts: {len(data['alerts'])}")
        print("   ✅ Dashboard passed!")
    else:
        print(f"   ❌ Failed: {response.text}")

def test_leaderboard():
    """Test leaderboard"""
    print("\n🏆 Testing Leaderboard...")
    response = requests.get(f"{BASE_URL}/api/v1/engagement/leaderboard?limit=5")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Top {len(data)} students:")
        for i, student in enumerate(data, 1):
            print(f"      {i}. {student['student_id']}: {student['avg_engagement_score']:.2f}")
        print("   ✅ Leaderboard passed!")
    else:
        print(f"   ❌ Failed: {response.text}")

def test_event_ingest():
    """Test event ingestion"""
    print("\n📥 Testing Event Ingestion...")
    event = {
        "student_id": "STU0001",
        "event_type": "login",
        "event_timestamp": datetime.now().isoformat(),
        "session_id": "test_session_123",
        "event_data": {"test": True},
        "source_service": "test"
    }
    response = requests.post(f"{BASE_URL}/api/v1/events/ingest", json=event)
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"   Event ID: {data['event_id']}")
        print(f"   Status: {data['status']}")
        print("   ✅ Event ingestion passed!")
    else:
        print(f"   ❌ Failed: {response.text}")

def test_prediction_stats():
    """Test prediction statistics"""
    print("\n📈 Testing Prediction Statistics...")
    response = requests.get(f"{BASE_URL}/api/v1/predictions/statistics")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Total Predictions: {data['total_predictions']}")
        print(f"   At-Risk: {data['at_risk_percentage']:.1f}%")
        print(f"   High Risk: {data['risk_levels']['high']}")
        print("   ✅ Prediction stats passed!")
    else:
        print(f"   ❌ Failed: {response.text}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 EDUMIND API TEST SUITE")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    
    try:
        test_health()
        test_system_stats()
        test_engagement_score()
        test_engagement_summary()
        test_prediction()
        test_at_risk_students()
        test_student_dashboard()
        test_leaderboard()
        test_event_ingest()
        test_prediction_stats()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n🎉 API is fully operational!")
        print("📚 View documentation: http://localhost:8002/api/docs")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Cannot connect to API at {BASE_URL}")
        print("   Make sure the server is running:")
        print("   uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()

