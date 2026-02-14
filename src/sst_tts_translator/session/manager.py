"""Session management for voice development conversations."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class Session:
    """A voice development session tracking conversation history."""

    session_id: str
    created_at: str
    history: List[Dict[str, Any]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

    def add_entry(self, role: str, content: str) -> None:
        """Add a conversation entry with the current timestamp."""
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def get_summary(self) -> Dict[str, Any]:
        """Return a summary dict of this session."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "entries": len(self.history),
            "context": self.context,
        }


class SessionManager:
    """Manages voice development sessions with in-memory storage."""

    def __init__(self, max_sessions: int = 100) -> None:
        """Initialize with configurable max session count."""
        self._sessions: Dict[str, Session] = {}
        self._max_sessions: int = max_sessions

    def create_session(self, context: Optional[Dict[str, Any]] = None) -> Session:
        """Create a new session with a UUID4 id."""
        session = Session(
            session_id=str(uuid.uuid4()),
            created_at=datetime.now(timezone.utc).isoformat(),
            context=context if context is not None else {},
        )
        self._sessions[session.session_id] = session
        self._enforce_limit()
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID, or None."""
        return self._sessions.get(session_id)

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all session summaries."""
        return [session.get_summary() for session in self._sessions.values()]

    def delete_session(self, session_id: str) -> bool:
        """Delete a session. Returns True if found and deleted."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def add_to_session(self, session_id: str, role: str, content: str) -> bool:
        """Add entry to session. Returns True if session found."""
        session = self._sessions.get(session_id)
        if session is None:
            return False
        session.add_entry(role, content)
        return True

    def _enforce_limit(self) -> None:
        """Remove oldest sessions if over max limit."""
        while len(self._sessions) > self._max_sessions:
            oldest_id = min(
                self._sessions,
                key=lambda sid: self._sessions[sid].created_at,
            )
            del self._sessions[oldest_id]
