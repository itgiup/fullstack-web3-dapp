import strawberry
from typing import Optional, List
from beanie import PydanticObjectId

from app.services import UserService
from app.graphql.types import (
    User, UserConnection, UserRole, UserStatus
)


@strawberry.type
class UserQuery:
    
    @strawberry.field
    async def user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            user_model = await UserService.get_user_by_id(user_id)
            if user_model:
                return User.from_model(user_model)
            return None
        except Exception:
            return None
    
    @strawberry.field
    async def user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            user_model = await UserService.get_user_by_username(username)
            if user_model:
                return User.from_model(user_model)
            return None
        except Exception:
            return None
    
    @strawberry.field
    async def user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            user_model = await UserService.get_user_by_email(email)
            if user_model:
                return User.from_model(user_model)
            return None
        except Exception:
            return None
    
    @strawberry.field
    async def user_by_wallet(self, wallet_address: str) -> Optional[User]:
        """Get user by wallet address"""
        try:
            user_model = await UserService.get_user_by_wallet(wallet_address)
            if user_model:
                return User.from_model(user_model)
            return None
        except Exception:
            return None
    
    @strawberry.field
    async def users(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[UserStatus] = None,
        role: Optional[UserRole] = None,
        search: Optional[str] = None
    ) -> UserConnection:
        """Get users with pagination and filters"""
        try:
            # Convert GraphQL enums to model enums
            status_filter = None
            if status:
                from app.models import UserStatus as UserStatusModel
                status_filter = UserStatusModel(status.value)
            
            role_filter = None
            if role:
                from app.models import UserRole as UserRoleModel
                role_filter = UserRoleModel(role.value)
            
            # Ensure limit doesn't exceed maximum
            limit = min(limit, 100)
            
            # Get users and total count
            users_models = await UserService.get_users(
                skip=skip,
                limit=limit,
                status=status_filter,
                role=role_filter,
                search=search
            )
            
            total_count = await UserService.get_users_count(
                status=status_filter,
                role=role_filter,
                search=search
            )
            
            # Convert to GraphQL types
            users = [User.from_model(user) for user in users_models]
            
            return UserConnection(
                users=users,
                total_count=total_count,
                has_next_page=(skip + limit) < total_count,
                has_previous_page=skip > 0
            )
            
        except Exception as e:
            # Return empty connection on error
            return UserConnection(
                users=[],
                total_count=0,
                has_next_page=False,
                has_previous_page=False
            )
    
    @strawberry.field
    async def active_users(self, days: int = 30) -> List[User]:
        """Get users active in the last N days"""
        try:
            users_models = await UserService.get_active_users_in_period(days)
            return [User.from_model(user) for user in users_models]
        except Exception:
            return []
    
    @strawberry.field
    async def user_stats(self) -> dict:
        """Get user statistics"""
        try:
            from app.models import UserStatus as UserStatusModel, UserRole as UserRoleModel
            
            total_users = await UserService.get_users_count()
            active_users = await UserService.get_users_count(status=UserStatusModel.ACTIVE)
            admin_users = await UserService.get_users_count(role=UserRoleModel.ADMIN)
            recent_active = len(await UserService.get_active_users_in_period(7))
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "admin_users": admin_users,
                "recent_active_users": recent_active
            }
        except Exception:
            return {
                "total_users": 0,
                "active_users": 0,
                "admin_users": 0,
                "recent_active_users": 0
            }
