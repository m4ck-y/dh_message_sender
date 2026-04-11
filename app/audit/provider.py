from app.audit.repository import InMemoryAuditRepository

# Simple singleton provider for the in-memory repository
_audit_repo = InMemoryAuditRepository()

def get_audit_repository():
    return _audit_repo
