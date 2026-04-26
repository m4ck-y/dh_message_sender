from fastapi import APIRouter, HTTPException, status
from app.waitlist.controller import WaitlistApplication
from app.waitlist.models import WaitlistRequest, WaitlistResponse, InviteRequest

controller = WaitlistApplication()

router_waitlist = APIRouter(prefix="/v1/waitlist", tags=["Waitlist"])

TAG_WAITLIST = {
    "name": "Waitlist",
    "description": (
        "Waitlist notification emails. "
        "`/confirmation` — sent when a lead registers to the waitlist (you're on the list, we'll notify you). "
        "`/invite` — sent when admin invites a lead to start the onboarding registration."
    ),
}


@router_waitlist.post("/confirmation", response_model=WaitlistResponse)
async def send_waitlist_confirmation(request: WaitlistRequest) -> WaitlistResponse:
    """
    Send a waitlist registration confirmation.

    Notifies the lead that they have been added to the waiting list
    and will be contacted when the product is available.
    """
    try:
        response = await controller.send_confirmation(request)
        if not response.success:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response.message)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Confirmation dispatch failed: {str(e)}")


@router_waitlist.post("/invite", response_model=WaitlistResponse)
async def send_waitlist_invite(request: InviteRequest) -> WaitlistResponse:
    """
    Send a waitlist invitation to start onboarding.

    Contains a secure token link. The lead clicks it to access
    the registration form and become an applicant.
    """
    try:
        response = await controller.send_invite(request)
        if not response.success:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response.message)
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Invite dispatch failed: {str(e)}")
