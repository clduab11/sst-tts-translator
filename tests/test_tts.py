"""Tests for TTS (Text-to-Speech) module."""

import pytest
from sst_tts_translator.tts import PiperTTS, ElevenLabsTTS, create_tts_provider


def test_create_piper_provider():
    """Test creating Piper TTS provider."""
    provider = create_tts_provider("piper")
    assert isinstance(provider, PiperTTS)


def test_create_elevenlabs_provider():
    """Test creating ElevenLabs TTS provider requires API key."""
    with pytest.raises(ValueError, match="API key required"):
        create_tts_provider("elevenlabs")


def test_create_elevenlabs_with_key():
    """Test creating ElevenLabs TTS provider with API key."""
    provider = create_tts_provider("elevenlabs", api_key="test_key")
    assert isinstance(provider, ElevenLabsTTS)


def test_create_unknown_tts_provider():
    """Test creating unknown TTS provider raises error."""
    with pytest.raises(ValueError, match="Unknown TTS provider"):
        create_tts_provider("unknown")


def test_piper_tts_model_path():
    """Test PiperTTS stores model path."""
    provider = PiperTTS(model_path="custom_model")
    assert provider.model_path == "custom_model"


def test_elevenlabs_default_constants():
    """Test ElevenLabs default constants."""
    provider = ElevenLabsTTS(api_key="test_key")
    assert provider.DEFAULT_VOICE_ID == "21m00Tcm4TlvDq8ikWAM"
    assert provider.DEFAULT_MODEL_ID == "eleven_monolingual_v1"
