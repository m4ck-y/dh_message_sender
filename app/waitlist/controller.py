from datetime import datetime, timezone
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from app.config import settings
from app.waitlist.models import WaitlistRequest, WaitlistResponse, InviteRequest
from app.core.messaging.models import MessagePayload, MessageChannel
from app.core.messaging.dispatcher import get_dispatcher


class WaitlistApplication:
    """
    Application service for managing Waitlist registrations and status notifications.
    """
    def __init__(self):
        template_dir = Path(__file__).parent.parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        self.dispatcher = get_dispatcher()

    async def send_confirmation(self, request: WaitlistRequest) -> WaitlistResponse:
        """Dispatches a waitlist registration confirmation via the specified channel."""
        try:
            user_name = request.user_name or "User"
            website_url = request.website_url or settings.WEBSITE_URL
            show_website_button = bool(website_url and website_url.strip())
            offerings_data = self._generate_offerings_text(request.offerings)

            template_data = {
                "app_name": settings.APP_NAME,
                "company_name": settings.COMPANY_NAME,
                "logo_url": settings.COMPANY_LOGO_URL,
                "support_email": settings.SUPPORT_EMAIL,
                "website_url": website_url,
                "user_name": user_name,
                "user_email": request.email,
                "show_website_button": show_website_button,
                **offerings_data,
            }

            html_content = self.jinja_env.get_template("waitlist.html").render(**template_data)
            text_content = self._generate_text_content(
                user_name, request.email, website_url, show_website_button, offerings_data
            )

            payload = MessagePayload(
                recipient=request.email,
                subject=f"¡Ya estás en la lista de espera de {settings.APP_NAME}!",
                body_html=html_content,
                body_text=text_content,
                channel=request.channel,
                payload_details={"user_name": user_name, "offerings": request.offerings, "message_type": offerings_data["message_type"]},
                metadata={"message_type": "Waitlist", "sender": settings.SMTP_FROM_EMAIL},
            )

            await self.dispatcher.dispatch(payload)

            return WaitlistResponse(
                success=True,
                message="Waitlist confirmation dispatched successfully",
                sent_to=request.email,
                timestamp=datetime.now(timezone.utc).isoformat(),
                user_name=user_name,
                has_action_button=show_website_button,
                logo_used=settings.COMPANY_LOGO_URL,
                offerings_count=len(request.offerings),
                message_type=offerings_data["message_type"],
                text_content=offerings_data["offerings_text"],
            )

        except Exception as e:
            return WaitlistResponse(
                success=False,
                message=str(e),
                sent_to=request.email,
                timestamp=datetime.now(timezone.utc).isoformat(),
                user_name=request.user_name or "User",
            )

    async def send_invite(self, request: InviteRequest) -> WaitlistResponse:
        """Dispatches an invitation email with the onboarding secure token."""
        try:
            invite_link = f"{settings.WEBSITE_URL}/onboarding/start?token={request.invite_token}"
            expires_display = request.token_expires_at.strftime("%B %d, %Y at %I:%M %p UTC")

            template_data = {
                "app_name": settings.APP_NAME,
                "company_name": settings.COMPANY_NAME,
                "logo_url": settings.COMPANY_LOGO_URL,
                "support_email": settings.SUPPORT_EMAIL,
                "website_url": settings.WEBSITE_URL,
                "user_name": request.client_name,
                "invite_link": invite_link,
                "token_expires_at": expires_display,
            }

            html_content = self.jinja_env.get_template("invite.html").render(**template_data)
            text_content = (
                f"Has sido invitado a unirte a {settings.APP_NAME}.\n"
                f"Completa tu registro aquí: {invite_link}\n"
                f"Esta invitación expira el {expires_display}."
            )

            payload = MessagePayload(
                recipient=request.email,
                subject=f"Estás invitado a unirte a {settings.APP_NAME}",
                body_html=html_content,
                body_text=text_content,
                channel=request.channel,
                payload_details={"client_name": request.client_name, "message_type": "Invite"},
                metadata={"message_type": "Invite", "sender": settings.SMTP_FROM_EMAIL},
            )

            await self.dispatcher.dispatch(payload)

            return WaitlistResponse(
                success=True,
                message="Invite dispatched successfully",
                sent_to=request.email,
                timestamp=datetime.now(timezone.utc).isoformat(),
                user_name=request.client_name,
                has_action_button=True,
                logo_used=settings.COMPANY_LOGO_URL,
                offerings_count=0,
                message_type="invite",
            )

        except Exception as e:
            return WaitlistResponse(
                success=False,
                message=str(e),
                sent_to=request.email,
                timestamp=datetime.now(timezone.utc).isoformat(),
                user_name=request.client_name,
            )

    def _generate_offerings_text(self, offerings: list[str]) -> dict:
        count = len(offerings)
        if count == 0:
            return {"offerings_text": "nuestra plataforma", "offerings_text_html": "nuestra plataforma", "message_type": "platform", "availability_message": "En cuanto nuestra plataforma esté disponible oficialmente"}
        elif count == 1:
            name = offerings[0]
            return {"offerings_text": name, "offerings_text_html": f"<strong>{name}</strong>", "message_type": "single", "availability_message": f"En cuanto <strong>{name}</strong> esté disponible oficialmente"}
        else:
            text = ", ".join(offerings)
            html = ", ".join([f"<strong>{o}</strong>" for o in offerings])
            return {"offerings_text": text, "offerings_text_html": html, "message_type": "multiple", "availability_message": f"En cuanto nuestras soluciones {html} estén disponibles oficialmente"}

    def _generate_text_content(self, user_name: str, user_email: str, website_url: str, show_button: bool, offerings_data: dict) -> str:
        return f"¡Gracias por unirte a {settings.APP_NAME}!\nHola {user_name}, hemos registrado tu interés ({user_email}).\n{offerings_data['availability_message']}, nos pondremos en contacto contigo.".strip()
