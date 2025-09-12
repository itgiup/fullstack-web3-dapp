import json
import httpx
from typing import Optional, Dict, Any
from datetime import datetime

from app.config import settings
from app.models import (
    RegisterRequest, LoginRequest, WalletLoginRequest,
    TokenPair, AuthResponse, PasswordHash
)
from app.services.jwt_service import JWTService
from app.database import get_redis


class AuthNotFoundError(Exception):
    """Authentication error"""
    pass


class AuthInvalidCredentialsError(Exception):
    """Invalid credentials error"""
    pass


class AuthService:
    """Authentication Service - integrates with user-service"""
    
    @staticmethod
    async def register_user(request: RegisterRequest) -> AuthResponse:
        """Register new user via user-service"""
        try:
            # Create user in user-service
            async with httpx.AsyncClient() as client:
                create_user_payload = {
                    "query": """
                        mutation CreateUser($input: CreateUserInput!) {
                            createUser(input: $input) {
                                success
                                message
                                user {
                                    id
                                    username
                                    email
                                    role
                                    profile {
                                        firstName
                                        lastName
                                    }
                                }
                            }
                        }
                    """,
                    "variables": {
                        "input": {
                            "username": request.username,
                            "email": request.email,
                            "firstName": request.first_name,
                            "lastName": request.last_name,
                            "role": "USER"
                        }
                    }
                }
                
                response = await client.post(
                    f"{settings.user_service_url}/graphql",
                    json=create_user_payload,
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    return AuthResponse(
                        success=False,
                        message="Failed to create user account"
                    )
                
                result = response.json()
                if result.get("errors"):
                    error_msg = result["errors"][0].get("message", "Registration failed")
                    return AuthResponse(
                        success=False,
                        message=error_msg
                    )
                
                create_result = result["data"]["createUser"]
                if not create_result["success"]:
                    return AuthResponse(
                        success=False,
                        message=create_result["message"]
                    )
                
                user_data = create_result["user"]
                
                # Store password hash in Redis (auth-service manages passwords)
                password_hash = JWTService.hash_password(request.password)
                await AuthService._store_password_hash(user_data["id"], password_hash)
                
                # Add wallet if provided
                if request.wallet_address:
                    await AuthService._add_wallet_to_user(user_data["id"], request.wallet_address)
                
                return AuthResponse(
                    success=True,
                    message="User registered successfully",
                    user=user_data
                )
                
        except httpx.RequestError:
            return AuthResponse(
                success=False,
                message="User service unavailable"
            )
        except Exception as e:
            return AuthResponse(
                success=False,
                message=f"Registration failed: {str(e)}"
            )
    
    @staticmethod
    async def login_user(request: LoginRequest) -> AuthResponse:
        """Login user and return tokens"""
        try:
            # Get user from user-service based on method
            user_data = None
            
            if request.method.value == "email":
                user_data = await AuthService._get_user_by_email(request.identifier)
            elif request.method.value == "username":
                user_data = await AuthService._get_user_by_username(request.identifier)
            elif request.method.value == "wallet":
                user_data = await AuthService._get_user_by_wallet(request.identifier)
            
            if not user_data:
                return AuthResponse(
                    success=False,
                    message="User not found"
                )
            
            # Check user status
            if user_data["status"] != "ACTIVE":
                return AuthResponse(
                    success=False,
                    message="Account is not active"
                )
            
            # For wallet login, verify signature
            if request.method.value == "wallet":
                if not request.signature or not request.message:
                    return AuthResponse(
                        success=False,
                        message="Signature and message required for wallet login"
                    )
                
                # TODO: Implement signature verification
                # For now, we'll skip signature verification
                # In production, verify the signature against the wallet address
            else:
                # For email/username login, verify password
                if not request.password:
                    return AuthResponse(
                        success=False,
                        message="Password required"
                    )
                
                # Get stored password hash
                stored_hash = await AuthService._get_password_hash(user_data["id"])
                if not stored_hash or not JWTService.verify_password(request.password, stored_hash):
                    return AuthResponse(
                        success=False,
                        message="Invalid credentials"
                    )
            
            # Create tokens
            tokens = await JWTService.create_token_pair(
                user_id=user_data["id"],
                username=user_data["username"],
                email=user_data["email"],
                role=user_data["role"]
            )
            
            # Store user session
            await JWTService.store_user_session(
                user_id=user_data["id"],
                username=user_data["username"],
                email=user_data["email"],
                role=user_data["role"]
            )
            
            # Update user activity in user-service
            await AuthService._update_user_activity(user_data["id"])
            
            return AuthResponse(
                success=True,
                message="Login successful",
                tokens=tokens,
                user=user_data
            )
            
        except Exception as e:
            return AuthResponse(
                success=False,
                message=f"Login failed: {str(e)}"
            )
    
    @staticmethod
    async def refresh_tokens(refresh_token: str) -> AuthResponse:
        """Refresh access token"""
        try:
            # Verify refresh token
            user_id = await JWTService.verify_refresh_token(refresh_token)
            if not user_id:
                return AuthResponse(
                    success=False,
                    message="Invalid refresh token"
                )
            
            # Get user data
            user_data = await AuthService._get_user_by_id(user_id)
            if not user_data or user_data["status"] != "ACTIVE":
                return AuthResponse(
                    success=False,
                    message="User not found or inactive"
                )
            
            # Create new token pair
            tokens = await JWTService.create_token_pair(
                user_id=user_data["id"],
                username=user_data["username"],
                email=user_data["email"],
                role=user_data["role"]
            )
            
            # Update session
            await JWTService.update_user_activity(user_id)
            
            return AuthResponse(
                success=True,
                message="Tokens refreshed successfully",
                tokens=tokens,
                user=user_data
            )
            
        except Exception as e:
            return AuthResponse(
                success=False,
                message=f"Token refresh failed: {str(e)}"
            )
    
    @staticmethod
    async def logout_user(user_id: str) -> bool:
        """Logout user and revoke tokens"""
        try:
            await JWTService.revoke_all_tokens(user_id)
            return True
        except Exception:
            return False
    
    @staticmethod
    async def change_password(user_id: str, current_password: str, new_password: str) -> AuthResponse:
        """Change user password"""
        try:
            # Verify current password
            stored_hash = await AuthService._get_password_hash(user_id)
            if not stored_hash or not JWTService.verify_password(current_password, stored_hash):
                return AuthResponse(
                    success=False,
                    message="Current password is incorrect"
                )
            
            # Hash new password and store
            new_hash = JWTService.hash_password(new_password)
            await AuthService._store_password_hash(user_id, new_hash)
            
            # Revoke all existing tokens (force re-login)
            await JWTService.revoke_all_tokens(user_id)
            
            return AuthResponse(
                success=True,
                message="Password changed successfully"
            )
            
        except Exception as e:
            return AuthResponse(
                success=False,
                message=f"Password change failed: {str(e)}"
            )
    
    # Helper methods to interact with user-service
    @staticmethod
    async def _get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID from user-service"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "query": """
                        query GetUserById($userId: String!) {
                            userById(userId: $userId) {
                                id
                                username
                                email
                                role
                                status
                                profile {
                                    firstName
                                    lastName
                                }
                            }
                        }
                    """,
                    "variables": {"userId": user_id}
                }
                
                response = await client.post(
                    f"{settings.user_service_url}/graphql",
                    json=payload,
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["data"]["userById"]
                    
        except Exception:
            pass
        
        return None
    
    @staticmethod
    async def _get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get user by email from user-service"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "query": """
                        query GetUserByEmail($email: String!) {
                            userByEmail(email: $email) {
                                id
                                username
                                email
                                role
                                status
                                profile {
                                    firstName
                                    lastName
                                }
                            }
                        }
                    """,
                    "variables": {"email": email}
                }
                
                response = await client.post(
                    f"{settings.user_service_url}/graphql",
                    json=payload,
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["data"]["userByEmail"]
                    
        except Exception:
            pass
        
        return None
    
    @staticmethod
    async def _get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
        """Get user by username from user-service"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "query": """
                        query GetUserByUsername($username: String!) {
                            userByUsername(username: $username) {
                                id
                                username
                                email
                                role
                                status
                                profile {
                                    firstName
                                    lastName
                                }
                            }
                        }
                    """,
                    "variables": {"username": username}
                }
                
                response = await client.post(
                    f"{settings.user_service_url}/graphql",
                    json=payload,
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["data"]["userByUsername"]
                    
        except Exception:
            pass
        
        return None
    
    @staticmethod
    async def _get_user_by_wallet(wallet_address: str) -> Optional[Dict[str, Any]]:
        """Get user by wallet address from user-service"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "query": """
                        query GetUserByWallet($walletAddress: String!) {
                            userByWallet(walletAddress: $walletAddress) {
                                id
                                username
                                email
                                role
                                status
                                profile {
                                    firstName
                                    lastName
                                }
                            }
                        }
                    """,
                    "variables": {"walletAddress": wallet_address}
                }
                
                response = await client.post(
                    f"{settings.user_service_url}/graphql",
                    json=payload,
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["data"]["userByWallet"]
                    
        except Exception:
            pass
        
        return None
    
    @staticmethod
    async def _update_user_activity(user_id: str):
        """Update user activity in user-service"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "query": """
                        mutation UpdateUserActivity($userId: String!) {
                            updateUserActivity(userId: $userId) {
                                success
                            }
                        }
                    """,
                    "variables": {"userId": user_id}
                }
                
                await client.post(
                    f"{settings.user_service_url}/graphql",
                    json=payload,
                    timeout=5.0
                )
                
        except Exception:
            pass
    
    @staticmethod
    async def _add_wallet_to_user(user_id: str, wallet_address: str):
        """Add wallet to user in user-service"""
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "query": """
                        mutation AddWallet($userId: String!, $input: AddWalletInput!) {
                            addWallet(userId: $userId, input: $input) {
                                success
                            }
                        }
                    """,
                    "variables": {
                        "userId": user_id,
                        "input": {"address": wallet_address, "network": "ethereum"}
                    }
                }
                
                await client.post(
                    f"{settings.user_service_url}/graphql",
                    json=payload,
                    timeout=5.0
                )
                
        except Exception:
            pass
    
    @staticmethod
    async def _store_password_hash(user_id: str, password_hash: str):
        """Store password hash in Redis"""
        redis_client = await get_redis()
        
        password_data = PasswordHash(
            user_id=user_id,
            password_hash=password_hash,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        await redis_client.set(
            f"password:{user_id}",
            password_data.json()
        )
    
    @staticmethod
    async def _get_password_hash(user_id: str) -> Optional[str]:
        """Get password hash from Redis"""
        redis_client = await get_redis()
        
        password_data = await redis_client.get(f"password:{user_id}")
        if password_data:
            password_obj = PasswordHash.parse_raw(password_data)
            return password_obj.password_hash
        
        return None
