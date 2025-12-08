"""
Test script to check if recommendations can be generated
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.learning_style import (
    StudentLearningProfile,
    LearningResource,
    StudentStruggle,
    ResourceRecommendation
)
from sqlalchemy import func

def check_database():
    """Check database contents"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*60)
        print("DATABASE CONTENTS CHECK")
        print("="*60)
        
        # Check students
        student_count = db.query(StudentLearningProfile).count()
        print(f"\n1. Students: {student_count}")
        
        if student_count > 0:
            sample_student = db.query(StudentLearningProfile).first()
            print(f"   Sample: {sample_student.student_id} - {sample_student.learning_style}")
        
        # Check resources
        resource_count = db.query(LearningResource).count()
        print(f"\n2. Learning Resources: {resource_count}")
        
        if resource_count > 0:
            # Count by type
            resource_types = db.query(
                LearningResource.resource_type,
                func.count(LearningResource.resource_id)
            ).group_by(LearningResource.resource_type).all()
            
            for rtype, count in resource_types:
                print(f"   - {rtype}: {count}")
        
        # Check struggles
        struggle_count = db.query(StudentStruggle).count()
        print(f"\n3. Student Struggles: {struggle_count}")
        
        if struggle_count > 0:
            sample_struggle = db.query(StudentStruggle).first()
            print(f"   Sample: {sample_struggle.student_id} - {sample_struggle.topic}")
        
        # Check existing recommendations
        recommendation_count = db.query(ResourceRecommendation).count()
        print(f"\n4. Existing Recommendations: {recommendation_count}")
        
        print("\n" + "="*60)
        print("DIAGNOSIS")
        print("="*60)
        
        if resource_count == 0:
            print("\n❌ PROBLEM: No learning resources in database!")
            print("   Solution: Run 'python scripts/generate_sample_data.py'")
        elif struggle_count == 0:
            print("\n⚠️  WARNING: No student struggles detected")
            print("   Recommendations need struggles to be triggered")
            print("   Solution: Add struggles manually or via API")
        else:
            print("\n✅ Database has resources and struggles")
            print("   Recommendations should work!")
        
        print("\n" + "="*60)
        
    finally:
        db.close()

def test_recommendation_for_student(student_id: str):
    """Test recommendation generation for a specific student"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*60)
        print(f"TESTING RECOMMENDATIONS FOR {student_id}")
        print("="*60)
        
        # Check if student exists
        student = db.query(StudentLearningProfile).filter(
            StudentLearningProfile.student_id == student_id
        ).first()
        
        if not student:
            print(f"\n❌ Student {student_id} not found!")
            return
        
        print(f"\n✅ Student found: {student.learning_style}")
        
        # Check for struggles
        struggles = db.query(StudentStruggle).filter(
            StudentStruggle.student_id == student_id
        ).all()
        
        print(f"\n📊 Struggles for this student: {len(struggles)}")
        for struggle in struggles[:3]:
            print(f"   - {struggle.topic} (severity: {struggle.severity})")
        
        # Check available resources
        resources = db.query(LearningResource).limit(5).all()
        print(f"\n📚 Sample resources available:")
        for resource in resources:
            print(f"   - {resource.title} ({resource.resource_type})")
        
        if len(struggles) == 0:
            print("\n⚠️  No struggles found for this student!")
            print("   Recommendations are triggered by struggles.")
            print("   Try adding a struggle via the API:")
            print(f"""
   POST /api/v1/struggles
   {{
       "student_id": "{student_id}",
       "topic": "Python Loops",
       "severity": "medium"
   }}
            """)
        
    finally:
        db.close()

if __name__ == "__main__":
    check_database()
    
    # Test for a specific student
    if len(sys.argv) > 1:
        student_id = sys.argv[1]
        test_recommendation_for_student(student_id)
    else:
        print("\nTo test a specific student, run:")
        print("  python test_recommendations.py STU0001")





