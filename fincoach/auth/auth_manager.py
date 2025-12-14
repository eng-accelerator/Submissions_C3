import bcrypt
from database.db_manager import DBManager
from typing import Optional, Tuple
import re

class AuthManager:
    def __init__(self):
        self.db = DBManager()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one digit"
        return True, "Password is strong"
    
    def register_user(self, username: str, email: str, password: str, 
                     full_name: str = None, phone: str = None) -> Tuple[bool, str]:
        """Register a new user"""
        # Validate inputs
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if not self.validate_email(email):
            return False, "Invalid email format"
        
        is_valid, msg = self.validate_password(password)
        if not is_valid:
            return False, msg
        
        # Check if user already exists
        if self.db.get_user_by_username(username):
            return False, "Username already exists"
        
        if self.db.get_user_by_email(email):
            return False, "Email already registered"
        
        # Hash password and create user
        password_hash = self.hash_password(password)
        user = self.db.create_user(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            phone=phone
        )
        
        if user:
            return True, "User registered successfully"
        else:
            return False, "Error creating user"
    
    def login_user(self, username_or_email: str, password: str) -> Tuple[bool, str, Optional[int]]:
        """Login a user"""
        # Try to find user by username or email
        user = self.db.get_user_by_username(username_or_email)
        if not user:
            user = self.db.get_user_by_email(username_or_email)
        
        if not user:
            return False, "User not found", None
        
        if not user.is_active:
            return False, "Account is deactivated", None
        
        # Verify password
        if not self.verify_password(password, user.password_hash):
            return False, "Invalid password", None
        
        # Update last login
        self.db.update_user_login(user.id)
        
        return True, "Login successful", user.id
    
    def get_user_info(self, user_id: int):
        """Get user information"""
        return self.db.get_user_by_id(user_id)
