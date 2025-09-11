from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import re


class LoginMethod(str, Enum):
    EMAIL = "email"
    USERNAME = "username"
    WALLET = "wallet"


class AuthProvider(str, Enum):
    LOCAL = "local"
    WALLET = "wallet"
    GOOGLE = "google"
    GITHUB = "github"


# Request Models
class LoginRequest(BaseModel):
    identifier: str = Field(..., description="Username, email, or wallet address")
    password: Optional[str] = Field(None, description="Password for email/username login")
    signature: Optional[str] = Field(None, description="Signature for wallet login")
    message: Optional[str] = Field(None, description="Message for wallet login")
    method: LoginMethod = LoginMethod.EMAIL


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    wallet_address: Optional[str] = None
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('wallet_address')
    def validate_wallet_address(cls, v):
        if v and not re.match(r'^0x[a-fA-F0-9]{40}$', v):
            raise ValueError('Invalid Ethereum address format')
        return v.lower() if v else None


class WalletLoginRequest(BaseModel):
    wallet_address: str = Field(..., min_length=42, max_length=42)
    signature: str = Field(..., description="Signed message")
    message: str = Field(..., description="Original message that was signed")
    
    @validator('wallet_address')
    def validate_wallet_address(cls, v):
        if not re.match(r'^0x[a-fA-F0-9]{40}$', v):
            raise ValueError('Invalid Ethereum address format')
        return v.lower()


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class ResetPasswordRequest(BaseModel):
    email: EmailStr


class ConfirmResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        # Same validation as above
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


# Response Models
class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class AuthResponse(BaseModel):
    success: bool
    message: str
    tokens: Optional[TokenPair] = None
    user: Optional[Dict[str, Any]] = None


class LogoutResponse(BaseModel):
    success: bool
    message: str


# JWT Payload Model
class TokenPayload(BaseModel):
    user_id: str
    username: str
    email: str
    role: str
    exp: datetime
    iat: datetime
    jti: str  # JWT ID for revocation


# Session Model (for Redis storage)
class UserSession(BaseModel):
    user_id: str
    username: str
    email: str
    role: str
    login_time: datetime
    last_activity: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True


# Password Hash Model (for storage)
class PasswordHash(BaseModel):
    user_id: str
    password_hash: str
    created_at: datetime
    updated_at: datetime
