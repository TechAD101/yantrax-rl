"""Simple authentication service using bcrypt"""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import hmac
import bcrypt

from db import get_session
from models import User


SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')


def is_legacy_hash(hashed: str) -> bool:
    """Check if the hash is a legacy SHA256 hash (64 hex characters)"""
    if len(hashed) == 64:
        try:
            int(hashed, 16)
            return True
        except ValueError:
            return False
    return False


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt or legacy SHA256 hash"""
    if is_legacy_hash(hashed):
        legacy_hash = hashlib.sha256(password.encode()).hexdigest()
        return hmac.compare_digest(legacy_hash, hashed)

    try:
        # bcrypt.checkpw expects bytes
        return bcrypt.checkpw(password.encode(), hashed.encode('utf-8'))
    except Exception:
        return False


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
        
        if verify_password(password, user.password_hash):
            # Optional: Migrate legacy hash to bcrypt on successful login
            if is_legacy_hash(user.password_hash):
                try:
                    user.password_hash = hash_password(password)
                    session.commit()
                except Exception:
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
