import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import redis.asyncio as redis

from app.config import settings
from app.models import TokenPayload, TokenPair, UserSession
from app.database import get_redis

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTService:
    """JWT Token Management Service"""
    
    @staticmethod
    def create_access_token(
        user_id: str,
        username: str, 
        email: str,
        role: str
    ) -> str:
        """Create JWT access token"""
        now = datetime.utcnow()
        expire = now + timedelta(minutes=settings.access_token_expire_minutes)
        
        payload = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "role": role,
            "exp": expire,
            "iat": now,
            "type": "access",
            "jti": str(uuid.uuid4())  # JWT ID for revocation
        }
        
        return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    
    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """Create JWT refresh token"""
        now = datetime.utcnow()
        expire = now + timedelta(days=settings.refresh_token_expire_days)
        
        payload = {
            "user_id": user_id,
            "exp": expire,
            "iat": now,
            "type": "refresh",
            "jti": str(uuid.uuid4())
        }
        
        return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    
    @staticmethod
    async def create_token_pair(
        user_id: str,
        username: str,
        email: str, 
        role: str
    ) -> TokenPair:
        """Create access + refresh token pair"""
        access_token = JWTService.create_access_token(user_id, username, email, role)
        refresh_token = JWTService.create_refresh_token(user_id)
        
        # Store refresh token in Redis
        redis_client = await get_redis()
        refresh_key = f"{settings.redis_refresh_prefix}{user_id}"
        await redis_client.setex(
            refresh_key, 
            settings.refresh_token_expire_days * 24 * 3600,  # seconds
            refresh_token
        )
        
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60
        )
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(
                token, 
                settings.secret_key, 
                algorithms=[settings.algorithm]
            )
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def verify_access_token(token: str) -> Optional[TokenPayload]:
        """Verify access token and return payload"""
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm]
            )
            
            # Check token type
            if payload.get("type") != "access":
                return None
            
            # Check expiration
            exp = payload.get("exp")
            if not exp or datetime.utcnow() > datetime.fromtimestamp(exp):
                return None
            
            return TokenPayload(
                user_id=payload.get("user_id"),
                username=payload.get("username"),
                email=payload.get("email"),
                role=payload.get("role"),
                exp=datetime.fromtimestamp(exp),
                iat=datetime.fromtimestamp(payload.get("iat")),
                jti=payload.get("jti")
            )
            
        except JWTError:
            return None
    
    @staticmethod
    async def verify_refresh_token(token: str) -> Optional[str]:
        """Verify refresh token and return user_id"""
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm]
            )
            
            # Check token type
            if payload.get("type") != "refresh":
                return None
            
            user_id = payload.get("user_id")
            if not user_id:
                return None
            
            # Check if token exists in Redis
            redis_client = await get_redis()
            refresh_key = f"{settings.redis_refresh_prefix}{user_id}"
            stored_token = await redis_client.get(refresh_key)
            
            if stored_token != token:
                return None
            
            return user_id
            
        except JWTError:
            return None
    
    @staticmethod
    async def revoke_refresh_token(user_id: str):
        """Revoke refresh token for user"""
        redis_client = await get_redis()
        refresh_key = f"{settings.redis_refresh_prefix}{user_id}"
        await redis_client.delete(refresh_key)
    
    @staticmethod
    async def revoke_all_tokens(user_id: str):
        """Revoke all tokens for user"""
        redis_client = await get_redis()
        
        # Delete refresh token
        refresh_key = f"{settings.redis_refresh_prefix}{user_id}"
        await redis_client.delete(refresh_key)
        
        # Delete user session
        session_key = f"{settings.redis_token_prefix}{user_id}"
        await redis_client.delete(session_key)
    
    @staticmethod
    async def store_user_session(
        user_id: str,
        username: str,
        email: str,
        role: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Store user session in Redis"""
        session = UserSession(
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            login_time=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
            is_active=True
        )
        
        redis_client = await get_redis()
        session_key = f"{settings.redis_token_prefix}{user_id}"
        
        await redis_client.setex(
            session_key,
            settings.access_token_expire_minutes * 60,  # Same as access token expiry
            session.json()
        )
    
    @staticmethod
    async def get_user_session(user_id: str) -> Optional[UserSession]:
        """Get user session from Redis"""
        redis_client = await get_redis()
        session_key = f"{settings.redis_token_prefix}{user_id}"
        
        session_data = await redis_client.get(session_key)
        if session_data:
            return UserSession.parse_raw(session_data)
        
        return None
    
    @staticmethod
    async def update_user_activity(user_id: str):
        """Update user last activity"""
        session = await JWTService.get_user_session(user_id)
        if session:
            session.last_activity = datetime.utcnow()
            
            redis_client = await get_redis()
            session_key = f"{settings.redis_token_prefix}{user_id}"
            
            await redis_client.setex(
                session_key,
                settings.access_token_expire_minutes * 60,
                session.json()
            )
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)
