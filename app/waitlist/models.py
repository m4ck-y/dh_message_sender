from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from app.core.messaging.models import MessageChannel


class WaitlistRequest(BaseModel):
    """
    Request model for waitlist registration and notification.
    """
    email: EmailStr = Field(
        ...,
        description="**Recipient** - Contact email or identifier",
        example="user@example.com"
    )
    
    user_name: Optional[str] = Field(
        None,
        max_length=100,
        description="**User Name** for personalization",
        example="John Doe"
    )
    
    website_url: Optional[str] = Field(
        None,
        max_length=2048,
        description="**Website URL** for the action button",
        example="https://myapp.com"
    )
    
    offerings: List[str] = Field(
        default_factory=list,
        max_items=10,
        description="**List of offerings** or services of interest"
    )

    channel: MessageChannel = Field(
        default=MessageChannel.EMAIL,
        description="**Delivery Channel** selection"
    )
    
    @validator('website_url')
    def validate_website_url(cls, v):
        if v is not None and v.strip():
            if not (v.startswith('http://') or v.startswith('https://')):
                raise ValueError('URL must start with http:// or https://')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "user_name": "John Doe",
                "offerings": ["CRM", "AI Tools"],
                "channel": "email"
            }
        }


class InviteRequest(BaseModel):
    """Request model for sending a waitlist invitation email with onboarding token."""
    email: EmailStr = Field(..., description="Recipient email address.", examples=["juan.perez@example.com"])
    client_name: str = Field(..., description="Name of the lead for personalization.", examples=["Juan Pérez"])
    invite_token: str = Field(..., description="Secure token to start the onboarding process.", examples=["tok_a1b2c3d4"])
    token_expires_at: datetime = Field(..., description="UTC expiry of the invite token.", examples=["2026-05-03T10:30:00Z"])
    channel: MessageChannel = Field(default=MessageChannel.EMAIL, description="Delivery channel.")


class WaitlistResponse(BaseModel):
    """
    Detailed response model for waitlist operations.
    """
    success: bool = Field(..., description="**Dispatch Status**")
    message: str = Field(..., description="**Result Message**")
    sent_to: str = Field(..., description="**Recipient Confirmation**")
    timestamp: str = Field(..., description="**ISO Timestamp**")
    user_name: str = Field(..., description="**Applied Name**")
    has_action_button: bool = Field(False, description="**Action Button Included**")
    logo_used: Optional[str] = Field(None, description="**Branding Logo URL**")
    offerings_count: int = Field(0, description="**Number of offerings** requested")
    message_type: str = Field("platform", description="**Generated message type** (single/multiple/platform)")
    text_content: Optional[str] = Field(None, description="**Generated plain-text content**")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Waitlist confirmation dispatched",
                "sent_to": "user@example.com",
                "timestamp": "2025-01-19T10:30:00Z"
            }
        }