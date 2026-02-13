"""Tests for STT module."""

import pytest
from sst_tts_translator.stt import WhisperSTT, create_stt_provider


@pytest.mark.asyncio
async def test_create_whisper_provider():
    """Test creating Whisper STT provider."""
    provider = create_stt_provider("whisper")
    assert isinstance(provider, WhisperSTT)


def test_create_deepgram_provider():
    """Test creating Deepgram STT provider requires API key."""
    with pytest.raises(ValueError, match="API key required"):
        create_stt_provider("deepgram")


def test_create_unknown_provider():
    """Test creating unknown provider raises error."""
    with pytest.raises(ValueError, match="Unknown STT provider"):
        create_stt_provider("unknown")
