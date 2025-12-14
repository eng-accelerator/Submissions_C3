"""
Financial data models: Snapshot, Assets, Liabilities, Goals.
"""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Enum, Numeric, Date, JSON, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from models.database import Base


class AssetType(str, enum.Enum):
    """Asset types."""
    CASH = "cash"
    FD = "fd"
    MF = "mf"
    ETF = "etf"
    STOCK = "stock"
    GOLD = "gold"
    CRYPTO = "crypto"
    REAL_ESTATE = "real_estate"
    OTHER = "other"


class Liquidity(str, enum.Enum):
    """Liquidity levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class LiabilityType(str, enum.Enum):
    """Liability/debt types."""
    CREDIT_CARD = "credit_card"
    PERSONAL_LOAN = "personal_loan"
    HOME_LOAN = "home_loan"
    CAR_LOAN = "car_loan"
    EDUCATION_LOAN = "education_loan"
    OTHER = "other"


class GoalCategory(str, enum.Enum):
    """Goal categories based on timeline."""
    EMERGENCY = "emergency"
    SHORT_TERM = "short_term"      # < 3 years
    MEDIUM_TERM = "medium_term"    # 3-5 years
    LONG_TERM = "long_term"        # 5+ years
    RETIREMENT = "retirement"


class FinancialSnapshot(Base):
    """Point-in-time financial snapshot."""
    __tablename__ = "financial_snapshots"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    monthly_income = Column(Numeric(12, 2), nullable=False)
    monthly_expenses = Column(Numeric(12, 2), nullable=False)
    current_savings = Column(Numeric(12, 2), nullable=False)
    expense_breakdown = Column(JSON, nullable=True)  # JSONB in PostgreSQL, JSON in SQLite
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="snapshots")
    plans = relationship("Plan", back_populates="snapshot")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('monthly_income >= 0', name='check_income_positive'),
        CheckConstraint('monthly_expenses >= 0', name='check_expenses_positive'),
        CheckConstraint('current_savings >= 0', name='check_savings_positive'),
    )
    
    def __repr__(self):
        return f"<FinancialSnapshot(id={self.id}, user_id={self.user_id})>"


class Asset(Base):
    """User assets and investments."""
    __tablename__ = "assets"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(Enum(AssetType), nullable=False)
    name = Column(String(200), nullable=False)
    current_value = Column(Numeric(15, 2), nullable=False)
    liquidity = Column(Enum(Liquidity), nullable=True)
    expected_return = Column(Numeric(5, 4), default=0.0, nullable=True)  # As decimal (0.12 = 12%)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    user = relationship("User", back_populates="assets")
    
    __table_args__ = (
        CheckConstraint('current_value >= 0', name='check_asset_value_positive'),
    )
    
    def __repr__(self):
        return f"<Asset(id={self.id}, type={self.type}, value={self.current_value})>"


class Liability(Base):
    """User liabilities and debts."""
    __tablename__ = "liabilities"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(Enum(LiabilityType), nullable=False)
    name = Column(String(200), nullable=False)
    outstanding_amount = Column(Numeric(15, 2), nullable=False)
    interest_rate = Column(Numeric(5, 4), nullable=False)  # As decimal (0.36 = 36%)
    tenure_months = Column(Integer, nullable=True)
    minimum_payment = Column(Numeric(12, 2), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    user = relationship("User", back_populates="liabilities")
    
    __table_args__ = (
        CheckConstraint('outstanding_amount >= 0', name='check_liability_positive'),
        CheckConstraint('interest_rate >= 0 AND interest_rate <= 1', name='check_interest_rate_valid'),
    )
    
    def __repr__(self):
        return f"<Liability(id={self.id}, type={self.type}, amount={self.outstanding_amount})>"


class Goal(Base):
    """User financial goals."""
    __tablename__ = "goals"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    target_amount = Column(Numeric(15, 2), nullable=False)
    target_date = Column(Date, nullable=False)
    priority = Column(Integer, nullable=True)  # 1-5, 1 being highest
    category = Column(Enum(GoalCategory), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    user = relationship("User", back_populates="goals")
    
    __table_args__ = (
        CheckConstraint('target_amount > 0', name='check_goal_amount_positive'),
        CheckConstraint('priority >= 1 AND priority <= 5', name='check_priority_range'),
    )
    
    def __repr__(self):
        return f"<Goal(id={self.id}, name={self.name}, amount={self.target_amount})>"
