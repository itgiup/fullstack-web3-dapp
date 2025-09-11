import strawberry
from app.graphql.mutations import AuthMutation
from app.graphql.types import MeResponse, HealthResponse
from app.services import JWTService
from app.database import check_redis_health
import httpx
from app.config import settings


@strawberry.type
class AuthQuery:
    
    @strawberry.field
    async def me(self, info) -> MeResponse:
        """Get current authenticated user info"""
        # Get user from context (set by auth middleware)
        user = getattr(info.context.get("request", {}), "user", None)
        if not user:
            raise Exception("Not authenticated")
        
        # Get session info
        session = await JWTService.get_user_session(user.user_id)
        
        return MeResponse(
            id=user.user_id,
            username=user.username,
            email=user.email,
            role=user.role,
            status="ACTIVE",  # From token, user is active
            login_time=session.login_time if session else None,
            last_activity=session.last_activity if session else None
        )
    
    @strawberry.field
    async def health(self) -> HealthResponse:
        """Auth service health check"""
        redis_connected = await check_redis_health()
        
        # Check user-service connection
        user_service_connected = False
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{settings.user_service_url}/health",
                    timeout=3.0
                )
                user_service_connected = response.status_code == 200
        except:
            pass
        
        return HealthResponse(
            status="OK" if redis_connected and user_service_connected else "ERROR",
            service="auth-service",
            redis_connected=redis_connected,
            user_service_connected=user_service_connected
        )


@strawberry.type
class Query(AuthQuery):
    pass


@strawberry.type
class Mutation(AuthMutation):
    pass


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)
