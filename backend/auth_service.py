"""Simple authentication service using bcrypt"""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import hmac

from db import get_session
from models import User


SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')


def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(username: str, email: str, password: str) -> Dict[str, Any]:
    """Register a new user"""
    session = get_session()
    try:
        # Check if user exists
        existing = session.query(User).filter((User.username == username) | (User.email == email)).first()
        if existing:
            raise ValueError("User already exists")
        
        pwd_hash = hash_password(password)
        user = User(username=username, email=email, password_hash=pwd_hash)
        session.add(user)
        session.commit()
        return user.to_dict()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user and return user info"""
    session = get_session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return None
        
        pwd_hash = hash_password(password)
        if pwd_hash == user.password_hash:
            return user.to_dict()
        return None
    finally:
        session.close()


def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    session = get_session()
    try:
        user = session.query(User).get(user_id)
        return user.to_dict() if user else None
    finally:
        session.close()
