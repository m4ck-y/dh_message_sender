from typing import Protocol, runtime_checkable
from app.core.messaging.models import MessagePayload

@runtime_checkable
class IMessageProvider(Protocol):
    async def send(self, payload: MessagePayload) -> None:
        """
        Sends a message using the provider's specific implementation.
        Should raise an exception if sending fails.
        """
        ...
