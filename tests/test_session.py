"""Tests for session management module."""

import pytest
from sst_tts_translator.session import Session, SessionManager


def test_session_creation():
    """Test creating a session."""
    manager = SessionManager()
    session = manager.create_session()
    assert session.session_id is not None
    assert session.created_at is not None
    assert session.history == []
    assert session.context == {}


def test_session_creation_with_context():
    """Test creating a session with context."""
    manager = SessionManager()
    context = {"language": "python", "project": "test"}
    session = manager.create_session(context=context)
    assert session.context == context


def test_session_add_entry():
    """Test adding entries to a session."""
    session = Session(session_id="test-id", created_at="2024-01-01T00:00:00")
    session.add_entry("user", "create a REST API")
    
    assert len(session.history) == 1
    assert session.history[0]["role"] == "user"
    assert session.history[0]["content"] == "create a REST API"
    assert "timestamp" in session.history[0]


def test_session_get_summary():
    """Test session summary."""
    session = Session(
        session_id="test-id",
        created_at="2024-01-01T00:00:00",
        context={"language": "python"}
    )
    session.add_entry("user", "hello")
    
    summary = session.get_summary()
    assert summary["session_id"] == "test-id"
    assert summary["entries"] == 1
    assert summary["context"]["language"] == "python"


def test_session_manager_get():
    """Test getting a session by ID."""
    manager = SessionManager()
    session = manager.create_session()
    
    retrieved = manager.get_session(session.session_id)
    assert retrieved is not None
    assert retrieved.session_id == session.session_id


def test_session_manager_get_nonexistent():
    """Test getting a nonexistent session."""
    manager = SessionManager()
    assert manager.get_session("nonexistent") is None


def test_session_manager_list():
    """Test listing sessions."""
    manager = SessionManager()
    manager.create_session()
    manager.create_session()
    
    sessions = manager.list_sessions()
    assert len(sessions) == 2


def test_session_manager_delete():
    """Test deleting a session."""
    manager = SessionManager()
    session = manager.create_session()
    
    assert manager.delete_session(session.session_id) is True
    assert manager.get_session(session.session_id) is None


def test_session_manager_delete_nonexistent():
    """Test deleting a nonexistent session."""
    manager = SessionManager()
    assert manager.delete_session("nonexistent") is False


def test_session_manager_add_to_session():
    """Test adding entry via manager."""
    manager = SessionManager()
    session = manager.create_session()
    
    assert manager.add_to_session(session.session_id, "user", "test") is True
    retrieved = manager.get_session(session.session_id)
    assert len(retrieved.history) == 1


def test_session_manager_add_to_nonexistent():
    """Test adding entry to nonexistent session."""
    manager = SessionManager()
    assert manager.add_to_session("nonexistent", "user", "test") is False


def test_session_manager_enforce_limit():
    """Test that session manager enforces max session limit."""
    manager = SessionManager(max_sessions=3)
    
    ids = []
    for _ in range(5):
        session = manager.create_session()
        ids.append(session.session_id)
    
    sessions = manager.list_sessions()
    assert len(sessions) == 3
    
    # Oldest sessions should have been evicted
    assert manager.get_session(ids[0]) is None
    assert manager.get_session(ids[1]) is None
    assert manager.get_session(ids[4]) is not None
