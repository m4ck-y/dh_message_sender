from typing import Dict, Any
from app.core.messaging.interfaces import IMessageProvider
from app.core.messaging.models import MessagePayload
from app.audit.models import MessageAuditEntry, MessageStatus, MessageChannel
from app.audit.provider import get_audit_repository
from app.utils.observability import emit_event
from app.config import settings

# Provider implementations
from app.core.messaging.providers.email_smtp import SmtpEmailProvider
from app.core.messaging.providers.sms import SmsProvider
from app.core.messaging.providers.whatsapp import WhatsAppProvider

class MessageDispatcher:
    """
    Central router for multi-channel message dispatch.
    
    Responsible for selecting the appropriate provider based on the requested channel,
    executing the dispatch, and ensuring every attempt is recorded in the Audit log.
    """
    def __init__(self, providers: Dict[MessageChannel, IMessageProvider]):
        self.providers = providers
        self.audit_repo = get_audit_repository()

    async def dispatch(self, payload: MessagePayload) -> None:
        """
        Dispatches a message using the appropriate provider and records the outcome.
        """
        provider = self.providers.get(payload.channel)
        
        if not provider:
            error_msg = f"No provider registered for channel: {payload.channel}"
            self._log_audit(payload, MessageStatus.FAILED, error_msg)
            raise ValueError(error_msg)

        try:
            await provider.send(payload)
            self._log_audit(payload, MessageStatus.SUCCESS)
            await emit_event(
                event=f"{payload.channel.value}.sent",
                status="success",
                channel=payload.channel.value,
                recipient=payload.recipient,
                message_type=payload.metadata.get("message_type", "Unknown"),
                metadata=payload.payload_details
            )
        except NotImplementedError as e:
            error_msg = str(e)
            self._log_audit(payload, MessageStatus.FAILED, error_msg)
            await emit_event(
                event=f"{payload.channel.value}.failed",
                status="failed",
                channel=payload.channel.value,
                recipient=payload.recipient,
                message_type=payload.metadata.get("message_type", "Unknown"),
                error=error_msg,
                metadata=payload.payload_details
            )
            raise e
        except Exception as e:
            self._log_audit(payload, MessageStatus.FAILED, str(e))
            await emit_event(
                event=f"{payload.channel.value}.failed",
                status="failed",
                channel=payload.channel.value,
                recipient=payload.recipient,
                message_type=payload.metadata.get("message_type", "Unknown"),
                error=str(e),
                metadata=payload.payload_details
            )
            raise e

    def _log_audit(self, payload: MessagePayload, status: MessageStatus, error_message: str = None):
        """
        Internal mapping to persist message attempts to the IAuditRepository.
        """
        entry = MessageAuditEntry(
            sender=payload.metadata.get("sender", settings.SMTP_FROM_EMAIL),
            recipient=payload.recipient,
            message_type=payload.metadata.get("message_type", "Unknown"),
            channel=payload.channel,
            status=status,
            payload_details=payload.payload_details,
            error_message=error_message
        )
        self.audit_repo.save(entry)

# Initialize global dispatcher with available providers
_dispatcher = MessageDispatcher({
    MessageChannel.EMAIL: SmtpEmailProvider(),
    MessageChannel.SMS: SmsProvider(),
    MessageChannel.WHATSAPP: WhatsAppProvider()
})

def get_dispatcher() -> MessageDispatcher:
    """
    Dependency provider for the MessageDispatcher singleton.
    """
    return _dispatcher
