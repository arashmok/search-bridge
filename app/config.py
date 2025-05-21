from pydantic import BaseSettings
from functools import lru_cache
import os
from typing import Optional

class Settings(BaseSettings):
    # API keys
    google_api_key: Optional[str] = None
    google_cx: Optional[str] = None  # Search engine ID for Google Custom Search
    bing_api_key: Optional[str] = None
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    
    # Rate limiting
    enable_rate_limit: bool = True
    rate_limit: int = 100  # requests per hour
    
    # Cache settings
    enable_cache: bool = True
    cache_ttl: int = 3600  # seconds
    
    class Config:
        env_file = ".env"
        env_prefix = "SEARCH_"

@lru_cache()
def get_settings() -> Settings:
    return Settings()