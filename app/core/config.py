# app/core/config.py

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr
import os

# Pydantic v2 requires this explicit definition for loading .env files
# This class defines the structure and validation rules for all environment variables.
class Settings(BaseSettings):
    # --- Application Settings ---
    PROJECT_NAME: str = "Enterprise Knowledge Agent"
    API_V1_STR: str = "/api/v1"
    DEBUG_MODE: bool = Field(False)
    
    # --- Security & Auth (from .env) ---
    # SecretStr is used to prevent the key from being accidentally logged or displayed
    SECRET_KEY: SecretStr = Field(..., description="Key used for JWT signing.")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # --- Database Settings (for Long-Term Memory) ---
    # This must be the full PostgreSQL connection URL
    DATABASE_URL: str = Field(..., description="The PostgreSQL connection URL for LTM.")
    
    # --- RAG/LLM Settings ---
    # Used for initializing the LLM/Embedding models
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    CHROMA_PERSIST_DIR: str = "./chroma_data"
    
    # Pydantic configuration class to specify where to find the .env file
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'),
        env_file_encoding='utf-8',
        extra='ignore' # Ignores extra variables in .env not defined here
    )

# Use lru_cache to ensure settings are only initialized once upon first call
@lru_cache()
def get_settings() -> Settings:
    """Returns a cached instance of the application settings."""
    return Settings()

# Export the settings instance for direct use in non-dependency contexts
settings = get_settings()