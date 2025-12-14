"""
Data service for CRUD operations on financial data.
Handles both guest mode (session state) and persistent storage (database).
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from models.database import get_db
from models.financial import FinancialSnapshot, Asset, Liability, Goal
from models.user import User


class DataService:
    """Service for managing financial data with dual mode: guest or persisted."""
    
    @staticmethod
    def save_snapshot(user_id: str, snapshot_data: Dict[str, Any]) -> bool:
        """
        Save financial snapshot to database.
        
        Args:
            user_id: User ID
            snapshot_data: Dict with monthly_income, monthly_expenses, current_savings
            
        Returns:
            True if saved successfully
        """
        db = next(get_db())
        
        try:
            # Check if snapshot already exists
            existing = db.query(FinancialSnapshot).filter(
                FinancialSnapshot.user_id == user_id
            ).order_by(FinancialSnapshot.snapshot_date.desc()).first()
            
            # Create new snapshot (versioned)
            snapshot = FinancialSnapshot(
                user_id=user_id,
                monthly_income=snapshot_data.get('monthly_income', 0),
                monthly_expenses=snapshot_data.get('monthly_expenses', 0),
                current_savings=snapshot_data.get('current_savings', 0),
                snapshot_date=datetime.utcnow()
            )
            
            db.add(snapshot)
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error saving snapshot: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def save_assets(user_id: str, assets: List[Dict[str, Any]]) -> bool:
        """Save user assets to database."""
        db = next(get_db())
        
        try:
            # Delete existing assets
            db.query(Asset).filter(Asset.user_id == user_id).delete()
            
            # Add new assets
            for asset_data in assets:
                asset = Asset(
                    user_id=user_id,
                    asset_type=asset_data.get('type', 'other'),
                    name=asset_data.get('name', 'Unnamed Asset'),
                    value=asset_data.get('value', 0)
                )
                db.add(asset)
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error saving assets: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def save_liabilities(user_id: str, liabilities: List[Dict[str, Any]]) -> bool:
        """Save user liabilities to database."""
        db = next(get_db())
        
        try:
            # Delete existing liabilities
            db.query(Liability).filter(Liability.user_id == user_id).delete()
            
            # Add new liabilities
            for liability_data in liabilities:
                liability = Liability(
                    user_id=user_id,
                    liability_type=liability_data.get('type', 'other'),
                    name=liability_data.get('name', 'Unnamed Debt'),
                    outstanding=liability_data.get('outstanding', 0),
                    interest_rate=liability_data.get('interest_rate', 0),
                    minimum_payment=liability_data.get('minimum_payment', 0)
                )
                db.add(liability)
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error saving liabilities: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def save_goals(user_id: str, goals: List[Dict[str, Any]]) -> bool:
        """Save user goals to database."""
        db = next(get_db())
        
        try:
            # Delete existing goals
            db.query(Goal).filter(Goal.user_id == user_id).delete()
            
            # Add new goals
            for goal_data in goals:
                goal = Goal(
                    user_id=user_id,
                    category=goal_data.get('category', 'other'),
                    name=goal_data.get('name', 'Unnamed Goal'),
                    target_amount=goal_data.get('target_amount', 0),
                    current_amount=goal_data.get('current_progress', 0),
                    target_date=datetime.strptime(goal_data.get('target_date'), '%Y-%m-%d') if goal_data.get('target_date') else None
                )
                db.add(goal)
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error saving goals: {e}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def load_user_data(user_id: str) -> Dict[str, Any]:
        """Load all financial data for a user from database."""
        db = next(get_db())
        
        try:
            # Get latest snapshot
            snapshot = db.query(FinancialSnapshot).filter(
                FinancialSnapshot.user_id == user_id
            ).order_by(FinancialSnapshot.snapshot_date.desc()).first()
            
            # Get assets
            assets = db.query(Asset).filter(Asset.user_id == user_id).all()
            
            # Get liabilities
            liabilities = db.query(Liability).filter(Liability.user_id == user_id).all()
            
            # Get goals
            goals = db.query(Goal).filter(Goal.user_id == user_id).all()
            
            return {
                'snapshot': {
                    'monthly_income': snapshot.monthly_income if snapshot else 0,
                    'monthly_expenses': snapshot.monthly_expenses if snapshot else 0,
                    'current_savings': snapshot.current_savings if snapshot else 0,
                } if snapshot else {},
                'assets': [
                    {
                        'type': asset.asset_type,
                        'name': asset.name,
                        'value': asset.value
                    } for asset in assets
                ],
                'liabilities': [
                    {
                        'type': liability.liability_type,
                        'name': liability.name,
                        'outstanding': liability.outstanding,
                        'interest_rate': liability.interest_rate
                    } for liability in liabilities
                ],
                'goals': [
                    {
                        'category': goal.category,
                        'name': goal.name,
                        'target_amount': goal.target_amount,
                        'current_progress': goal.current_amount,
                        'target_date': goal.target_date.strftime('%Y-%m-%d') if goal.target_date else None
                    } for goal in goals
                ]
            }
            
        except Exception as e:
            print(f"Error loading user data: {e}")
            return {'snapshot': {}, 'assets': [], 'liabilities': [], 'goals': []}
        finally:
            db.close()
