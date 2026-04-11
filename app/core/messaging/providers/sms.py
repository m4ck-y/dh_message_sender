from app.core.messaging.interfaces import IMessageProvider
from app.core.messaging.models import MessagePayload

class SmsProvider(IMessageProvider):
    async def send(self, payload: MessagePayload) -> None:
        """
        Placeholder for SMS implementation (e.g., Twilio, AWS SNS).
        """
        raise NotImplementedError("SMS provider has not been implemented yet.")
