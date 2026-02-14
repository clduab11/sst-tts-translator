"""Text-to-Speech module with support for multiple providers."""

import html
from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional
import asyncio


class TTSProvider(ABC):
    """Abstract base class for TTS providers."""

    @abstractmethod
    async def synthesize(self, text: str, voice: str = "default") -> bytes:
        """
        Convert text to audio bytes.

        Args:
            text: Text to synthesize
            voice: Voice identifier

        Returns:
            Synthesized audio as bytes
        """
        pass

    @abstractmethod
    async def synthesize_stream(
        self, text: str, voice: str = "default"
    ) -> AsyncIterator[bytes]:
        """
        Stream synthesized audio chunks.

        Args:
            text: Text to synthesize
            voice: Voice identifier

        Yields:
            Audio data chunks
        """
        pass


class PiperTTS(TTSProvider):
    """Piper TTS implementation for local/offline synthesis."""

    def __init__(self, model_path: str = "en_US-lessac-medium"):
        """
        Initialize Piper TTS.

        Args:
            model_path: Path or name of the Piper voice model
        """
        self.model_path = model_path
        self._piper = None

    async def _load_model(self):
        """Lazy load Piper model."""
        if self._piper is None:
            try:
                import piper
            except ImportError:
                raise RuntimeError(
                    "Piper TTS not available - install piper-tts"
                )
            # Load model in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            try:
                self._piper = await loop.run_in_executor(
                    None, piper.PiperVoice.load, self.model_path
                )
            except Exception as e:
                raise RuntimeError(
                    f"Failed to load Piper model '{self.model_path}': {e}"
                ) from e

    async def synthesize(self, text: str, voice: str = "default") -> bytes:
        """Synthesize text to audio bytes using Piper."""
        await self._load_model()

        import io
        import wave

        buffer = io.BytesIO()

        # Run synthesis in thread pool to avoid blocking
        loop = asyncio.get_event_loop()

        def _synthesize():
            with wave.open(buffer, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self._piper.config.sample_rate)
                self._piper.synthesize(text, wav_file)
            return buffer.getvalue()

        return await loop.run_in_executor(None, _synthesize)

    async def synthesize_stream(
        self, text: str, voice: str = "default"
    ) -> AsyncIterator[bytes]:
        """Stream synthesized audio chunks using Piper."""
        await self._load_model()

        loop = asyncio.get_event_loop()

        def _synthesize_raw():
            return list(self._piper.synthesize_stream_raw(text))

        chunks = await loop.run_in_executor(None, _synthesize_raw)
        for chunk in chunks:
            yield chunk


class ElevenLabsTTS(TTSProvider):
    """ElevenLabs TTS implementation with streaming support."""

    DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"
    DEFAULT_MODEL_ID = "eleven_monolingual_v1"

    def __init__(self, api_key: str):
        """
        Initialize ElevenLabs TTS.

        Args:
            api_key: ElevenLabs API key
        """
        self.api_key = api_key

    async def synthesize(self, text: str, voice: str = "default") -> bytes:
        """Synthesize text to audio bytes using ElevenLabs API."""
        import httpx

        voice_id = voice if voice != "default" else self.DEFAULT_VOICE_ID
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={
                        "text": text,
                        "model_id": self.DEFAULT_MODEL_ID,
                    },
                    headers={"xi-api-key": self.api_key},
                    timeout=30.0,
                )
                response.raise_for_status()
                return response.content
        except httpx.HTTPStatusError as e:
            safe_text = html.escape(text[:50])
            detail = html.escape(e.response.text[:200]) if e.response.text else ""
            raise RuntimeError(
                f"ElevenLabs API error for text '{safe_text}...': "
                f"{e.response.status_code} {detail}"
            ) from e
        except Exception as e:
            raise RuntimeError(f"ElevenLabs synthesis error: {e}") from e

    async def synthesize_stream(
        self, text: str, voice: str = "default"
    ) -> AsyncIterator[bytes]:
        """Stream synthesized audio chunks using ElevenLabs API."""
        import httpx

        voice_id = voice if voice != "default" else self.DEFAULT_VOICE_ID
        url = (
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"
        )

        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    url,
                    json={
                        "text": text,
                        "model_id": self.DEFAULT_MODEL_ID,
                    },
                    headers={"xi-api-key": self.api_key},
                    timeout=30.0,
                ) as response:
                    response.raise_for_status()
                    async for chunk in response.aiter_bytes():
                        yield chunk
        except httpx.HTTPStatusError as e:
            safe_text = html.escape(text[:50])
            detail = html.escape(e.response.text[:200]) if e.response.text else ""
            raise RuntimeError(
                f"ElevenLabs streaming error for text '{safe_text}...': "
                f"{e.response.status_code} {detail}"
            ) from e
        except Exception as e:
            raise RuntimeError(
                f"ElevenLabs streaming error: {e}"
            ) from e


def create_tts_provider(
    provider: str,
    api_key: Optional[str] = None,
) -> TTSProvider:
    """
    Factory function to create TTS provider.

    Args:
        provider: Provider name ('piper' or 'elevenlabs')
        api_key: API key for provider (required for elevenlabs)

    Returns:
        TTS provider instance
    """
    if provider.lower() == "piper":
        return PiperTTS()
    elif provider.lower() == "elevenlabs":
        if not api_key:
            raise ValueError("API key required for ElevenLabs")
        return ElevenLabsTTS(api_key)
    else:
        raise ValueError(f"Unknown TTS provider: {provider}")
