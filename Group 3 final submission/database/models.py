from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    phone = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Profile data
    monthly_income = Column(Float, default=0.0)
    occupation = Column(String(100))
    age = Column(Integer)
    dependents = Column(Integer, default=0)
    city = Column(String(100))
    
    # Document flags
    has_salary_slip = Column(Boolean, default=False)
    has_bank_statement = Column(Boolean, default=False)
    has_loan_data = Column(Boolean, default=False)
    has_credit_card_statement = Column(Boolean, default=False)
    has_collateral_details = Column(Boolean, default=False)

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    document_type = Column(String(50), nullable=False)  # salary_slip, bank_statement, etc.
    file_name = Column(String(255))
    file_path = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)
    doc_metadata = Column(Text)  # JSON string for additional info (renamed from metadata)

class FinancialData(Base):
    __tablename__ = 'financial_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    data_type = Column(String(50))  # income, expense, debt, investment, etc.
    category = Column(String(100))
    amount = Column(Float)
    description = Column(Text)
    transaction_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    source_document_id = Column(Integer)

class ChatHistory(Base):
    __tablename__ = 'chat_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text)
    agent_type = Column(String(50))  # debt_analyzer, savings_strategy, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

# Get database URL and handle different drivers
DATABASE_URL = os.getenv('DATABASE_URL')

# Support for both psycopg2 and psycopg drivers
if DATABASE_URL:
    # If psycopg2 is not available, try psycopg
    if 'postgresql+psycopg2' in DATABASE_URL:
        try:
            import psycopg2
        except ImportError:
            # psycopg2 not available, try psycopg
            try:
                import psycopg
                DATABASE_URL = DATABASE_URL.replace('postgresql+psycopg2', 'postgresql+psycopg')
                print("Using psycopg driver instead of psycopg2")
            except ImportError:
                print("WARNING: Neither psycopg2 nor psycopg is installed!")
                print("Please install one: pip install psycopg2-binary OR pip install 'psycopg[binary]'")

# Create engine
engine = create_engine(DATABASE_URL)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()