"""
Seed demo learning resources and recommendations so the learning-style dashboard
shows non-zero RESOURCES, RECOMMENDATIONS, and SUCCESS RATE.

Run from service-learning-style directory:
    python scripts/seed_demo_data.py
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models import LearningResource, ResourceRecommendation, StudentLearningProfile

DEMO_STUDENTS = [
    "STU0001", "STU0002", "STU0003", "STU0004", "STU0005",  # Institute A
    "STU0006", "STU0007", "STU0008", "STU0009", "STU0010",  # Institute B
    "STU0011", "STU0012", "STU0013", "STU0014", "STU0015",  # Institute B
    "STU0016", "STU0017", "STU0018", "STU0019", "STU0020",  # Institute B
    "STU0021", "STU0022", "STU0023", "STU0024", "STU0025"   # Institute B
]

DEMO_RESOURCES = [
    {
        "resource_type": "video",
        "title": "Introduction to Machine Learning",
        "description": "Short video on ML basics",
        "topic": "Machine Learning",
        "subject": "Computer Science",
        "difficulty_level": "Medium",
        "learning_styles": ["Visual", "Auditory"],
        "url": "https://example.com/edumind/video/ml-intro",
        "estimated_duration": 15,
        "effectiveness_rating": 4.2,
        "total_views": 100,
        "total_completions": 60,
    },
    {
        "resource_type": "article",
        "title": "Understanding Neural Networks",
        "description": "Reading material on neural nets",
        "topic": "Deep Learning",
        "subject": "Computer Science",
        "difficulty_level": "Hard",
        "learning_styles": ["Reading"],
        "url": "https://example.com/edumind/article/nn",
        "estimated_duration": 20,
        "effectiveness_rating": 4.0,
        "total_views": 80,
        "total_completions": 45,
    },
    {
        "resource_type": "interactive",
        "title": "Hands-on Python Practice",
        "description": "Interactive coding exercises",
        "topic": "Programming",
        "subject": "Computer Science",
        "difficulty_level": "Easy",
        "learning_styles": ["Kinesthetic"],
        "url": "https://example.com/edumind/interactive/python",
        "estimated_duration": 30,
        "effectiveness_rating": 4.5,
        "total_views": 120,
        "total_completions": 90,
    },
    {
        "resource_type": "quiz",
        "title": "ML Fundamentals Quiz",
        "description": "Quick knowledge check",
        "topic": "Machine Learning",
        "subject": "Computer Science",
        "difficulty_level": "Medium",
        "learning_styles": ["Reading", "Kinesthetic"],
        "url": "https://example.com/edumind/quiz/ml-fundamentals",
        "estimated_duration": 10,
        "effectiveness_rating": 3.8,
        "total_views": 90,
        "total_completions": 70,
    },
    {
        "resource_type": "tutorial",
        "title": "Step-by-step Data Preprocessing",
        "description": "Tutorial for data prep",
        "topic": "Data Science",
        "subject": "Computer Science",
        "difficulty_level": "Medium",
        "learning_styles": ["Visual", "Reading"],
        "url": "https://example.com/edumind/tutorial/data-prep",
        "estimated_duration": 25,
        "effectiveness_rating": 4.3,
        "total_views": 85,
        "total_completions": 55,
    },
    {
        "resource_type": "cheatsheet",
        "title": "Pandas Quick Reference",
        "description": "One-page pandas reference",
        "topic": "Data Science",
        "subject": "Computer Science",
        "difficulty_level": "Easy",
        "learning_styles": ["Reading", "Visual"],
        "url": "https://example.com/edumind/cheatsheet/pandas",
        "estimated_duration": 5,
        "effectiveness_rating": 4.6,
        "total_views": 200,
        "total_completions": 180,
    },
    {
        "resource_type": "video",
        "title": "Web Development Basics: HTML & CSS",
        "description": "Comprehensive video tutorial on web fundamentals",
        "topic": "Web Development",
        "subject": "Computer Science",
        "difficulty_level": "Easy",
        "learning_styles": ["Visual", "Auditory"],
        "url": "https://example.com/edumind/video/web-basics",
        "estimated_duration": 45,
        "effectiveness_rating": 4.4,
        "total_views": 150,
        "total_completions": 110,
    },
    {
        "resource_type": "article",
        "title": "JavaScript Fundamentals Explained",
        "description": "In-depth article covering JS basics and best practices",
        "topic": "Programming",
        "subject": "Computer Science",
        "difficulty_level": "Medium",
        "learning_styles": ["Reading"],
        "url": "https://example.com/edumind/article/javascript",
        "estimated_duration": 30,
        "effectiveness_rating": 4.1,
        "total_views": 95,
        "total_completions": 65,
    },
    {
        "resource_type": "interactive",
        "title": "Database Design Workshop",
        "description": "Interactive exercises for designing relational databases",
        "topic": "Database Management",
        "subject": "Computer Science",
        "difficulty_level": "Medium",
        "learning_styles": ["Kinesthetic", "Visual"],
        "url": "https://example.com/edumind/interactive/db-design",
        "estimated_duration": 60,
        "effectiveness_rating": 4.3,
        "total_views": 75,
        "total_completions": 55,
    },
    {
        "resource_type": "quiz",
        "title": "SQL Query Practice Quiz",
        "description": "Test your SQL knowledge with practical questions",
        "topic": "Database Management",
        "subject": "Computer Science",
        "difficulty_level": "Medium",
        "learning_styles": ["Reading", "Kinesthetic"],
        "url": "https://example.com/edumind/quiz/sql-practice",
        "estimated_duration": 15,
        "effectiveness_rating": 4.0,
        "total_views": 120,
        "total_completions": 95,
    },
    {
        "resource_type": "tutorial",
        "title": "Building REST APIs with Python Flask",
        "description": "Step-by-step guide to creating RESTful APIs",
        "topic": "Web Development",
        "subject": "Computer Science",
        "difficulty_level": "Hard",
        "learning_styles": ["Visual", "Reading", "Kinesthetic"],
        "url": "https://example.com/edumind/tutorial/flask-api",
        "estimated_duration": 90,
        "effectiveness_rating": 4.5,
        "total_views": 110,
        "total_completions": 75,
    },
    {
        "resource_type": "video",
        "title": "Computer Networks: TCP/IP Explained",
        "description": "Visual explanation of network protocols and layers",
        "topic": "Computer Networks",
        "subject": "Computer Science",
        "difficulty_level": "Hard",
        "learning_styles": ["Visual", "Auditory"],
        "url": "https://example.com/edumind/video/tcpip",
        "estimated_duration": 50,
        "effectiveness_rating": 4.2,
        "total_views": 85,
        "total_completions": 60,
    },
    {
        "resource_type": "article",
        "title": "Software Engineering Best Practices",
        "description": "Comprehensive guide to software development methodologies",
        "topic": "Software Engineering",
        "subject": "Computer Science",
        "difficulty_level": "Medium",
        "learning_styles": ["Reading"],
        "url": "https://example.com/edumind/article/software-eng",
        "estimated_duration": 40,
        "effectiveness_rating": 4.3,
        "total_views": 100,
        "total_completions": 70,
    },
    {
        "resource_type": "interactive",
        "title": "Algorithm Visualization Lab",
        "description": "Hands-on practice with sorting and searching algorithms",
        "topic": "Algorithms",
        "subject": "Computer Science",
        "difficulty_level": "Hard",
        "learning_styles": ["Kinesthetic", "Visual"],
        "url": "https://example.com/edumind/interactive/algorithms",
        "estimated_duration": 75,
        "effectiveness_rating": 4.4,
        "total_views": 90,
        "total_completions": 65,
    },
    {
        "resource_type": "practice",
        "title": "Git Version Control Exercises",
        "description": "Practical exercises for mastering Git commands",
        "topic": "Software Engineering",
        "subject": "Computer Science",
        "difficulty_level": "Easy",
        "learning_styles": ["Kinesthetic", "Reading"],
        "url": "https://example.com/edumind/practice/git",
        "estimated_duration": 35,
        "effectiveness_rating": 4.5,
        "total_views": 140,
        "total_completions": 115,
    },
    {
        "resource_type": "video",
        "title": "Introduction to React.js",
        "description": "Video course on React fundamentals and hooks",
        "topic": "Web Development",
        "subject": "Computer Science",
        "difficulty_level": "Medium",
        "learning_styles": ["Visual", "Auditory"],
        "url": "https://example.com/edumind/video/react-intro",
        "estimated_duration": 55,
        "effectiveness_rating": 4.6,
        "total_views": 180,
        "total_completions": 135,
    },
    {
        "resource_type": "cheatsheet",
        "title": "Linux Command Line Reference",
        "description": "Quick reference for common Linux commands",
        "topic": "Operating Systems",
        "subject": "Computer Science",
        "difficulty_level": "Easy",
        "learning_styles": ["Reading", "Visual"],
        "url": "https://example.com/edumind/cheatsheet/linux",
        "estimated_duration": 10,
        "effectiveness_rating": 4.7,
        "total_views": 220,
        "total_completions": 200,
    },
    {
        "resource_type": "tutorial",
        "title": "Docker Containerization Guide",
        "description": "Step-by-step tutorial on containerizing applications",
        "topic": "DevOps",
        "subject": "Computer Science",
        "difficulty_level": "Medium",
        "learning_styles": ["Visual", "Reading", "Kinesthetic"],
        "url": "https://example.com/edumind/tutorial/docker",
        "estimated_duration": 65,
        "effectiveness_rating": 4.4,
        "total_views": 105,
        "total_completions": 80,
    },
    {
        "resource_type": "quiz",
        "title": "Data Structures Assessment",
        "description": "Comprehensive quiz on arrays, lists, trees, and graphs",
        "topic": "Data Structures",
        "subject": "Computer Science",
        "difficulty_level": "Hard",
        "learning_styles": ["Reading", "Kinesthetic"],
        "url": "https://example.com/edumind/quiz/data-structures",
        "estimated_duration": 25,
        "effectiveness_rating": 3.9,
        "total_views": 70,
        "total_completions": 50,
    },
    {
        "resource_type": "article",
        "title": "Cybersecurity Fundamentals",
        "description": "Essential reading on security best practices and threats",
        "topic": "Cybersecurity",
        "subject": "Computer Science",
        "difficulty_level": "Medium",
        "learning_styles": ["Reading"],
        "url": "https://example.com/edumind/article/cybersecurity",
        "estimated_duration": 35,
        "effectiveness_rating": 4.2,
        "total_views": 88,
        "total_completions": 62,
    },
]


def seed_resources(db):
    """Insert demo resources if none exist."""
    existing = db.query(LearningResource).count()
    if existing > 0:
        print(f"  Learning resources already exist ({existing}). Skipping.")
        return list(db.query(LearningResource).limit(len(DEMO_RESOURCES)).all())
    for r in DEMO_RESOURCES:
        rec = LearningResource(**r)
        db.add(rec)
    db.commit()
    # Fetch so we have IDs
    resources = db.query(LearningResource).all()
    print(f"  Created {len(resources)} learning resources.")
    return resources


def seed_recommendations(db, resources):
    """Create demo recommendations for each demo student; some completed for success rate."""
    if not resources:
        return
    existing = db.query(ResourceRecommendation).count()
    if existing > 0:
        print(f"  Recommendations already exist ({existing}). Skipping.")
        return
    now = datetime.utcnow()
    rec_id = 0
    for student_id in DEMO_STUDENTS:
        # Ensure student profile exists
        profile = db.query(StudentLearningProfile).filter(
            StudentLearningProfile.student_id == student_id
        ).first()
        if not profile:
            continue
        # 5-6 recommendations per student; about half completed
        # Use more resources now that we have 20 available
        num_recommendations = min(6, len(resources))
        for i, res in enumerate(resources[:num_recommendations]):
            rec_id += 1
            completed = (rec_id + ord(student_id[-1])) % 2 == 0  # vary by student
            rec = ResourceRecommendation(
                student_id=student_id,
                resource_id=res.resource_id,
                reason=f"Matches your learning style and current topic progress.",
                relevance_score=0.7 + (i * 0.05),
                rank_position=i + 1,
                recommended_at=now - timedelta(days=5 - i),
                viewed=completed or (rec_id % 3 == 0),
                completed=completed,
                completed_at=now - timedelta(days=3 - i) if completed else None,
                completion_percentage=100.0 if completed else (50.0 if rec_id % 3 == 0 else 0.0),
            )
            db.add(rec)
    db.commit()
    count = db.query(ResourceRecommendation).count()
    completed = db.query(ResourceRecommendation).filter(ResourceRecommendation.completed == True).count()
    print(f"  Created {count} recommendations ({completed} completed).")


def main():
    print("=" * 60)
    print("  Learning Style Service – Demo Data Seeder")
    print("=" * 60)
    db = SessionLocal()
    try:
        print("\n1. Seeding learning resources...")
        resources = seed_resources(db)
        print("\n2. Seeding recommendations for demo students...")
        seed_recommendations(db, resources)
        print("\n" + "=" * 60)
        print("  Done. Restart or refresh the learning-style dashboard.")
        print("=" * 60)
    finally:
        db.close()


if __name__ == "__main__":
    main()
