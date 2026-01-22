"""
JWT Authentication for I-Intern integration
"""
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import jwt
from datetime import datetime

from config import settings
from models import get_db
from models.database import Base
from models.multi_tenant import User, UserRole

# Security scheme
security = HTTPBearer(auto_error=False)


class CurrentUser:
    """Current authenticated user"""
    def __init__(
        self,
        id: int,
        i_intern_user_id: str,
        email: str,
        name: str,
        role: UserRole,
        company_id: Optional[int] = None
    ):
        self.id = id
        self.i_intern_user_id = i_intern_user_id
        self.email = email
        self.name = name
        self.role = role
        self.company_id = company_id
    
    def is_student(self) -> bool:
        return self.role == UserRole.STUDENT
    
    def is_recruiter(self) -> bool:
        return self.role == UserRole.RECRUITER
    
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN


def decode_i_intern_token(token: str) -> dict:
    """
    Decode JWT token from I-Intern platform
    
    Expected token payload:
    {
        "user_id": "123",
        "email": "user@example.com",
        "name": "John Doe",
        "role": "student" | "recruiter",
        "company_id": "456" (optional, for recruiters),
        "exp": 1234567890
    }
    """
    try:
        # Debug logging
        print(f"[AUTH] Attempting to decode token")
        print(f"[AUTH] JWT_SECRET: {settings.JWT_SECRET[:20]}...")
        print(f"[AUTH] JWT_ALGORITHM: {settings.JWT_ALGORITHM}")
        print(f"[AUTH] Token (first 50 chars): {token[:50]}...")
        
        # Decode token
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        print(f"[AUTH] Token decoded successfully: {payload}")
        return payload
    except jwt.ExpiredSignatureError as e:
        print(f"[AUTH ERROR] Token expired: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        print(f"[AUTH ERROR] Invalid token: {e}")
        print(f"[AUTH ERROR] Error type: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


def get_or_create_user(db: Session, token_payload: dict) -> User:
    """Get existing user or create from token payload"""
    i_intern_user_id = str(token_payload["user_id"])
    
    # Check if user exists
    user = db.query(User).filter(User.i_intern_user_id == i_intern_user_id).first()
    
    if not user:
        # Create new user from token
        user = User(
            i_intern_user_id=i_intern_user_id,
            email=token_payload["email"],
            name=token_payload["name"],
            role=UserRole(token_payload["role"]),
            company_id=token_payload.get("company_id")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
    
    return user


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[CurrentUser]:
    """
    Get current authenticated user from JWT token
    Returns None if no token provided (allows public access)
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = decode_i_intern_token(token)
    
    # Get or create user in database
    user = get_or_create_user(db, payload)
    
    return CurrentUser(
        id=user.id,
        i_intern_user_id=user.i_intern_user_id,
        email=user.email,
        name=user.name,
        role=user.role,
        company_id=user.company_id
    )


async def require_auth(
    current_user: Optional[CurrentUser] = Depends(get_current_user)
) -> CurrentUser:
    """Require authentication - raise error if not authenticated"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return current_user


async def require_student(
    current_user: CurrentUser = Depends(require_auth)
) -> CurrentUser:
    """Require student role"""
    if not current_user.is_student():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student access required"
        )
    return current_user


async def require_recruiter(
    current_user: CurrentUser = Depends(require_auth)
) -> CurrentUser:
    """Require recruiter role"""
    if not current_user.is_recruiter():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Recruiter access required"
        )
    return current_user


async def require_admin(
    current_user: CurrentUser = Depends(require_auth)
) -> CurrentUser:
    """Require admin role"""
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def require_recruiter_or_admin(
    current_user: CurrentUser = Depends(require_auth)
) -> CurrentUser:
    """Require recruiter or admin role (for job description management)"""
    if not (current_user.is_recruiter() or current_user.is_admin()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Recruiter or admin access required"
        )
    return current_user
