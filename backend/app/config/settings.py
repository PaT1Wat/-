from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/manga_recommendation"
    
    # Supabase Configuration
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    supabase_jwt_secret: Optional[str] = None
    
    # Firebase (legacy - can be removed after migration)
    firebase_project_id: Optional[str] = None
    firebase_private_key: Optional[str] = None
    firebase_client_email: Optional[str] = None
    
    # JWT
    jwt_secret: str = "your-secret-key-at-least-32-characters-long"
    jwt_algorithm: str = "HS256"
    jwt_expires_in_days: int = 7
    
    # Server
    port: int = 3001
    cors_origin: str = "*"
    environment: str = "development"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
