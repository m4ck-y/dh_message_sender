from abc import ABC, abstractmethod
from typing import List
from app.audit.models import MessageAuditEntry

class IAuditRepository(ABC):
    @abstractmethod
    def save(self, entry: MessageAuditEntry) -> None:
        pass

    @abstractmethod
    def get_all(self, limit: int = 100) -> List[MessageAuditEntry]:
        pass

class InMemoryAuditRepository(IAuditRepository):
    def __init__(self):
        self._logs: List[MessageAuditEntry] = []

    def save(self, entry: MessageAuditEntry) -> None:
        self._logs.append(entry)

    def get_all(self, limit: int = 100) -> List[MessageAuditEntry]:
        # Return last N logs, sorted by timestamp descending
        sorted_logs = sorted(self._logs, key=lambda x: x.timestamp, reverse=True)
        return sorted_logs[:limit]
