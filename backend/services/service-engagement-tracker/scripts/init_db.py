"""
Database initialization script
Creates all tables and optionally generates synthetic data
"""
import sys
import os

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base, init_db, drop_all_tables
from app.models import (
    StudentActivityEvent,
    DailyEngagementMetric,
    EngagementScore,
    DisengagementPrediction,
    InterventionLog,
    StudySchedule
)


def create_tables():
    """Create all database tables"""
    print("=" * 60)
    print("DATABASE INITIALIZATION")
    print("=" * 60)
    
    print("\n📊 Creating database tables...")
    print(f"   Database: {engine.url}")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("\n✅ Successfully created tables:")
        for table in Base.metadata.sorted_tables:
            print(f"   - {table.name}")
        
        print("\n" + "=" * 60)
        print("✅ DATABASE INITIALIZATION COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error creating tables: {str(e)}")
        sys.exit(1)


def reset_database():
    """Drop all tables and recreate (USE WITH CAUTION!)"""
    print("\n⚠️  WARNING: This will DELETE ALL DATA!")
    confirm = input("Type 'yes' to confirm: ")
    
    if confirm.lower() == 'yes':
        print("\n🗑️  Dropping all tables...")
        drop_all_tables()
        
        print("\n📊 Recreating tables...")
        create_tables()
    else:
        print("\n❌ Operation cancelled")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize database")
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Drop all tables and recreate (DANGEROUS!)'
    )
    
    args = parser.parse_args()
    
    if args.reset:
        reset_database()
    else:
        create_tables()

