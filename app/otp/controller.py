from datetime import datetime
from typing import Optional
from jinja2 import Environment, FileSystemLoader

from app.config import settings
from app.otp.models import OTPRequest, OTPResponse, WelcomeRequest
from app.core.messaging.models import MessagePayload, MessageChannel
from app.core.messaging.dispatcher import get_dispatcher

TEMPLATES_DIR = "app/templates"

class OTPApplication:
    """
    Application service for managing User-related messages such as OTP and Welcome notifications.
    """
    def __init__(self):
        print(f"[INFO] Initializing OTPApplication with templates at: {TEMPLATES_DIR}")
        self.jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
        self.dispatcher = get_dispatcher()

    async def send_otp(self, request: OTPRequest) -> OTPResponse:
        """
        Dispatches an OTP verification code via the specified channel.
        """
        try:
            template = self.jinja_env.get_template("otp.html")
            
            show_expiry = request.expiry_minutes is not None and request.expiry_minutes > 0
            show_redirect_button = request.redirect_url is not None and request.redirect_url.strip() != ""
            
            context = {
                "email": request.email,
                "otp_code": request.code,
                "app_name": settings.APP_NAME,
                "logo_url": settings.COMPANY_LOGO_URL,
                "expiry_minutes": request.expiry_minutes,
                "show_expiry": show_expiry,
                "redirect_url": request.redirect_url,
                "show_redirect_button": show_redirect_button,
                "company_name": settings.COMPANY_NAME,
                "support_email": settings.SUPPORT_EMAIL,
                "website_url": settings.WEBSITE_URL
            }
            
            html_content = template.render(context)
            
            payload = MessagePayload(
                recipient=request.email,
                subject="Verification Code",
                body_html=html_content,
                channel=request.channel,
                payload_details={
                    "code": request.code,
                    "expiry_minutes": request.expiry_minutes
                },
                metadata={
                    "message_type": "OTP",
                    "sender": settings.SMTP_FROM_EMAIL
                }
            )
            
            await self.dispatcher.dispatch(payload)
            
            return OTPResponse(
                success=True,
                message="Code dispatched successfully",
                sent_to=request.email,
                timestamp=datetime.utcnow().isoformat() + "Z",
                expiry_minutes=request.expiry_minutes,
                has_action_button=show_redirect_button,
                logo_used=settings.COMPANY_LOGO_URL
            )
                
        except Exception as e:
            print(f"[ERROR] Dispatch error in send_otp: {str(e)}")
            return OTPResponse(
                success=False,
                message=f"Dispatch failed: {str(e)}",
                sent_to=request.email if 'request' in locals() else "Unknown",
                timestamp=datetime.utcnow().isoformat() + "Z"
            )

    async def send_welcome(self, request: WelcomeRequest) -> OTPResponse:
        """
        Dispatches a welcome notification to a new user via the specified channel.
        """
        try:
            template = self.jinja_env.get_template("welcome.html")
            
            context = {
                "email": request.email,
                "user_name": request.user_name,
                "app_name": settings.APP_NAME,
                "logo_url": settings.COMPANY_LOGO_URL,
                "login_url": request.login_url,
                "company_name": settings.COMPANY_NAME,
                "support_email": settings.SUPPORT_EMAIL,
                "website_url": settings.WEBSITE_URL,
                "current_year": datetime.now().year
            }
            
            html_content = template.render(context)
            
            payload = MessagePayload(
                recipient=request.email,
                subject=f"Welcome to {settings.APP_NAME}",
                body_html=html_content,
                channel=request.channel,
                payload_details={
                    "user_name": request.user_name,
                    "login_url": request.login_url
                },
                metadata={
                    "message_type": "Welcome",
                    "sender": settings.SMTP_FROM_EMAIL
                }
            )
            
            await self.dispatcher.dispatch(payload)
            
            return OTPResponse(
                success=True,
                message="Welcome message dispatched successfully",
                sent_to=request.email,
                timestamp=datetime.utcnow().isoformat() + "Z",
                has_action_button=bool(request.login_url),
                logo_used=settings.COMPANY_LOGO_URL
            )
        except Exception as e:
            print(f"[ERROR] Dispatch error in send_welcome: {str(e)}")
            return OTPResponse(
                success=False,
                message=f"Welcome dispatch failed: {str(e)}",
                sent_to=request.email if 'request' in locals() else "Unknown",
                timestamp=datetime.utcnow().isoformat() + "Z"
            )