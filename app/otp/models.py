from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from app.core.messaging.models import MessageChannel


class OTPRequest(BaseModel):
    """
    Request model for multi-channel OTP (One-Time Password) dispatch.
    """
    email: EmailStr = Field(
        ...,
        description="**Recipient** - Email address or contact identifier",
        example="user@example.com"
    )
    
    code: str = Field(
        ...,
        min_length=4,
        max_length=8,
        description="**OTP Code** - Between 4 and 8 characters",
        example="A1B2C3"
    )
    
    expiry_minutes: Optional[int] = Field(
        None,
        ge=0,
        le=1440,
        description="**Expiration time** in minutes",
        example=10
    )
    
    redirect_url: Optional[str] = Field(
        None,
        max_length=2048,
        description="**Redirect URL** (Optional)",
        example="https://app.com/dashboard?verified=true"
    )

    channel: MessageChannel = Field(
        default=MessageChannel.EMAIL,
        description="**Delivery Channel** - Email, SMS, or WhatsApp"
    )
    
    @validator('redirect_url')
    def validate_redirect_url(cls, v):
        if v is not None and v.strip():
            if not (v.startswith('http://') or v.startswith('https://')):
                raise ValueError('Redirect URL must start with http:// or https://')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "code": "A1B2C3",
                "expiry_minutes": 10,
                "redirect_url": "https://app.com/dashboard?verified=true",
                "channel": "email"
            }
        }


class WelcomeRequest(BaseModel):
    """
    Request model for user onboarding/welcome message dispatch.
    """
    email: EmailStr = Field(..., description="Recipient email address")
    user_name: str = Field(..., description="Name of the user for personalization")
    login_url: Optional[str] = Field(None, description="Direct login link")
    channel: MessageChannel = Field(
        default=MessageChannel.EMAIL,
        description="Delivery channel selection"
    )


class OTPResponse(BaseModel):
    """
    Standard response model for messaging operations.
    """
    success: bool = Field(..., description="**Dispatch Status** - True if successful")
    message: str = Field(..., description="**Result Message** - Detailed outcome information")
    sent_to: str = Field(..., description="**Recipient Confirmation**")
    timestamp: str = Field(..., description="**ISO Timestamp**")
    expiry_minutes: Optional[int] = Field(None, description="**Applied expiration** in minutes")
    has_action_button: bool = Field(False, description="**Action Button Included**")
    logo_used: Optional[str] = Field(None, description="**Branding Logo URL**")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Message dispatched successfully",
                "sent_to": "user@example.com",
                "timestamp": "2025-01-19T10:30:00Z"
            }
        }