from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
import re


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"
    PENDING = "pending"


class SocialLinks(BaseModel):
    twitter: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None
    
    @validator('twitter', 'linkedin', 'github', 'website')
    def validate_urls(cls, v):
        if v and not re.match(r'^https?://', v):
            raise ValueError('URL must start with http:// or https://')
        return v


class UserProfile(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    cover_url: Optional[str] = None
    location: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, regex=r'^\+?1?\d{9,15}$')
    social_links: Optional[SocialLinks] = None
    date_of_birth: Optional[datetime] = None


class WalletAddress(BaseModel):
    address: str = Field(..., min_length=42, max_length=42)
    network: str = Field(..., min_length=1)
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('address')
    def validate_ethereum_address(cls, v):
        if not re.match(r'^0x[a-fA-F0-9]{40}$', v):
            raise ValueError('Invalid Ethereum address format')
        return v.lower()


class User(Document):
    # Core fields
    username: Indexed(str, unique=True) = Field(..., min_length=3, max_length=30)
    email: Indexed(EmailStr, unique=True)
    
    # Profile
    profile: UserProfile = Field(default_factory=UserProfile)
    
    # Authentication & Authorization
    role: UserRole = Field(default=UserRole.USER)
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    is_verified: bool = False
    
    # Web3
    wallet_addresses: List[WalletAddress] = Field(default_factory=list)
    primary_wallet: Optional[str] = None  # Address of primary wallet
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    last_active: Optional[datetime] = None
    
    # Statistics
    login_count: int = 0
    reputation_score: int = 0
    
    # Preferences
    settings: dict = Field(default_factory=dict)
    preferences: dict = Field(default_factory=dict)
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v
    
    def add_wallet(self, address: str, network: str = "ethereum") -> bool:
        """Add a new wallet address to user"""
        # Check if address already exists
        for wallet in self.wallet_addresses:
            if wallet.address.lower() == address.lower():
                return False
        
        new_wallet = WalletAddress(address=address, network=network)
        self.wallet_addresses.append(new_wallet)
        
        # Set as primary if it's the first wallet
        if not self.primary_wallet:
            self.primary_wallet = address.lower()
        
        return True
    
    def remove_wallet(self, address: str) -> bool:
        """Remove a wallet address"""
        address = address.lower()
        for i, wallet in enumerate(self.wallet_addresses):
            if wallet.address == address:
                self.wallet_addresses.pop(i)
                # Update primary wallet if removed
                if self.primary_wallet == address:
                    self.primary_wallet = self.wallet_addresses[0].address if self.wallet_addresses else None
                return True
        return False
    
    def set_primary_wallet(self, address: str) -> bool:
        """Set primary wallet address"""
        address = address.lower()
        for wallet in self.wallet_addresses:
            if wallet.address == address:
                self.primary_wallet = address
                return True
        return False
    
    def update_last_activity(self):
        """Update last activity timestamp"""
        self.last_active = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def increment_login(self):
        """Increment login count and update last login"""
        self.login_count += 1
        self.last_login = datetime.utcnow()
        self.update_last_activity()
    
    class Settings:
        name = "users"
        indexes = [
            "username",
            "email", 
            "status",
            "role",
            "created_at",
            "last_active",
            "wallet_addresses.address"
        ]
