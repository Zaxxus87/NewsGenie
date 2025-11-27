"""
Configuration management for NewsGenie
Handles environment variables and application settings
"""
import os
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    news_api_key: str = os.getenv("NEWS_API_KEY", "")
    
    # Model Configuration
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    temperature: float = 0.7
    max_tokens: int = 1000
    
    # Application Settings
    app_title: str = os.getenv("APP_TITLE", "NewsGenie")
    app_description: str = os.getenv("APP_DESCRIPTION", "Your AI-powered news assistant")
    
    # News API Settings
    news_api_page_size: int = 10
    news_categories: list = [
        "general",
        "business",
        "technology",
        "entertainment",
        "health",
        "science",
        "sports"
    ]
    
    def validate_api_keys(self) -> dict:
        """Validate that required API keys are present"""
        missing_keys = []
        
        if not self.openai_api_key:
            missing_keys.append("OPENAI_API_KEY")
        if not self.news_api_key:
            missing_keys.append("NEWS_API_KEY")
        
        return {
            "valid": len(missing_keys) == 0,
            "missing_keys": missing_keys
        }
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create global settings instance
settings = Settings()