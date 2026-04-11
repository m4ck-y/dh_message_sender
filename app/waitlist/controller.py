from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from app.config import settings
from app.waitlist.models import WaitlistRequest, WaitlistResponse
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
        print(f"[INFO] WaitlistApplication initialized")

    async def send_confirmation(self, request: WaitlistRequest) -> WaitlistResponse:
        """
        Dispatches a waitlist confirmation via the specified channel.
        """
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
                **offerings_data
            }
            
            template = self.jinja_env.get_template("waitlist.html")
            html_content = template.render(**template_data)
            
            text_content = self._generate_text_content(
                user_name, request.email, website_url, show_website_button, offerings_data
            )
            
            payload = MessagePayload(
                recipient=request.email,
                subject="Thank you for joining our waitlist!",
                body_html=html_content,
                body_text=text_content,
                channel=request.channel,
                payload_details={
                    "user_name": user_name,
                    "offerings": request.offerings,
                    "message_type": offerings_data['message_type']
                },
                metadata={
                    "message_type": "Waitlist",
                    "sender": settings.SMTP_FROM_EMAIL
                }
            )
            
            await self.dispatcher.dispatch(payload)
            
            return WaitlistResponse(
                success=True,
                message="Waitlist confirmation dispatched successfully",
                sent_to=request.email,
                timestamp=datetime.utcnow().isoformat() + "Z",
                user_name=user_name,
                has_action_button=show_website_button,
                logo_used=settings.COMPANY_LOGO_URL,
                offerings_count=len(request.offerings),
                message_type=offerings_data['message_type'],
                text_content=offerings_data['offerings_text']
            )
            
        except Exception as e:
            print(f"[ERROR] Dispatch error in send_confirmation: {str(e)}")
            return WaitlistResponse(
                success=False,
                message=str(e),
                sent_to=request.email if 'request' in locals() else "Unknown",
                timestamp=datetime.utcnow().isoformat() + "Z",
                user_name=request.user_name or "User"
            )

    def _generate_offerings_text(self, offerings: list[str]) -> dict:
        """
        Generates English text and HTML snippets based on the number of offerings provided.
        """
        offerings_count = len(offerings)
        if offerings_count == 0:
            return {
                'offerings_text': 'our platform',
                'offerings_text_html': 'our platform',
                'message_type': 'platform',
                'availability_message': 'As soon as our platform is officially available'
            }
        elif offerings_count == 1:
            offering_name = offerings[0]
            return {
                'offerings_text': offering_name,
                'offerings_text_html': f'<strong>{offering_name}</strong>',
                'message_type': 'single',
                'availability_message': f'As soon as <strong>{offering_name}</strong> is officially available'
            }
        else:
            offerings_text = ', '.join(offerings)
            offerings_text_html = ', '.join([f'<strong>{offering}</strong>' for offering in offerings])
            return {
                'offerings_text': offerings_text,
                'offerings_text_html': offerings_text_html,
                'message_type': 'multiple',
                'availability_message': f'As soon as our solutions {offerings_text_html} are officially available'
            }

    def _generate_text_content(self, user_name: str, user_email: str, website_url: str, 
                               show_website_button: bool, offerings_data: dict) -> str:
        """
        Generates the plain text version of the waitlist notification.
        """
        return f"""
Thank you for joining {settings.APP_NAME}!
Hello {user_name}, we have successfully registered your interest ({user_email}).
{offerings_data['availability_message']}, we will reach out to you.
        """.strip()