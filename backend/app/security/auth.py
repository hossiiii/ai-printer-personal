"""
Advanced authentication and authorization system
"""
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis
import logging
from ..config import settings
from ..database.models import User, UserRole
from ..database.connection import get_db_context
from .encryption import EncryptionService
from .audit import AuditLogger

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

# Redis client for session management
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

# Security utilities
security = HTTPBearer(auto_error=False)
encryption_service = EncryptionService()
audit_logger = AuditLogger()


class AuthenticationError(Exception):
    """Authentication related errors"""
    pass


class AuthorizationError(Exception):
    """Authorization related errors"""
    pass


class TokenBlacklist:
    """Manage blacklisted tokens"""
    
    @staticmethod
    def blacklist_token(jti: str, exp: int):
        """Add token to blacklist"""
        ttl = exp - int(time.time())
        if ttl > 0:
            redis_client.setex(f"blacklist:{jti}", ttl, "1")
    
    @staticmethod
    def is_blacklisted(jti: str) -> bool:
        """Check if token is blacklisted"""
        return redis_client.exists(f"blacklist:{jti}")


class SessionManager:
    """Manage user sessions with Redis"""
    
    @staticmethod
    def create_session(user_id: int, session_data: Dict[str, Any]) -> str:
        """Create a new user session"""
        session_id = f"session:{user_id}:{int(time.time())}"
        session_data.update({
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "user_id": user_id
        })
        
        # Store session with 7-day expiry
        redis_client.hmset(session_id, session_data)
        redis_client.expire(session_id, 7 * 24 * 3600)
        
        # Track active sessions for user
        redis_client.sadd(f"user_sessions:{user_id}", session_id)
        redis_client.expire(f"user_sessions:{user_id}", 7 * 24 * 3600)
        
        return session_id
    
    @staticmethod
    def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        session_data = redis_client.hgetall(session_id)
        if session_data:
            # Update last activity
            redis_client.hset(session_id, "last_activity", datetime.utcnow().isoformat())
            return session_data
        return None
    
    @staticmethod
    def invalidate_session(session_id: str):
        """Invalidate a specific session"""
        session_data = redis_client.hgetall(session_id)
        if session_data and "user_id" in session_data:
            user_id = session_data["user_id"]
            redis_client.srem(f"user_sessions:{user_id}", session_id)
        redis_client.delete(session_id)
    
    @staticmethod
    def invalidate_all_user_sessions(user_id: int):
        """Invalidate all sessions for a user"""
        session_ids = redis_client.smembers(f"user_sessions:{user_id}")
        for session_id in session_ids:
            redis_client.delete(session_id)
        redis_client.delete(f"user_sessions:{user_id}")
    
    @staticmethod
    def get_active_sessions(user_id: int) -> List[Dict[str, Any]]:
        """Get all active sessions for a user"""
        session_ids = redis_client.smembers(f"user_sessions:{user_id}")
        sessions = []
        for session_id in session_ids:
            session_data = redis_client.hgetall(session_id)
            if session_data:
                sessions.append({**session_data, "session_id": session_id})
        return sessions


class AuthService:
    """Advanced authentication service"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": f"{data.get('sub', 'unknown')}_{int(time.time())}"
        })
        
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """Create JWT refresh token"""
        data = {
            "sub": str(user_id),
            "type": "refresh",
            "exp": datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            "iat": datetime.utcnow(),
            "jti": f"refresh_{user_id}_{int(time.time())}"
        }
        
        encoded_jwt = jwt.encode(data, settings.JWT_SECRET_KEY, algorithm="HS256")
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
            
            # Check if token is blacklisted
            jti = payload.get("jti")
            if jti and TokenBlacklist.is_blacklisted(jti):
                raise AuthenticationError("Token has been revoked")
            
            return payload
            
        except JWTError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")
    
    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        async with get_db_context() as db:
            from sqlalchemy import select
            
            result = await db.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return None
            
            if not AuthService.verify_password(password, user.hashed_password):
                return None
            
            if not user.is_active:
                raise AuthenticationError("Account is disabled")
            
            # Update last login
            user.last_login = datetime.utcnow()
            await db.commit()
            
            return user
    
    @staticmethod
    async def get_current_user(
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> User:
        """Get current authenticated user"""
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        try:
            payload = AuthService.verify_token(credentials.credentials)
            user_id = int(payload.get("sub"))
            
            if not user_id:
                raise AuthenticationError("Invalid token payload")
            
            # Get user from database
            async with get_db_context() as db:
                from sqlalchemy import select
                
                result = await db.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    raise AuthenticationError("User not found")
                
                if not user.is_active:
                    raise AuthenticationError("Account is disabled")
                
                # Log user activity
                audit_logger.log_user_activity(
                    user_id=user.id,
                    action="api_access",
                    resource_type="api",
                    details={"endpoint": request.url.path, "method": request.method},
                    ip_address=request.client.host,
                    user_agent=request.headers.get("user-agent")
                )
                
                return user
                
        except (JWTError, AuthenticationError) as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"}
            )


class AuthorizationService:
    """Role-based access control"""
    
    @staticmethod
    def require_role(required_role: UserRole):
        """Decorator to require specific user role"""
        def role_checker(current_user: User = Depends(AuthService.get_current_user)):
            if current_user.role != required_role and current_user.role != UserRole.ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            return current_user
        return role_checker
    
    @staticmethod
    def require_admin():
        """Require admin role"""
        return AuthorizationService.require_role(UserRole.ADMIN)
    
    @staticmethod
    def require_premium():
        """Require premium or admin role"""
        def premium_checker(current_user: User = Depends(AuthService.get_current_user)):
            if current_user.role not in [UserRole.PREMIUM, UserRole.ADMIN]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Premium subscription required"
                )
            return current_user
        return premium_checker
    
    @staticmethod
    def check_resource_ownership(user: User, resource_user_id: int) -> bool:
        """Check if user owns the resource"""
        return user.id == resource_user_id or user.role == UserRole.ADMIN
    
    @staticmethod
    def require_ownership():
        """Require resource ownership"""
        def ownership_checker(
            resource_user_id: int,
            current_user: User = Depends(AuthService.get_current_user)
        ):
            if not AuthorizationService.check_resource_ownership(current_user, resource_user_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: resource ownership required"
                )
            return current_user
        return ownership_checker


class RateLimiter:
    """Rate limiting service"""
    
    @staticmethod
    def check_rate_limit(
        key: str,
        limit: int,
        window: int = 3600,
        identifier: str = "default"
    ) -> Dict[str, Any]:
        """Check if rate limit is exceeded"""
        cache_key = f"rate_limit:{identifier}:{key}"
        
        try:
            current = redis_client.get(cache_key)
            if current is None:
                # First request in window
                redis_client.setex(cache_key, window, 1)
                return {
                    "allowed": True,
                    "count": 1,
                    "limit": limit,
                    "reset_time": int(time.time()) + window
                }
            
            current_count = int(current)
            if current_count >= limit:
                ttl = redis_client.ttl(cache_key)
                return {
                    "allowed": False,
                    "count": current_count,
                    "limit": limit,
                    "reset_time": int(time.time()) + ttl
                }
            
            # Increment counter
            redis_client.incr(cache_key)
            ttl = redis_client.ttl(cache_key)
            
            return {
                "allowed": True,
                "count": current_count + 1,
                "limit": limit,
                "reset_time": int(time.time()) + ttl
            }
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # Allow request if rate limiting fails
            return {
                "allowed": True,
                "count": 0,
                "limit": limit,
                "reset_time": int(time.time()) + window
            }
    
    @staticmethod
    def rate_limit_middleware(
        limit: int = 60,
        window: int = 3600,
        per: str = "ip"
    ):
        """Rate limiting middleware"""
        def rate_limiter(request: Request, current_user: User = None):
            if per == "user" and current_user:
                identifier = f"user:{current_user.id}"
            else:
                identifier = f"ip:{request.client.host}"
            
            result = RateLimiter.check_rate_limit(
                key=request.url.path,
                limit=limit,
                window=window,
                identifier=identifier
            )
            
            if not result["allowed"]:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                    headers={
                        "X-RateLimit-Limit": str(result["limit"]),
                        "X-RateLimit-Remaining": str(max(0, result["limit"] - result["count"])),
                        "X-RateLimit-Reset": str(result["reset_time"])
                    }
                )
            
            return result
        
        return rate_limiter


# Dependency functions
async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    """Dependency to get current authenticated user"""
    return await AuthService.get_current_user(request, credentials)


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_roles(*roles: UserRole):
    """Dependency to require specific roles"""
    def role_dependency(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in roles and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_dependency


# Export main dependencies
__all__ = [
    "AuthService",
    "AuthorizationService",
    "SessionManager",
    "TokenBlacklist",
    "RateLimiter",
    "get_current_user",
    "get_current_active_user",
    "require_roles"
]