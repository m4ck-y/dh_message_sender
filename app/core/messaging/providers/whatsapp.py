from app.core.messaging.interfaces import IMessageProvider
from app.core.messaging.models import MessagePayload

class WhatsAppProvider(IMessageProvider):
    async def send(self, payload: MessagePayload) -> None:
        """
        Placeholder for WhatsApp implementation (e.g., Meta API, Twilio).
        """
        raise NotImplementedError("WhatsApp provider has not been implemented yet.")
