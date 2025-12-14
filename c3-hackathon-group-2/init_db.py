"""
Initialize database on app startup.
Run this once to create all tables.
"""
from models.database import init_db

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("✅ Database initialized successfully!")
    print("Tables created: users, user_profiles, financial_snapshots, assets, liabilities, goals, buckets, plans, monthly_progress, recommendation_logs")
