from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # JWT Settings
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_token_prefix: str = "auth_token:"
    redis_refresh_prefix: str = "auth_refresh:"
    
    # User Service Integration
    user_service_url: str = "http://user-service:8000"
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:3080"]
    
    # Password Settings
    password_min_length: int = 8
    password_require_special: bool = True
    password_require_uppercase: bool = True
    password_require_numbers: bool = True
    
    # Rate Limiting
    login_rate_limit: int = 5  # attempts per minute
    register_rate_limit: int = 3  # attempts per minute
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
