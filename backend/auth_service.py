"""Simple authentication service using bcrypt"""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
from passlib.context import CryptContext

from db import get_session
from models import User


SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Setup Password Context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt. Support legacy SHA256 hashes."""
    # Check if it looks like a bcrypt hash (starts with $2b$, $2a$, etc.)
    if hashed_password.startswith('$'):
        return pwd_context.verify(plain_password, hashed_password)
    else:
        # Legacy SHA256 support
        legacy_hash = hashlib.sha256(plain_password.encode()).hexdigest()
        return legacy_hash == hashed_password


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
    """Authenticate user and return user info. Upgrades legacy hashes."""
    session = get_session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return None
        
        if verify_password(password, user.password_hash):
            # Upgrade legacy hash to bcrypt if needed
            if not user.password_hash.startswith('$'):
                try:
                    user.password_hash = hash_password(password)
                    session.commit()
                except Exception:
                    # Log but continue if migration fails
                    session.rollback()
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
