from fastapi import APIRouter, HTTPException, status
from app.otp.controller import OTPApplication
from app.otp.models import OTPRequest, OTPResponse, WelcomeRequest

controller = OTPApplication()

router_otp = APIRouter(prefix="/v1", tags=["OTP"])
router_notifications = APIRouter(prefix="/v1/notifications", tags=["Notifications"])

TAG_OTP = {
    "name": "OTP",
    "description": "Send OTP verification codes via Email, SMS, or WhatsApp. The code is generated and hashed by the calling service — this endpoint only dispatches it.",
}

TAG_NOTIFICATIONS = {
    "name": "Notifications",
    "description": "System notifications — welcome messages sent when an applicant is approved and becomes an active user.",
}


@router_otp.post("/otp", response_model=OTPResponse)
async def send_otp_code(request: OTPRequest) -> OTPResponse:
    """
    Dispatch an OTP verification code via the specified channel.

    Supports EMAIL, SMS, and WhatsApp. The `purpose` field customizes
    the email subject (login, password reset, sensitive action).
    """
    try:
        response = await controller.send_otp(request)
        if not response.success:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response.message)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"OTP dispatch failed: {str(e)}")


@router_notifications.post("/welcome", response_model=OTPResponse)
async def send_welcome_message(request: WelcomeRequest) -> OTPResponse:
    """
    Send a welcome notification to a newly approved user.

    Triggered when an admin approves an applicant — the applicant
    becomes an active user and receives this onboarding welcome email.
    """
    try:
        response = await controller.send_welcome(request)
        if not response.success:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response.message)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Welcome dispatch failed: {str(e)}")
