import strawberry
from fastapi import Request
from typing import Optional

from app.services import AuthService, JWTService
from app.models import (
    RegisterRequest, LoginRequest, WalletLoginRequest,
    ChangePasswordRequest, LoginMethod
)
from app.graphql.types import (
    RegisterInput, LoginInput, WalletLoginInput, 
    RefreshTokenInput, ChangePasswordInput,
    AuthResponse, LogoutResponse, UserInfo, TokenPair
)


@strawberry.type  
class AuthMutation:
    
    @strawberry.field
    async def register(self, input: RegisterInput) -> AuthResponse:
        """Register new user"""
        try:
            # Convert GraphQL input to service request
            request = RegisterRequest(
                username=input.username,
                email=input.email,
                password=input.password,
                confirm_password=input.confirm_password,
                first_name=input.first_name,
                last_name=input.last_name,
                wallet_address=input.wallet_address
            )
            
            # Call auth service
            result = await AuthService.register_user(request)
            
            # Convert response
            user_info = None
            if result.user:
                user_info = UserInfo(
                    id=result.user["id"],
                    username=result.user["username"],
                    email=result.user["email"],
                    role=result.user["role"],
                    status="ACTIVE",  # New users are active
                    first_name=result.user.get("profile", {}).get("firstName"),
                    last_name=result.user.get("profile", {}).get("lastName")
                )
            
            return AuthResponse(
                success=result.success,
                message=result.message,
                tokens=result.tokens,
                user=user_info
            )
            
        except ValueError as e:
            return AuthResponse(
                success=False,
                message=str(e),
                tokens=None,
                user=None
            )
        except Exception as e:
            return AuthResponse(
                success=False,
                message=f"Registration failed: {str(e)}",
                tokens=None,
                user=None
            )
    
    @strawberry.field
    async def login(self, input: LoginInput) -> AuthResponse:
        """Login user"""
        try:
            # Convert method enum
            method = LoginMethod(input.method.value)
            
            # Convert GraphQL input to service request
            request = LoginRequest(
                identifier=input.identifier,
                password=input.password,
                signature=input.signature,
                message=input.message,
                method=method
            )
            
            # Call auth service
            result = await AuthService.login_user(request)
            
            # Convert response
            user_info = None
            token_pair = None
            
            if result.user:
                user_info = UserInfo(
                    id=result.user["id"],
                    username=result.user["username"],
                    email=result.user["email"],
                    role=result.user["role"],
                    status=result.user["status"],
                    first_name=result.user.get("profile", {}).get("firstName"),
                    last_name=result.user.get("profile", {}).get("lastName")
                )
            
            if result.tokens:
                token_pair = TokenPair(
                    access_token=result.tokens.access_token,
                    refresh_token=result.tokens.refresh_token,
                    token_type=result.tokens.token_type,
                    expires_in=result.tokens.expires_in
                )
            
            return AuthResponse(
                success=result.success,
                message=result.message,
                tokens=token_pair,
                user=user_info
            )
            
        except ValueError as e:
            return AuthResponse(
                success=False,
                message=str(e),
                tokens=None,
                user=None
            )
        except Exception as e:
            return AuthResponse(
                success=False,
                message=f"Login failed: {str(e)}",
                tokens=None,
                user=None
            )
    
    @strawberry.field
    async def wallet_login(self, input: WalletLoginInput) -> AuthResponse:
        """Login with wallet signature"""
        try:
            # Convert to service request
            request = WalletLoginRequest(
                wallet_address=input.wallet_address,
                signature=input.signature,
                message=input.message
            )
            
            # Convert to LoginRequest for auth service
            login_request = LoginRequest(
                identifier=input.wallet_address,
                signature=input.signature,
                message=input.message,
                method=LoginMethod.WALLET
            )
            
            # Call auth service
            result = await AuthService.login_user(login_request)
            
            # Convert response (same as login)
            user_info = None
            token_pair = None
            
            if result.user:
                user_info = UserInfo(
                    id=result.user["id"],
                    username=result.user["username"],
                    email=result.user["email"],
                    role=result.user["role"],
                    status=result.user["status"],
                    first_name=result.user.get("profile", {}).get("firstName"),
                    last_name=result.user.get("profile", {}).get("lastName")
                )
            
            if result.tokens:
                token_pair = TokenPair(
                    access_token=result.tokens.access_token,
                    refresh_token=result.tokens.refresh_token,
                    token_type=result.tokens.token_type,
                    expires_in=result.tokens.expires_in
                )
            
            return AuthResponse(
                success=result.success,
                message=result.message,
                tokens=token_pair,
                user=user_info
            )
            
        except ValueError as e:
            return AuthResponse(
                success=False,
                message=str(e),
                tokens=None,
                user=None
            )
        except Exception as e:
            return AuthResponse(
                success=False,
                message=f"Wallet login failed: {str(e)}",
                tokens=None,
                user=None
            )
    
    @strawberry.field
    async def refresh_token(self, input: RefreshTokenInput) -> AuthResponse:
        """Refresh access token"""
        try:
            # Call auth service
            result = await AuthService.refresh_tokens(input.refresh_token)
            
            # Convert response
            user_info = None
            token_pair = None
            
            if result.user:
                user_info = UserInfo(
                    id=result.user["id"],
                    username=result.user["username"],
                    email=result.user["email"],
                    role=result.user["role"],
                    status=result.user["status"],
                    first_name=result.user.get("profile", {}).get("firstName"),
                    last_name=result.user.get("profile", {}).get("lastName")
                )
            
            if result.tokens:
                token_pair = TokenPair(
                    access_token=result.tokens.access_token,
                    refresh_token=result.tokens.refresh_token,
                    token_type=result.tokens.token_type,
                    expires_in=result.tokens.expires_in
                )
            
            return AuthResponse(
                success=result.success,
                message=result.message,
                tokens=token_pair,
                user=user_info
            )
            
        except Exception as e:
            return AuthResponse(
                success=False,
                message=f"Token refresh failed: {str(e)}",
                tokens=None,
                user=None
            )
    
    @strawberry.field
    async def logout(self, info) -> LogoutResponse:
        """Logout current user"""
        try:
            # Get user from context (set by auth middleware)
            user = getattr(info.context.get("request", {}), "user", None)
            if not user:
                return LogoutResponse(
                    success=False,
                    message="Not authenticated"
                )
            
            # Call auth service
            success = await AuthService.logout_user(user.user_id)
            
            return LogoutResponse(
                success=success,
                message="Logged out successfully" if success else "Logout failed"
            )
            
        except Exception as e:
            return LogoutResponse(
                success=False,
                message=f"Logout failed: {str(e)}"
            )
    
    @strawberry.field
    async def change_password(self, input: ChangePasswordInput, info) -> AuthResponse:
        """Change password for authenticated user"""
        try:
            # Get user from context
            user = getattr(info.context.get("request", {}), "user", None)
            if not user:
                return AuthResponse(
                    success=False,
                    message="Not authenticated"
                )
            
            # Convert input to service request
            request = ChangePasswordRequest(
                current_password=input.current_password,
                new_password=input.new_password,
                confirm_password=input.confirm_password
            )
            
            # Call auth service
            result = await AuthService.change_password(
                user.user_id,
                input.current_password,
                input.new_password
            )
            
            return AuthResponse(
                success=result.success,
                message=result.message,
                tokens=None,
                user=None
            )
            
        except ValueError as e:
            return AuthResponse(
                success=False,
                message=str(e),
                tokens=None,
                user=None
            )
        except Exception as e:
            return AuthResponse(
                success=False,
                message=f"Password change failed: {str(e)}",
                tokens=None,
                user=None
            )
