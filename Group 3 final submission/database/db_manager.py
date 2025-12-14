from sqlalchemy.orm import Session
from database.models import User, Document, FinancialData, ChatHistory, SessionLocal
from datetime import datetime
from typing import Optional, List, Dict
import json

class DBManager:
    def __init__(self):
        self.session = SessionLocal()
    
    def __del__(self):
        self.session.close()
    
    # User operations
    def create_user(self, username: str, email: str, password_hash: str, 
                   full_name: str = None, phone: str = None) -> Optional[User]:
        """Create a new user"""
        try:
            user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                full_name=full_name,
                phone=phone
            )
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            return user
        except Exception as e:
            self.session.rollback()
            print(f"Error creating user: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            return self.session.query(User).filter(User.username == username).first()
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            return self.session.query(User).filter(User.email == email).first()
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            return self.session.query(User).filter(User.id == user_id).first()
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def update_user_login(self, user_id: int):
        """Update last login time"""
        try:
            user = self.get_user_by_id(user_id)
            if user:
                user.last_login = datetime.utcnow()
                self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"Error updating login: {e}")
    
    def update_user_profile(self, user_id: int, **kwargs):
        """Update user profile data"""
        try:
            user = self.get_user_by_id(user_id)
            if user:
                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            print(f"Error updating profile: {e}")
            return False
    
    # Document operations
    def add_document(self, user_id: int, document_type: str, 
                    file_name: str, file_path: str, metadata: Dict = None) -> Optional[Document]:
        """Add a document"""
        try:
            doc = Document(
                user_id=user_id,
                document_type=document_type,
                file_name=file_name,
                file_path=file_path,
                doc_metadata=json.dumps(metadata) if metadata else None  # Changed from metadata to doc_metadata
            )
            self.session.add(doc)
            self.session.commit()
            self.session.refresh(doc)
            
            # Update user document flags
            flag_name = f"has_{document_type}"
            if hasattr(User, flag_name):
                self.update_user_profile(user_id, **{flag_name: True})
            
            return doc
        except Exception as e:
            self.session.rollback()
            print(f"Error adding document: {e}")
            return None
    
    def get_user_documents(self, user_id: int, document_type: str = None) -> List[Document]:
        """Get user documents"""
        try:
            query = self.session.query(Document).filter(Document.user_id == user_id)
            if document_type:
                query = query.filter(Document.document_type == document_type)
            return query.all()
        except Exception as e:
            print(f"Error getting documents: {e}")
            return []
    
    # Financial data operations
    def add_financial_data(self, user_id: int, data_type: str, category: str,
                          amount: float, description: str = None, 
                          transaction_date: datetime = None,
                          source_document_id: int = None) -> Optional[FinancialData]:
        """Add financial data entry"""
        try:
            data = FinancialData(
                user_id=user_id,
                data_type=data_type,
                category=category,
                amount=amount,
                description=description,
                transaction_date=transaction_date or datetime.utcnow(),
                source_document_id=source_document_id
            )
            self.session.add(data)
            self.session.commit()
            self.session.refresh(data)
            return data
        except Exception as e:
            self.session.rollback()
            print(f"Error adding financial data: {e}")
            return None
    
    def get_financial_data(self, user_id: int, data_type: str = None,
                          start_date: datetime = None, end_date: datetime = None) -> List[FinancialData]:
        """Get financial data"""
        try:
            query = self.session.query(FinancialData).filter(FinancialData.user_id == user_id)
            if data_type:
                query = query.filter(FinancialData.data_type == data_type)
            if start_date:
                query = query.filter(FinancialData.transaction_date >= start_date)
            if end_date:
                query = query.filter(FinancialData.transaction_date <= end_date)
            return query.all()
        except Exception as e:
            print(f"Error getting financial data: {e}")
            return []
    
    # Chat history operations
    def add_chat_message(self, user_id: int, message: str, response: str = None,
                        agent_type: str = None) -> Optional[ChatHistory]:
        """Add chat message"""
        try:
            chat = ChatHistory(
                user_id=user_id,
                message=message,
                response=response,
                agent_type=agent_type
            )
            self.session.add(chat)
            self.session.commit()
            self.session.refresh(chat)
            return chat
        except Exception as e:
            self.session.rollback()
            print(f"Error adding chat message: {e}")
            return None
    
    def get_chat_history(self, user_id: int, limit: int = 50) -> List[ChatHistory]:
        """Get chat history"""
        try:
            return self.session.query(ChatHistory)\
                .filter(ChatHistory.user_id == user_id)\
                .order_by(ChatHistory.created_at.desc())\
                .limit(limit)\
                .all()
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []