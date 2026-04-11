from fastapi import APIRouter, HTTPException, status
from app.waitlist.controller import WaitlistApplication
from app.waitlist.models import WaitlistRequest, WaitlistResponse

controller = WaitlistApplication()

MODULE_NAME = "waitlist"

router_waitlist = APIRouter(
    prefix=f"/{MODULE_NAME}",
    tags=[MODULE_NAME])

TAG_WAITLIST = {
    "name": MODULE_NAME,
    "description": """
- ⏳ **Waitlist Management** - Multi-channel Registration and Confirmations
- 🚀 **Automation:** Notifications triggered by user interest in specific offerings
"""
}

@router_waitlist.post("/send-confirmation", response_model=WaitlistResponse)
async def send_waitlist_confirmation(request: WaitlistRequest) -> WaitlistResponse:
    """
    Dispatch a waitlist registration confirmation via the specified channel.
    """
    try:
        response = await controller.send_confirmation(request)
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
            detail=f"Internal waitlist messaging error: {str(e)}"
        )