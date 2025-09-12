import strawberry
from typing import Optional

from app.services import UserService, UserNotFoundError, UserAlreadyExistsError
from app.models import UserProfile as UserProfileModel, SocialLinks as SocialLinksModel
from app.graphql.types import (
    User, UserResponse, BooleanResponse,
    CreateUserInput, UpdateUserInput, UpdateUserProfileInput, 
    UpdateSocialLinksInput, AddWalletInput,
    UserRole, UserStatus
)


@strawberry.type
class UserMutation:
    
    @strawberry.field
    async def create_user(self, input: CreateUserInput) -> UserResponse:
        """Create a new user"""
        try:
            # Create user profile
            profile = UserProfileModel(
                first_name=input.first_name,
                last_name=input.last_name,
                bio=input.bio
            )
            
            # Convert GraphQL enum to model enum
            from app.models import UserRole as UserRoleModel
            role = UserRoleModel(input.role.value) if input.role else UserRoleModel.USER
            
            # Create user
            user_model = await UserService.create_user(
                username=input.username,
                email=input.email,
                profile=profile,
                role=role
            )
            
            return UserResponse(
                success=True,
                message="User created successfully",
                user=User.from_model(user_model)
            )
            
        except UserAlreadyExistsError as e:
            return UserResponse(
                success=False,
                message=str(e),
                user=None
            )
        except Exception as e:
            return UserResponse(
                success=False,
                message=f"Failed to create user: {str(e)}",
                user=None
            )
    
    @strawberry.field
    async def update_user(self, user_id: str, input: UpdateUserInput) -> UserResponse:
        """Update user basic information"""
        try:
            update_data = {}
            if input.username:
                update_data['username'] = input.username
            if input.email:
                update_data['email'] = input.email
            
            if not update_data:
                return UserResponse(
                    success=False,
                    message="No data provided for update",
                    user=None
                )
            
            user_model = await UserService.update_user(user_id, update_data)
            
            return UserResponse(
                success=True,
                message="User updated successfully",
                user=User.from_model(user_model)
            )
            
        except UserNotFoundError:
            return UserResponse(
                success=False,
                message="User not found",
                user=None
            )
        except Exception as e:
            return UserResponse(
                success=False,
                message=f"Failed to update user: {str(e)}",
                user=None
            )
    
    @strawberry.field
    async def update_user_profile(self, user_id: str, input: UpdateUserProfileInput) -> UserResponse:
        """Update user profile"""
        try:
            profile_data = {}
            
            if input.first_name is not None:
                profile_data['first_name'] = input.first_name
            if input.last_name is not None:
                profile_data['last_name'] = input.last_name
            if input.bio is not None:
                profile_data['bio'] = input.bio
            if input.avatar_url is not None:
                profile_data['avatar_url'] = input.avatar_url
            if input.cover_url is not None:
                profile_data['cover_url'] = input.cover_url
            if input.location is not None:
                profile_data['location'] = input.location
            if input.phone is not None:
                profile_data['phone'] = input.phone
            if input.date_of_birth is not None:
                profile_data['date_of_birth'] = input.date_of_birth
            
            if not profile_data:
                return UserResponse(
                    success=False,
                    message="No profile data provided for update",
                    user=None
                )
            
            user_model = await UserService.update_user_profile(user_id, profile_data)
            
            return UserResponse(
                success=True,
                message="User profile updated successfully",
                user=User.from_model(user_model)
            )
            
        except UserNotFoundError:
            return UserResponse(
                success=False,
                message="User not found",
                user=None
            )
        except Exception as e:
            return UserResponse(
                success=False,
                message=f"Failed to update user profile: {str(e)}",
                user=None
            )
    
    @strawberry.field
    async def update_social_links(self, user_id: str, input: UpdateSocialLinksInput) -> UserResponse:
        """Update user social links"""
        try:
            user_model = await UserService.get_user_by_id(user_id)
            if not user_model:
                return UserResponse(
                    success=False,
                    message="User not found",
                    user=None
                )
            
            # Create or update social links
            social_links = SocialLinksModel(
                twitter=input.twitter,
                linkedin=input.linkedin,
                github=input.github,
                website=input.website
            )
            
            await UserService.update_user_profile(user_id, {'social_links': social_links})
            
            # Refresh user data
            updated_user = await UserService.get_user_by_id(user_id)
            
            return UserResponse(
                success=True,
                message="Social links updated successfully",
                user=User.from_model(updated_user)
            )
            
        except Exception as e:
            return UserResponse(
                success=False,
                message=f"Failed to update social links: {str(e)}",
                user=None
            )
    
    @strawberry.field
    async def add_wallet(self, user_id: str, input: AddWalletInput) -> BooleanResponse:
        """Add wallet address to user"""
        try:
            success = await UserService.add_wallet_to_user(
                user_id=user_id,
                wallet_address=input.address,
                network=input.network
            )
            
            if success:
                return BooleanResponse(
                    success=True,
                    message="Wallet added successfully"
                )
            else:
                return BooleanResponse(
                    success=False,
                    message="Wallet already exists or belongs to another user"
                )
                
        except UserNotFoundError:
            return BooleanResponse(
                success=False,
                message="User not found"
            )
        except Exception as e:
            return BooleanResponse(
                success=False,
                message=f"Failed to add wallet: {str(e)}"
            )
    
    @strawberry.field
    async def remove_wallet(self, user_id: str, wallet_address: str) -> BooleanResponse:
        """Remove wallet address from user"""
        try:
            success = await UserService.remove_wallet_from_user(user_id, wallet_address)
            
            if success:
                return BooleanResponse(
                    success=True,
                    message="Wallet removed successfully"
                )
            else:
                return BooleanResponse(
                    success=False,
                    message="Wallet not found"
                )
                
        except UserNotFoundError:
            return BooleanResponse(
                success=False,
                message="User not found"
            )
        except Exception as e:
            return BooleanResponse(
                success=False,
                message=f"Failed to remove wallet: {str(e)}"
            )
    
    @strawberry.field
    async def set_primary_wallet(self, user_id: str, wallet_address: str) -> BooleanResponse:
        """Set primary wallet for user"""
        try:
            success = await UserService.set_primary_wallet(user_id, wallet_address)
            
            if success:
                return BooleanResponse(
                    success=True,
                    message="Primary wallet set successfully"
                )
            else:
                return BooleanResponse(
                    success=False,
                    message="Wallet not found in user's wallet list"
                )
                
        except UserNotFoundError:
            return BooleanResponse(
                success=False,
                message="User not found"
            )
        except Exception as e:
            return BooleanResponse(
                success=False,
                message=f"Failed to set primary wallet: {str(e)}"
            )
    
    @strawberry.field
    async def update_user_status(self, user_id: str, status: UserStatus) -> UserResponse:
        """Update user status"""
        try:
            # Convert GraphQL enum to model enum
            from app.models import UserStatus as UserStatusModel
            status_model = UserStatusModel(status.value)
            
            user_model = await UserService.update_user_status(user_id, status_model)
            
            return UserResponse(
                success=True,
                message="User status updated successfully",
                user=User.from_model(user_model)
            )
            
        except UserNotFoundError:
            return UserResponse(
                success=False,
                message="User not found",
                user=None
            )
        except Exception as e:
            return UserResponse(
                success=False,
                message=f"Failed to update user status: {str(e)}",
                user=None
            )
    
    @strawberry.field
    async def update_user_role(self, user_id: str, role: UserRole) -> UserResponse:
        """Update user role"""
        try:
            # Convert GraphQL enum to model enum
            from app.models import UserRole as UserRoleModel
            role_model = UserRoleModel(role.value)
            
            user_model = await UserService.update_user_role(user_id, role_model)
            
            return UserResponse(
                success=True,
                message="User role updated successfully",
                user=User.from_model(user_model)
            )
            
        except UserNotFoundError:
            return UserResponse(
                success=False,
                message="User not found",
                user=None
            )
        except Exception as e:
            return UserResponse(
                success=False,
                message=f"Failed to update user role: {str(e)}",
                user=None
            )
    
    @strawberry.field
    async def delete_user(self, user_id: str) -> BooleanResponse:
        """Delete user (soft delete)"""
        try:
            success = await UserService.delete_user(user_id)
            
            return BooleanResponse(
                success=success,
                message="User deleted successfully" if success else "Failed to delete user"
            )
            
        except UserNotFoundError:
            return BooleanResponse(
                success=False,
                message="User not found"
            )
        except Exception as e:
            return BooleanResponse(
                success=False,
                message=f"Failed to delete user: {str(e)}"
            )
    
    @strawberry.field
    async def update_user_activity(self, user_id: str) -> BooleanResponse:
        """Update user last activity"""
        try:
            await UserService.update_user_activity(user_id)
            
            return BooleanResponse(
                success=True,
                message="User activity updated successfully"
            )
            
        except Exception as e:
            return BooleanResponse(
                success=False,
                message=f"Failed to update user activity: {str(e)}"
            )
