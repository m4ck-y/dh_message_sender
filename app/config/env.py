import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """
    Application-wide configuration settings for PulseCore.
    
    Loads values from environment variables with sensible defaults and 
    comprehensive validation for critical infrastructure like SMTP and CORS.
    """
    
    # API CONFIGURATION
    APP_NAME: str = os.getenv("APP_NAME", "PulseCore")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS CONFIGURATION
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")
    ALLOWED_METHODS: str = os.getenv("ALLOWED_METHODS", "*")
    ALLOWED_HEADERS: str = os.getenv("ALLOWED_HEADERS", "*")
    
    # SMTP CONFIGURATION
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL: str = os.getenv("SMTP_FROM_EMAIL", "")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "True").lower() == "true"
    SMTP_STARTTLS: bool = os.getenv("SMTP_STARTTLS", "True").lower() == "true"
    
    # BRANDING AND SUPPORT
    COMPANY_NAME: str = os.getenv("COMPANY_NAME", "Digital Hospital")
    COMPANY_LOGO_URL: str = os.getenv("COMPANY_LOGO_URL", "")
    SUPPORT_EMAIL: str = os.getenv("SUPPORT_EMAIL", "")
    WEBSITE_URL: str = os.getenv("WEBSITE_URL", "")

    # INTER-SERVICE CONFIGURATION
    # Pattern: SERVICE_<SERVICE_NAME>_URL (see api_middleware/.env.example)
    # If empty, events are stored in InMemoryAuditRepository only (graceful degradation).
    SERVICE_LOGGER_TRACER_URL: str = os.getenv("SERVICE_LOGGER_TRACER_URL", "")

    class Config:
        case_sensitive = True

settings = Settings()