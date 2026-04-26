"""
Authentication utilities for the application
"""
import hashlib
import bcrypt

def hash_password(password):
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password, password_hash):
    """Verify password against bcrypt hash"""
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except Exception:
        # Fallback for old SHA-256 hashes
        return hashlib.sha256(password.encode()).hexdigest() == password_hash

def validate_email(email):
    """Basic email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username):
    """Validate username (alphanumeric, 3-20 chars)"""
    import re
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username) is not None