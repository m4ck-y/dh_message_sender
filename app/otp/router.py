from fastapi import APIRouter, HTTPException, status
from app.otp.controller import OTPApplication
from app.otp.models import OTPRequest, OTPResponse, WelcomeRequest

controller = OTPApplication()

MODULE_NAME = "messages"

router_otp = APIRouter(
    prefix="/emails", # Maintained for path compatibility
    tags=[MODULE_NAME])

TAG_OTP = {
    "name": MODULE_NAME,
    "description": """
- 🔐 **User Messaging** - Identity Verification and Onboarding
- 🚀 **Channels:** Multi-channel routing engine (Email, SMS, WhatsApp)
"""
}

@router_otp.post("/send-otp", response_model=OTPResponse)
async def send_otp_code(request: OTPRequest) -> OTPResponse:
    """
    Dispatch an OTP verification code via the specified channel.
    """
    try:
        response = await controller.send_otp(request)
        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.message
            )
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal messaging error: {str(e)}"
        )

@router_otp.post("/welcome", response_model=OTPResponse)
async def send_welcome_message(request: WelcomeRequest) -> OTPResponse:
    """
    Dispatch a personalized welcome message to a new user.
    """
    try:
        response = await controller.send_welcome(request)
        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.message
            )
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal messaging error: {str(e)}"
        )

@router_otp.post("/send-otp-legacy")
async def send_otp_legacy(email: str, code: str):
    """
    Legacy compatibility endpoint for OTP dispatch.
    """
    try:
        request = OTPRequest(email=email, code=code)
        response = await controller.send_otp(request)
        if not response.success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=response.message
            )
        return {"success": True, "sent_to": email}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )