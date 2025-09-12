import strawberry
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.models import User as UserModel, UserRole as UserRoleModel, UserStatus as UserStatusModel


@strawberry.enum
class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


@strawberry.enum  
class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"
    PENDING = "pending"


@strawberry.type
class SocialLinks:
    twitter: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None


@strawberry.type
class UserProfile:
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    cover_url: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    social_links: Optional[SocialLinks] = None
    date_of_birth: Optional[datetime] = None


@strawberry.type
class WalletAddress:
    address: str
    network: str
    is_verified: bool
    created_at: datetime


@strawberry.type
class User:
    id: str
    username: str
    email: str
    profile: UserProfile
    role: UserRole
    status: UserStatus
    is_verified: bool
    wallet_addresses: List[WalletAddress]
    primary_wallet: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    last_active: Optional[datetime] = None
    login_count: int
    reputation_score: int
    
    @classmethod
    def from_model(cls, user: UserModel) -> "User":
        """Convert User model to GraphQL User type"""
        return cls(
            id=str(user.id),
            username=user.username,
            email=user.email,
            profile=UserProfile(
                first_name=user.profile.first_name,
                last_name=user.profile.last_name,
                bio=user.profile.bio,
                avatar_url=user.profile.avatar_url,
                cover_url=user.profile.cover_url,
                location=user.profile.location,
                phone=user.profile.phone,
                social_links=SocialLinks(
                    twitter=user.profile.social_links.twitter if user.profile.social_links else None,
                    linkedin=user.profile.social_links.linkedin if user.profile.social_links else None,
                    github=user.profile.social_links.github if user.profile.social_links else None,
                    website=user.profile.social_links.website if user.profile.social_links else None,
                ) if user.profile.social_links else None,
                date_of_birth=user.profile.date_of_birth,
            ),
            role=UserRole(user.role.value),
            status=UserStatus(user.status.value),
            is_verified=user.is_verified,
            wallet_addresses=[
                WalletAddress(
                    address=wallet.address,
                    network=wallet.network,
                    is_verified=wallet.is_verified,
                    created_at=wallet.created_at
                )
                for wallet in user.wallet_addresses
            ],
            primary_wallet=user.primary_wallet,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login,
            last_active=user.last_active,
            login_count=user.login_count,
            reputation_score=user.reputation_score,
        )


@strawberry.type
class UserConnection:
    """Paginated user results"""
    users: List[User]
    total_count: int
    has_next_page: bool
    has_previous_page: bool


# Input types for mutations
@strawberry.input
class CreateUserInput:
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    role: Optional[UserRole] = UserRole.USER


@strawberry.input
class UpdateUserInput:
    username: Optional[str] = None
    email: Optional[str] = None


@strawberry.input
class UpdateUserProfileInput:
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    cover_url: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None


@strawberry.input
class UpdateSocialLinksInput:
    twitter: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None


@strawberry.input
class AddWalletInput:
    address: str
    network: str = "ethereum"


# Response types
@strawberry.type
class UserResponse:
    """Standard response for user operations"""
    success: bool
    message: str
    user: Optional[User] = None


@strawberry.type
class BooleanResponse:
    """Standard boolean response"""
    success: bool
    message: str
