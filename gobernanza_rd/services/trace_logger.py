"""Trace/audit logging interface."""
import uuid
from typing import Any, Dict, Optional, Protocol


class TraceLogger(Protocol):
    async def log_event(
        self,
        event_type: Any,
        event_data: Dict[str, Any],
        actor_user_id: Optional[uuid.UUID] = None,
        actor_session_id: Optional[uuid.UUID] = None,
        actor_identity_level: Optional[int] = None,
        actor_ip_hash: Optional[str] = None,
        actor_device_fingerprint: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[uuid.UUID] = None,
    ) -> Any:
        ...