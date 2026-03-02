import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import User

security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(user_id: int) -> str:
    """Create a JWT access token"""
    expires_delta = timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    expire = datetime.utcnow() + expires_delta
    
    payload = {
        "sub": str(user_id),
        "exp": expire
    }
    
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.ALGORITHM)
    return token


def decode_token(token: str) -> Optional[int]:
    """Decode a JWT token and return user_id"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub"))
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token"""
    token = credentials.credentials
    user_id = decode_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


def log_audit(db: Session, user_id: int, action: str, resource_type: str, 
              resource_id: Optional[int] = None, details: Optional[dict] = None):
    """Helper function to log audit entries"""
    from app.models import AuditLog
    
    audit_entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {}
    )
    db.add(audit_entry)
    db.commit()
