from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.otp.router import router_otp, TAG_OTP
from app.waitlist.router import router_waitlist, TAG_WAITLIST
from app.audit.router import router_audit

# PulseCore - Multi-channel Messaging Service
app = FastAPI(
    title="PulseCore - Multi-channel Messaging API",
    version="1.1.0",
    description="""
Centralized API for multi-channel communication management.

## Capabilities
- **OTP Messaging** - Secure identity verification.
- **Onboarding (Welcome)** - Personalized user welcome notifications.
- **Waitlist Tracking** - Registration confirmation for waitlists.
- **Multi-channel Architecture** - Native Email support with built-in scalability for SMS and WhatsApp.

## Observability
- **Audit Logs** - Centralized tracking of every message dispatched and its delivery status.
""",
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        TAG_OTP, 
        TAG_WAITLIST, 
        {"name": "Audit", "description": "Full message traceability"}
    ]
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS.split(","),
    allow_headers=settings.ALLOWED_HEADERS.split(","),
)

@app.get("/")
async def root():
    return {
        "service": "PulseCore",
        "vision": "Multi-channel Messaging Engine",
        "version": "1.1.0",
        "docs": "/docs",
        "status": "ready"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "PulseCore",
        "smtp_configured": bool(settings.SMTP_HOST),
        "audit_storage": "in-memory"
    }

app.include_router(router_otp)
app.include_router(router_waitlist)
app.include_router(router_audit)