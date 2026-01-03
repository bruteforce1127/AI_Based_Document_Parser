"""
Auth Service - JWT token handling for authentication
"""
import jwt
import bcrypt
from datetime import datetime, timedelta
import config


def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password, hashed):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def create_token(user_id, email, name):
    """Create a JWT token with 90-day validity"""
    payload = {
        'user_id': user_id,
        'email': email,
        'name': name,
        'exp': datetime.utcnow() + timedelta(days=config.JWT_EXPIRY_DAYS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)


def verify_token(token):
    """Verify a JWT token and return payload"""
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_user_from_token(token):
    """Extract user info from token"""
    payload = verify_token(token)
    if payload:
        return {
            'user_id': payload.get('user_id'),
            'email': payload.get('email'),
            'name': payload.get('name')
        }
    return None
