from fastapi import APIRouter, Query
from typing import List
from app.audit.models import MessageAuditEntry
from app.audit.provider import get_audit_repository

router_audit = APIRouter(prefix="/audit", tags=["Audit"])

@router_audit.get("/logs", response_model=List[MessageAuditEntry])
async def get_audit_logs(
    limit: int = Query(default=10, ge=1, le=100, description="Number of logs to return")
):
    """
    Retrieve the most recent message audit logs.
    """
    repo = get_audit_repository()
    return repo.get_all(limit=limit)
