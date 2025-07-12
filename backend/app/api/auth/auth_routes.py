"""
Complete authentication and user management API routes
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, update
from pydantic import BaseModel, EmailStr, validator
import secrets
import logging

from ...database.connection import get_db_context
from ...database.models import User, UserRole, DocumentType
from ...security.auth import (
    AuthService, SessionManager, TokenBlacklist, RateLimiter,
    get_current_user, get_current_active_user, require_roles
)
from ...security.audit import audit_system, AuditEventType
from ...security.encryption import data_sanitizer, token_security
from ...config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])

# Rate limiting
rate_limiter = RateLimiter()


# Pydantic models
class UserRegistration(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Username must be between 3 and 50 characters')
        return data_sanitizer.sanitize_user_input(v)
    
    @validator('password')
    def validate_password(cls, v):
        strength = data_sanitizer.validate_password_strength(v)
        if not strength['is_strong']:
            raise ValueError(f'Password too weak: {strength["message"]}')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if not data_sanitizer.validate_email(v):
            raise ValueError('Invalid email format')
        return v.lower()


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class PasswordReset(BaseModel):
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        strength = data_sanitizer.validate_password_strength(v)
        if not strength['is_strong']:
            raise ValueError(f'Password too weak: {strength["message"]}')
        return v


class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        strength = data_sanitizer.validate_password_strength(v)
        if not strength['is_strong']:
            raise ValueError(f'Password too weak: {strength["message"]}')
        return v


class UserProfile(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    is_verified: bool
    subscription_tier: str
    monthly_usage: int
    monthly_limit: int
    created_at: datetime
    last_login: Optional[datetime]


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class SessionInfo(BaseModel):
    session_id: str
    created_at: str
    last_activity: str
    ip_address: Optional[str]
    user_agent: Optional[str]


@router.post("/register", response_model=TokenResponse)
async def register_user(
    user_data: UserRegistration,
    request: Request,
    response: Response
):
    """Register a new user"""
    
    # Rate limiting
    rate_limiter.rate_limit_middleware(limit=5, window=3600, per="ip")(request)
    
    try:
        async with get_db_context() as db:
            # Check if user already exists
            existing_user = await db.execute(
                select(User).where(
                    (User.email == user_data.email) | 
                    (User.username == user_data.username)
                )
            )
            
            if existing_user.scalar_one_or_none():
                await audit_system.log_event(
                    AuditEventType.LOGIN_FAILURE,
                    action="registration_failed",
                    details={"reason": "user_exists", "email": user_data.email},
                    ip_address=request.client.host
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email or username already exists"
                )
            
            # Create new user
            hashed_password = AuthService.get_password_hash(user_data.password)
            
            new_user = User(
                username=user_data.username,
                email=user_data.email,
                full_name=user_data.full_name,
                hashed_password=hashed_password,
                role=UserRole.USER,
                subscription_tier="free",
                monthly_limit=100,
                is_active=True,
                is_verified=False  # Require email verification
            )
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            # Create session
            session_data = {
                "ip_address": request.client.host,
                "user_agent": request.headers.get("user-agent", ""),
                "login_method": "registration"
            }
            session_id = SessionManager.create_session(new_user.id, session_data)
            
            # Generate tokens
            access_token = AuthService.create_access_token(
                data={"sub": str(new_user.id), "session_id": session_id}
            )
            refresh_token = AuthService.create_refresh_token(new_user.id)
            
            # Log successful registration
            await audit_system.log_user_activity(
                user_id=new_user.id,
                action="user_registration",
                resource_type="user",
                resource_id=str(new_user.id),
                details={"username": new_user.username, "email": new_user.email},
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent")
            )
            
            # Set secure cookie for session management
            response.set_cookie(
                key="session_id",
                value=session_id,
                max_age=7 * 24 * 3600,  # 7 days
                httponly=True,
                secure=not settings.DEVELOPMENT,
                samesite="strict"
            )
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=UserResponse(
                    id=new_user.id,
                    username=new_user.username,
                    email=new_user.email,
                    full_name=new_user.full_name,
                    role=new_user.role,
                    is_active=new_user.is_active,
                    is_verified=new_user.is_verified,
                    subscription_tier=new_user.subscription_tier,
                    monthly_usage=new_user.monthly_usage,
                    monthly_limit=new_user.monthly_limit,
                    created_at=new_user.created_at,
                    last_login=new_user.last_login
                )
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User registration failed: {e}")
        await audit_system.log_event(
            AuditEventType.SYSTEM_ERROR,
            action="registration_error",
            details={"error": str(e), "email": user_data.email},
            ip_address=request.client.host
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    login_data: UserLogin,
    request: Request,
    response: Response
):
    """Authenticate user and return tokens"""
    
    # Rate limiting
    rate_limiter.rate_limit_middleware(limit=10, window=3600, per="ip")(request)
    
    try:
        # Authenticate user
        user = await AuthService.authenticate_user(login_data.email, login_data.password)
        
        if not user:
            await audit_system.log_event(
                AuditEventType.LOGIN_FAILURE,
                action="login_failed",
                details={"reason": "invalid_credentials", "email": login_data.email},
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent")
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create session
        session_data = {
            "ip_address": request.client.host,
            "user_agent": request.headers.get("user-agent", ""),
            "login_method": "password",
            "remember_me": login_data.remember_me
        }
        session_id = SessionManager.create_session(user.id, session_data)
        
        # Generate tokens
        token_expires = timedelta(
            days=30 if login_data.remember_me else 1
        )
        access_token = AuthService.create_access_token(
            data={"sub": str(user.id), "session_id": session_id},
            expires_delta=token_expires
        )
        refresh_token = AuthService.create_refresh_token(user.id)
        
        # Log successful login
        await audit_system.log_event(
            AuditEventType.LOGIN_SUCCESS,
            user_id=user.id,
            action="login_success",
            details={"login_method": "password", "remember_me": login_data.remember_me},
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        
        # Set secure cookie
        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=30 * 24 * 3600 if login_data.remember_me else 24 * 3600,
            httponly=True,
            secure=not settings.DEVELOPMENT,
            samesite="strict"
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(token_expires.total_seconds()),
            user=UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                subscription_tier=user.subscription_tier,
                monthly_usage=user.monthly_usage,
                monthly_limit=user.monthly_limit,
                created_at=user.created_at,
                last_login=user.last_login
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {e}")
        await audit_system.log_event(
            AuditEventType.SYSTEM_ERROR,
            action="login_error",
            details={"error": str(e), "email": login_data.email},
            ip_address=request.client.host
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/logout")
async def logout_user(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_active_user)
):
    """Logout user and invalidate session"""
    
    try:
        # Get session ID from cookie or token
        session_id = request.cookies.get("session_id")
        
        if session_id:
            SessionManager.invalidate_session(session_id)
        
        # Clear cookies
        response.delete_cookie(key="session_id")
        
        # Log logout
        await audit_system.log_event(
            AuditEventType.LOGOUT,
            user_id=current_user.id,
            action="logout",
            details={"session_id": session_id},
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        subscription_tier=current_user.subscription_tier,
        monthly_usage=current_user.monthly_usage,
        monthly_limit=current_user.monthly_limit,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    profile_data: UserProfile,
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """Update user profile"""
    
    try:
        async with get_db_context() as db:
            # Check if username/email is already taken by another user
            existing_user = await db.execute(
                select(User).where(
                    ((User.email == profile_data.email) | 
                     (User.username == profile_data.username)) &
                    (User.id != current_user.id)
                )
            )
            
            if existing_user.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username or email already taken"
                )
            
            # Update user
            await db.execute(
                update(User)
                .where(User.id == current_user.id)
                .values(
                    username=profile_data.username,
                    email=profile_data.email,
                    full_name=profile_data.full_name
                )
            )
            await db.commit()
            
            # Refresh user object
            await db.refresh(current_user)
            
            # Log profile update
            await audit_system.log_data_access(
                user_id=current_user.id,
                data_type="user_profile",
                data_id=str(current_user.id),
                operation="update",
                details={
                    "updated_fields": ["username", "email", "full_name"],
                    "new_values": {
                        "username": profile_data.username,
                        "email": profile_data.email,
                        "full_name": profile_data.full_name
                    }
                },
                ip_address=request.client.host
            )
            
            return UserResponse(
                id=current_user.id,
                username=current_user.username,
                email=current_user.email,
                full_name=current_user.full_name,
                role=current_user.role,
                is_active=current_user.is_active,
                is_verified=current_user.is_verified,
                subscription_tier=current_user.subscription_tier,
                monthly_usage=current_user.monthly_usage,
                monthly_limit=current_user.monthly_limit,
                created_at=current_user.created_at,
                last_login=current_user.last_login
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """Change user password"""
    
    try:
        # Verify current password
        if not AuthService.verify_password(
            password_data.current_password, 
            current_user.hashed_password
        ):
            await audit_system.log_event(
                AuditEventType.SUSPICIOUS_ACTIVITY,
                user_id=current_user.id,
                action="password_change_failed",
                details={"reason": "incorrect_current_password"},
                ip_address=request.client.host
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Hash new password
        new_hashed_password = AuthService.get_password_hash(password_data.new_password)
        
        async with get_db_context() as db:
            # Update password
            await db.execute(
                update(User)
                .where(User.id == current_user.id)
                .values(hashed_password=new_hashed_password)
            )
            await db.commit()
            
            # Invalidate all user sessions except current
            SessionManager.invalidate_all_user_sessions(current_user.id)
            
            # Log password change
            await audit_system.log_event(
                AuditEventType.PASSWORD_CHANGE,
                user_id=current_user.id,
                action="password_changed",
                details={"forced_logout_all_sessions": True},
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent")
            )
            
            return {"message": "Password changed successfully"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.get("/sessions")
async def get_user_sessions(
    current_user: User = Depends(get_current_active_user)
):
    """Get user's active sessions"""
    
    try:
        sessions = SessionManager.get_active_sessions(current_user.id)
        return {
            "sessions": [
                SessionInfo(
                    session_id=session["session_id"],
                    created_at=session["created_at"],
                    last_activity=session["last_activity"],
                    ip_address=session.get("ip_address"),
                    user_agent=session.get("user_agent")
                )
                for session in sessions
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sessions"
        )


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """Revoke a specific session"""
    
    try:
        # Verify session belongs to user
        session_data = SessionManager.get_session(session_id)
        if not session_data or int(session_data.get("user_id", 0)) != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Invalidate session
        SessionManager.invalidate_session(session_id)
        
        # Log session revocation
        await audit_system.log_event(
            AuditEventType.LOGOUT,
            user_id=current_user.id,
            action="session_revoked",
            details={"revoked_session_id": session_id},
            ip_address=request.client.host
        )
        
        return {"message": "Session revoked successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session revocation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session revocation failed"
        )


@router.delete("/sessions")
async def revoke_all_sessions(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """Revoke all user sessions"""
    
    try:
        # Invalidate all sessions
        SessionManager.invalidate_all_user_sessions(current_user.id)
        
        # Log session revocation
        await audit_system.log_event(
            AuditEventType.LOGOUT,
            user_id=current_user.id,
            action="all_sessions_revoked",
            details={"reason": "user_requested"},
            ip_address=request.client.host
        )
        
        return {"message": "All sessions revoked successfully"}
        
    except Exception as e:
        logger.error(f"All sessions revocation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session revocation failed"
        )


# Admin endpoints
@router.get("/users", dependencies=[Depends(require_roles(UserRole.ADMIN))])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
):
    """List all users (admin only)"""
    
    try:
        async with get_db_context() as db:
            result = await db.execute(
                select(User)
                .offset(skip)
                .limit(limit)
                .order_by(User.created_at.desc())
            )
            users = result.scalars().all()
            
            return {
                "users": [
                    UserResponse(
                        id=user.id,
                        username=user.username,
                        email=user.email,
                        full_name=user.full_name,
                        role=user.role,
                        is_active=user.is_active,
                        is_verified=user.is_verified,
                        subscription_tier=user.subscription_tier,
                        monthly_usage=user.monthly_usage,
                        monthly_limit=user.monthly_limit,
                        created_at=user.created_at,
                        last_login=user.last_login
                    )
                    for user in users
                ]
            }
            
    except Exception as e:
        logger.error(f"Failed to list users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )


@router.put("/users/{user_id}/role", dependencies=[Depends(require_roles(UserRole.ADMIN))])
async def update_user_role(
    user_id: int,
    new_role: UserRole,
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    """Update user role (admin only)"""
    
    try:
        async with get_db_context() as db:
            # Get target user
            result = await db.execute(select(User).where(User.id == user_id))
            target_user = result.scalar_one_or_none()
            
            if not target_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            old_role = target_user.role
            
            # Update role
            await db.execute(
                update(User)
                .where(User.id == user_id)
                .values(role=new_role)
            )
            await db.commit()
            
            # Log role change
            await audit_system.log_event(
                AuditEventType.PERMISSION_ESCALATION,
                user_id=current_user.id,
                action="user_role_changed",
                resource_type="user",
                resource_id=str(user_id),
                details={
                    "target_user": target_user.username,
                    "old_role": old_role.value,
                    "new_role": new_role.value,
                    "changed_by": current_user.username
                },
                ip_address=request.client.host
            )
            
            return {"message": f"User role updated to {new_role.value}"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user role"
        )