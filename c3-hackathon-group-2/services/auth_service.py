"""
Authentication service for user registration, login, and session management.

This service handles all authentication logic in standalone Streamlit architecture.
Uses SQLAlchemy for database access and session-based authentication.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from models.database import get_db, init_db
from models.user import User, UserProfile
from models.financial import FinancialSnapshot, Asset, Liability, Goal, AssetType, LiabilityType, GoalCategory
from utils.security import hash_password, verify_password


class AuthService:
    """Authentication service for user management."""
    
    @staticmethod
    def register_user(email: str, password: str, name: str) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            email: User email address
            password: Plain text password (will be hashed)
            name: User's full name
            
        Returns:
            Dictionary with user data or error
            
        Raises:
            ValueError: If email already exists or validation fails
        """
        # Validate inputs
        if not email or not password or not name:
            raise ValueError("All fields are required")
        
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        # Get database session
        db = next(get_db())
        
        try:
            # Check if email exists
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                raise ValueError("Email already registered")
            
            # Create new user
            new_user = User(
                email=email,
                password_hash=hash_password(password),
                name=name
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            return {
                "success": True,
                "user_id": new_user.id,
                "email": new_user.email,
                "name": new_user.name
            }
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    @staticmethod
    def login_user(email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and create session.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            Dictionary with user data or error
            
        Raises:
            ValueError: If credentials are invalid
        """
        if not email or not password:
            raise ValueError("Email and password are required")
        
        db = next(get_db())
        
        try:
            # Find user
            user = db.query(User).filter(User.email == email).first()
            
            if not user or not verify_password(password, user.password_hash):
                raise ValueError("Invalid email or password")
            
            # Update last login
            user.last_login_at = datetime.utcnow()
            db.commit()
            
            return {
                "success": True,
                "user_id": user.id,
                "email": user.email,
                "name": user.name
            }
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    @staticmethod
    def get_user(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User data dictionary or None
        """
        db = next(get_db())
        
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return None
            
            return {
                "user_id": user.id,
                "email": user.email,
                "name": user.name,
                "created_at": user.created_at
            }
            
        finally:
    @staticmethod
    def get_or_create_guest(guest_id: str) -> Dict[str, Any]:
        """
        Get existing guest or create new one.
        
        Args:
            guest_id: UUID from browser cookie
            
        Returns:
            User data dictionary
        """
        db = next(get_db())
        
        try:
            # Try to find by ID
            user = db.query(User).filter(User.id == guest_id).first()
            
            if user:
                # Update last login
                user.last_login_at = datetime.utcnow()
                db.commit()
            else:
                # Create new guest user
                # We need dummy values for required fields
                user = User(
                    id=guest_id,
                    email=f"guest_{guest_id}@anon.com",
                    password_hash="guest_access", # Dummy hash
                    name="Guest User",
                    is_guest=1
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            
            return {
                "user_id": user.id,
                "email": user.email,
                "name": user.name,
                "is_guest": True
            }
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    @staticmethod
    def save_guest_data(user_id: str, data: Dict[str, Any]) -> bool:
        """
        Save guest financial data to database.
        Full replacement strategy for MVP (simplest sync).
        """
        db = next(get_db())
        try:
            # 1. Update/Create Snapshot
            db.query(FinancialSnapshot).filter(FinancialSnapshot.user_id == user_id).delete()
            db.query(Asset).filter(Asset.user_id == user_id).delete()
            db.query(Liability).filter(Liability.user_id == user_id).delete()
            db.query(Goal).filter(Goal.user_id == user_id).delete()
            
            # 2. Insert Snapshot
            snap_data = data.get("snapshot", {})
            if snap_data:
                snapshot = FinancialSnapshot(
                    user_id=user_id,
                    monthly_income=snap_data.get("income", 0),
                    monthly_expenses=snap_data.get("expenses", 0),
                    current_savings=snap_data.get("savings", 0)
                )
                db.add(snapshot)
            
            # 3. Insert Assets
            for a in data.get("assets", []):
                asset = Asset(
                    user_id=user_id,
                    type=a.get("type", "other"),
                    name=a.get("name", "Unnamed Asset"),
                    current_value=a.get("value", 0)
                )
                db.add(asset)
                
            # 4. Insert Liabilities
            for l in data.get("liabilities", []):
                liabilities = Liability(
                    user_id=user_id,
                    type=l.get("type", "other"),
                    name=l.get("name", "Unnamed Debt"),
                    outstanding_amount=l.get("amount", 0),
                    interest_rate=l.get("interest_rate", 0) / 100.0 if l.get("interest_rate", 0) > 1 else l.get("interest_rate", 0)
                )
                db.add(liabilities)
                
            # 5. Insert Goals
            for g in data.get("goals", []):
                goal = Goal(
                    user_id=user_id,
                    name=g.get("name", "Goal"),
                    target_amount=g.get("amount", 0),
                    target_date=datetime.strptime(g.get("date"), "%Y-%m-%d") if isinstance(g.get("date"), str) else datetime.now(),
                    category=g.get("category", "short_term")
                )
                db.add(goal)
                
            db.commit()
            return True
        except Exception as e:
            print(f"Error saving guest data: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    @staticmethod
    def load_guest_data(user_id: str) -> Dict[str, Any]:
        """Load guest data from DB to session state format."""
        db = next(get_db())
        try:
            snapshot = db.query(FinancialSnapshot).filter(FinancialSnapshot.user_id == user_id).first()
            assets = db.query(Asset).filter(Asset.user_id == user_id).all()
            liabilities = db.query(Liability).filter(Liability.user_id == user_id).all()
            goals = db.query(Goal).filter(Goal.user_id == user_id).all()
            
            if not snapshot and not assets:
                return {} # No data found
                
            return {
                "snapshot": {
                    "income": float(snapshot.monthly_income) if snapshot else 0,
                    "expenses": float(snapshot.monthly_expenses) if snapshot else 0,
                    "savings": float(snapshot.current_savings) if snapshot else 0
                },
                "assets": [
                    {"type": a.type.value, "name": a.name, "value": float(a.current_value)} for a in assets
                ],
                "liabilities": [
                    {"type": l.type.value, "name": l.name, "amount": float(l.outstanding_amount), "interest_rate": float(l.interest_rate)*100} for l in liabilities
                ],
                "goals": [
                    {"name": g.name, "amount": float(g.target_amount), "date": g.target_date.strftime("%Y-%m-%d") if g.target_date else None, "category": g.category.value} for g in goals
                ],
                "analysis": {} 
            }
        except Exception as e:
            print(f"Error loading data: {e}")
            return {}
        finally:
            db.close()
