from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración de la aplicación SmtpMailer FastAPI.
    
    Carga variables de entorno desde archivo .env y proporciona valores por defecto
    para desarrollo. Todas las configuraciones SMTP son obligatorias para el
    funcionamiento correcto del servicio de envío de correos.
    """
    
    # === CONFIGURACIÓN DE LA API ===
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # === CONFIGURACIÓN SMTP (OBLIGATORIAS) ===
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_USE_TLS: bool = True
    SMTP_USE_SSL: bool = False
    SMTP_FROM_EMAIL: str
    SMTP_FROM_NAME: str = "SmtpMailer API"
    
    # === CONFIGURACIÓN DE CORS ===
    ALLOWED_ORIGINS: str = "*"
    ALLOWED_METHODS: str = "GET,POST,PUT,DELETE,OPTIONS"
    ALLOWED_HEADERS: str = "*"
    
    # === CONFIGURACIÓN DE TIMEOUTS ===
    SMTP_TIMEOUT: int = 30
    
    # ========================================
    # VARIABLES NO UTILIZADAS (COMENTADAS)
    # ========================================
    
    # === CONFIGURACIÓN DE API AVANZADA ===
    # Para usar en uvicorn.run() o configuración de servidor
    # API_HOST: str = "127.0.0.1"  # Host del servidor
    # API_PORT: int = 8000         # Puerto del servidor
    # LOG_LEVEL: str = "INFO"      # Nivel de logging (DEBUG, INFO, WARN, ERROR)
    
    # === CONFIGURACIÓN DE SEGURIDAD ===
    # Para implementar autenticación y rate limiting
    # API_KEY_ENABLED: bool = False              # Activar autenticación por API key
    # API_KEY: Optional[str] = None              # API key para endpoints protegidos
    # RATE_LIMIT_ENABLED: bool = True           # Activar rate limiting
    # MAX_REQUESTS_PER_MINUTE: int = 100        # Límite por minuto por IP
    # MAX_REQUESTS_PER_HOUR: int = 1000         # Límite por hora por IP
    
    # === CONFIGURACIÓN DE PLANTILLAS ===
    # Para personalizar templates HTML de emails
    APP_NAME: str = "SmtpMailer API"
    COMPANY_NAME: str = "SmtpMailer API"
    COMPANY_LOGO_URL: str = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT5mug1kZAbRtSexOlAnCSRDudlfe-GKxYfQA&s"
    SUPPORT_EMAIL: str = "soporte@smtpmailer.com"
    WEBSITE_URL: str = "https://smtpmailer.com"
    
    # === CONFIGURACIÓN DE CACHE ===
    # Para implementar cache de templates y configuraciones
    # CACHE_TTL_SECONDS: int = 300  # 5 minutos  # TTL del cache
    # CACHE_ENABLED: bool = True                 # Activar/desactivar cache
    
    # === CONFIGURACIÓN DE TIMEOUTS AVANZADOS ===
    # Para timeouts de requests HTTP y otras operaciones
    # REQUEST_TIMEOUT: int = 60                  # Timeout para requests HTTP
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Instancia global de configuración
settings = Settings()