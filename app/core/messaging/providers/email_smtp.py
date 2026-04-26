import aiosmtplib
from email.message import EmailMessage
from app.config import settings
from app.core.messaging.interfaces import IMessageProvider
from app.core.messaging.models import MessagePayload

class SmtpEmailProvider(IMessageProvider):
    """
    Standard Email provider implementation using SMTP protocol.
    
    Supports secure delivery via TLS/SSL and incorporates high-level retry 
    and connection management via aiosmtplib.
    """
    async def send(self, payload: MessagePayload) -> None:
        """
        Constructs and sends an email via SMTP.
        """
        message = EmailMessage()
        message["From"] = settings.SMTP_FROM_EMAIL
        message["To"] = payload.recipient
        message["Subject"] = payload.subject
        
        # multipart/alternative order matters: clients display the LAST part they support.
        # Plain text goes first (fallback), HTML goes last (preferred).
        if payload.body_text:
            message.set_content(payload.body_text, subtype="plain")
            message.add_alternative(payload.body_html, subtype="html")
        else:
            message.set_content(payload.body_html, subtype="html")

        try:
            # Modern smart TLS selection based on standard port conventions
            # Port 465: Implicit TLS (use_tls)
            # Port 587/25: Explicit TLS (start_tls)
            
            port = settings.SMTP_PORT
            use_tls = settings.SMTP_USE_TLS if port == 465 else False
            start_tls = settings.SMTP_STARTTLS if port != 465 else False

            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=port,
                username=settings.SMTP_USERNAME,
                password=settings.SMTP_PASSWORD,
                use_tls=use_tls,
                start_tls=start_tls
            )
        except Exception as e:
            # Re-raise to be captured by the MessageDispatcher audit system
            raise e
