import strawberry
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

from app.models import LoginMethod, AuthProvider


@strawberry.enum
class LoginMethodEnum(Enum):
    EMAIL = "email"
    USERNAME = "username" 
    WALLET = "wallet"


@strawberry.enum
class AuthProviderEnum(Enum):
    LOCAL = "local"
    WALLET = "wallet"
    GOOGLE = "google"
    GITHUB = "github"


# Input Types
@strawberry.input
class RegisterInput:
    username: str
    email: str
    password: str
    confirm_password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    wallet_address: Optional[str] = None


@strawberry.input
class LoginInput:
    identifier: str  # username, email, or wallet address
    password: Optional[str] = None  # for email/username login
    signature: Optional[str] = None  # for wallet login
    message: Optional[str] = None  # for wallet login  
    method: LoginMethodEnum = LoginMethodEnum.EMAIL


@strawberry.input
class WalletLoginInput:
    wallet_address: str
    signature: str
    message: str


@strawberry.input
class RefreshTokenInput:
    refresh_token: str


@strawberry.input 
class ChangePasswordInput:
    current_password: str
    new_password: str
    confirm_password: str


# Response Types
@strawberry.type
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


@strawberry.type
class UserInfo:
    id: str
    username: str
    email: str
    role: str
    status: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


@strawberry.type
class AuthResponse:
    success: bool
    message: str
    tokens: Optional[TokenPair] = None
    user: Optional[UserInfo] = None


@strawberry.type
class LogoutResponse:
    success: bool
    message: str


@strawberry.type
class MeResponse:
    id: str
    username: str
    email: str
    role: str
    status: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    login_time: Optional[datetime] = None
    last_activity: Optional[datetime] = None


@strawberry.type
class HealthResponse:
    status: str
    service: str
    redis_connected: bool
    user_service_connected: bool
