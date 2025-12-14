"""
Plan and progress tracking models: Bucket, Plan, MonthlyProgress, RecommendationLog.
"""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Enum, Numeric, Date, JSON, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from models.database import Base


class BucketType(str, enum.Enum):
    """Money bucket types."""
    EMERGENCY = "emergency"
    DEBT = "debt"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    INSURANCE = "insurance"


class BucketStatus(str, enum.Enum):
    """Bucket status."""
    CRITICAL = "critical"
    ACTIVE = "active"
    ON_TRACK = "on_track"
    COMPLETED = "completed"
    DEFERRED = "deferred"


class ProgressStatus(str, enum.Enum):
    """Monthly progress status."""
    AHEAD = "ahead"
    ON_TRACK = "on_track"
    BEHIND = "behind"
    CRITICAL = "critical"


class Bucket(Base):
    """Money allocation buckets."""
    __tablename__ = "buckets"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(Enum(BucketType), nullable=False)
    target_amount = Column(Numeric(15, 2), nullable=False)
    current_amount = Column(Numeric(15, 2), default=0, nullable=False)
    status = Column(Enum(BucketStatus), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    user = relationship("User", back_populates="buckets")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'type', name='unique_user_bucket_type'),
        CheckConstraint('target_amount >= 0', name='check_bucket_target_positive'),
        CheckConstraint('current_amount >= 0', name='check_bucket_current_positive'),
    )
    
    def __repr__(self):
        return f"<Bucket(id={self.id}, type={self.type}, status={self.status})>"


class Plan(Base):
    """Generated financial plans with recommendations."""
    __tablename__ = "plans"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    snapshot_id = Column(String(36), ForeignKey("financial_snapshots.id"), nullable=True)
    strategy_type = Column(String(100), nullable=True)
    monthly_saving_target = Column(Numeric(12, 2), nullable=True)
    monthly_invest_target = Column(Numeric(12, 2), nullable=True)
    top_actions = Column(JSON, nullable=False)  # List of action objects
    buckets = Column(JSON, nullable=False)  # Bucket allocations
    projections = Column(JSON, nullable=True)  # Timeline projections
    confidence_score = Column(Numeric(3, 2), nullable=True)  # 0.00 to 1.00
    rule_version = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="plans")
    snapshot = relationship("FinancialSnapshot", back_populates="plans")
    progress_records = relationship("MonthlyProgress", back_populates="plan")
    recommendation_logs = relationship("RecommendationLog", back_populates="plan")
    
    __table_args__ = (
        CheckConstraint('confidence_score >= 0 AND confidence_score <= 1', name='check_confidence_range'),
    )
    
    def __repr__(self):
        return f"<Plan(id={self.id}, user_id={self.user_id}, version={self.rule_version})>"


class MonthlyProgress(Base):
    """User self-reported monthly progress."""
    __tablename__ = "monthly_progress"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(String(36), ForeignKey("plans.id"), nullable=True)
    month = Column(Date, nullable=False)  # First day of month
    saved_amount = Column(Numeric(12, 2), default=0, nullable=False)
    invested_amount = Column(Numeric(12, 2), default=0, nullable=False)
    debt_paid = Column(Numeric(12, 2), default=0, nullable=False)
    notes = Column(String(500), nullable=True)
    status = Column(Enum(ProgressStatus), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="progress")
    plan = relationship("Plan", back_populates="progress_records")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'month', name='unique_user_month'),
        CheckConstraint('saved_amount >= 0', name='check_saved_positive'),
        CheckConstraint('invested_amount >= 0', name='check_invested_positive'),
        CheckConstraint('debt_paid >= 0', name='check_debt_paid_positive'),
    )
    
    def __repr__(self):
        return f"<MonthlyProgress(id={self.id}, month={self.month}, status={self.status})>"


class RecommendationLog(Base):
    """Audit trail for AI recommendations and explanations."""
    __tablename__ = "recommendation_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(String(36), ForeignKey("plans.id"), nullable=True)
    rule_version = Column(String(20), nullable=False)
    explanation_source_ids = Column(JSON, nullable=True)  # Document IDs from vector DB
    model_version = Column(String(50), nullable=True)  # LLM model used
    context_data = Column(JSON, nullable=True)  # Additional context
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    user = relationship("User")
    plan = relationship("Plan", back_populates="recommendation_logs")
    
    def __repr__(self):
        return f"<RecommendationLog(id={self.id}, rule_version={self.rule_version})>"
