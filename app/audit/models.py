from pydantic import BaseModel, Field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from enum import Enum
from typing import Optional, Dict, Any

class MessageChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"

class MessageStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"

class MessageAuditEntry(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    sender: str
    recipient: str
    message_type: str  # e.g., "OTP", "Waitlist"
    channel: MessageChannel = MessageChannel.EMAIL
    status: MessageStatus
    payload_details: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
