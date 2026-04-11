from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.audit.models import MessageChannel

class MessagePayload(BaseModel):
    recipient: str
    subject: str
    body_html: str
    body_text: Optional[str] = None
    channel: MessageChannel = MessageChannel.EMAIL
    payload_details: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
