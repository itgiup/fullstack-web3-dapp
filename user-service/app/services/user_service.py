from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from beanie import PydanticObjectId
from beanie.operators import In, And, Or
from pymongo.errors import DuplicateKeyError

from app.models import User, UserRole, UserStatus, UserProfile
from app.config import settings


class UserNotFoundError(Exception):
    """User not found exception"""
    pass


class UserAlreadyExistsError(Exception):
    """User already exists exception"""
    pass


class UserService:
    """Service class for user operations"""

    @staticmethod
    async def create_user(
        username: str,
        email: str,
        profile: Optional[UserProfile] = None,
        role: UserRole = UserRole.USER
    ) -> User:
        """Create a new user"""
        try:
            # Check if user already exists
            existing_user = await User.find_one(
                Or(User.username == username, User.email == email)
            )
            if existing_user:
                if existing_user.username == username:
                    raise UserAlreadyExistsError(f"Username '{username}' already exists")
                else:
                    raise UserAlreadyExistsError(f"Email '{email}' already exists")
            
            # Create new user
            user = User(
                username=username,
                email=email,
                profile=profile or UserProfile(),
                role=role,
                status=UserStatus.ACTIVE
            )
            
            await user.create()
            return user
            
        except DuplicateKeyError as e:
            raise UserAlreadyExistsError("User with this username or email already exists")

    @staticmethod
    async def get_user_by_id(user_id: str | PydanticObjectId) -> Optional[User]:
        """Get user by ID"""
        if isinstance(user_id, str):
            user_id = PydanticObjectId(user_id)
        return await User.get(user_id)

    @staticmethod
    async def get_user_by_username(username: str) -> Optional[User]:
        """Get user by username"""
        return await User.find_one(User.username == username)

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        return await User.find_one(User.email == email)

    @staticmethod
    async def get_user_by_wallet(wallet_address: str) -> Optional[User]:
        """Get user by wallet address"""
        return await User.find_one(User.wallet_addresses.address == wallet_address.lower())

    @staticmethod
    async def update_user(
        user_id: str | PydanticObjectId,
        update_data: Dict[str, Any]
    ) -> Optional[User]:
        """Update user data"""
        user = await UserService.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")
        
        # Update timestamp
        update_data['updated_at'] = datetime.utcnow()
        
        # Update user fields
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        await user.save()
        return user

    @staticmethod
    async def update_user_profile(
        user_id: str | PydanticObjectId,
        profile_data: Dict[str, Any]
    ) -> Optional[User]:
        """Update user profile"""
        user = await UserService.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")
        
        # Update profile fields
        for field, value in profile_data.items():
            if hasattr(user.profile, field):
                setattr(user.profile, field, value)
        
        user.updated_at = datetime.utcnow()
        await user.save()
        return user

    @staticmethod
    async def add_wallet_to_user(
        user_id: str | PydanticObjectId,
        wallet_address: str,
        network: str = "ethereum"
    ) -> bool:
        """Add wallet address to user"""
        user = await UserService.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")
        
        # Check if wallet is already associated with another user
        existing_user = await UserService.get_user_by_wallet(wallet_address)
        if existing_user and existing_user.id != user.id:
            return False
        
        success = user.add_wallet(wallet_address, network)
        if success:
            user.updated_at = datetime.utcnow()
            await user.save()
        
        return success

    @staticmethod
    async def remove_wallet_from_user(
        user_id: str | PydanticObjectId,
        wallet_address: str
    ) -> bool:
        """Remove wallet address from user"""
        user = await UserService.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")
        
        success = user.remove_wallet(wallet_address)
        if success:
            user.updated_at = datetime.utcnow()
            await user.save()
        
        return success

    @staticmethod
    async def set_primary_wallet(
        user_id: str | PydanticObjectId,
        wallet_address: str
    ) -> bool:
        """Set primary wallet for user"""
        user = await UserService.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")
        
        success = user.set_primary_wallet(wallet_address)
        if success:
            user.updated_at = datetime.utcnow()
            await user.save()
        
        return success

    @staticmethod
    async def update_user_status(
        user_id: str | PydanticObjectId,
        status: UserStatus
    ) -> Optional[User]:
        """Update user status"""
        return await UserService.update_user(user_id, {"status": status})

    @staticmethod
    async def update_user_role(
        user_id: str | PydanticObjectId,
        role: UserRole
    ) -> Optional[User]:
        """Update user role"""
        return await UserService.update_user(user_id, {"role": role})

    @staticmethod
    async def delete_user(user_id: str | PydanticObjectId) -> bool:
        """Delete user (soft delete by setting status to inactive)"""
        user = await UserService.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")
        
        user.status = UserStatus.INACTIVE
        user.updated_at = datetime.utcnow()
        await user.save()
        return True

    @staticmethod
    async def get_users(
        skip: int = 0,
        limit: int = 20,
        status: Optional[UserStatus] = None,
        role: Optional[UserRole] = None,
        search: Optional[str] = None
    ) -> List[User]:
        """Get users with pagination and filters"""
        
        query = []
        
        # Add status filter
        if status:
            query.append(User.status == status)
        
        # Add role filter  
        if role:
            query.append(User.role == role)
        
        # Add search filter
        if search:
            query.append(
                Or(
                    User.username.contains(search, case_insensitive=True),
                    User.email.contains(search, case_insensitive=True),
                    User.profile.first_name.contains(search, case_insensitive=True),
                    User.profile.last_name.contains(search, case_insensitive=True)
                )
            )
        
        # Build final query
        if query:
            final_query = And(*query) if len(query) > 1 else query[0]
            users = await User.find(final_query).skip(skip).limit(limit).to_list()
        else:
            users = await User.find().skip(skip).limit(limit).to_list()
        
        return users

    @staticmethod
    async def get_users_count(
        status: Optional[UserStatus] = None,
        role: Optional[UserRole] = None,
        search: Optional[str] = None
    ) -> int:
        """Get total count of users with filters"""
        
        query = []
        
        if status:
            query.append(User.status == status)
        
        if role:
            query.append(User.role == role)
        
        if search:
            query.append(
                Or(
                    User.username.contains(search, case_insensitive=True),
                    User.email.contains(search, case_insensitive=True),
                    User.profile.first_name.contains(search, case_insensitive=True),
                    User.profile.last_name.contains(search, case_insensitive=True)
                )
            )
        
        if query:
            final_query = And(*query) if len(query) > 1 else query[0]
            return await User.find(final_query).count()
        else:
            return await User.find().count()

    @staticmethod
    async def get_active_users_in_period(days: int = 30) -> List[User]:
        """Get users active in the last N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return await User.find(
            And(
                User.status == UserStatus.ACTIVE,
                User.last_active >= cutoff_date
            )
        ).to_list()

    @staticmethod
    async def update_user_activity(user_id: str | PydanticObjectId):
        """Update user last activity"""
        user = await UserService.get_user_by_id(user_id)
        if user:
            user.update_last_activity()
            await user.save()

    @staticmethod
    async def increment_user_login(user_id: str | PydanticObjectId):
        """Increment user login count"""
        user = await UserService.get_user_by_id(user_id)
        if user:
            user.increment_login()
            await user.save()
