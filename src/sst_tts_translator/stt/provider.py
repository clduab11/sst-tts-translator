"""Speech-to-Text module with support for multiple providers."""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional
import asyncio
import io


class STTProvider(ABC):
    """Abstract base class for STT providers."""
    
    @abstractmethod
    async def transcribe_stream(
        self, 
        audio_stream: AsyncIterator[bytes]
    ) -> AsyncIterator[str]:
        """
        Transcribe streaming audio to text.
        
        Args:
            audio_stream: Async iterator of audio chunks
            
        Yields:
            Transcribed text chunks
        """
        pass
    
    @abstractmethod
    async def transcribe_file(self, audio_data: bytes) -> str:
        """
        Transcribe complete audio file to text.
        
        Args:
            audio_data: Complete audio file as bytes
            
        Returns:
            Transcribed text
        """
        pass


class WhisperSTT(STTProvider):
    """OpenAI Whisper STT implementation."""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize Whisper STT.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self._model = None
    
    async def _load_model(self):
        """Lazy load Whisper model."""
        if self._model is None:
            import whisper
            # Load model in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            self._model = await loop.run_in_executor(
                None, whisper.load_model, self.model_size
            )
    
    async def transcribe_stream(
        self, 
        audio_stream: AsyncIterator[bytes]
    ) -> AsyncIterator[str]:
        """Transcribe streaming audio using Whisper."""
        await self._load_model()
        
        # Buffer audio chunks
        buffer = io.BytesIO()
        async for chunk in audio_stream:
            buffer.write(chunk)
        
        # Transcribe buffered audio
        buffer.seek(0)
        audio_data = buffer.read()
        
        if audio_data:
            text = await self.transcribe_file(audio_data)
            yield text
    
    async def transcribe_file(self, audio_data: bytes) -> str:
        """Transcribe complete audio file using Whisper."""
        await self._load_model()
        
        # Save to temporary file and transcribe
        import tempfile
        import numpy as np
        import soundfile as sf
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name
        
        try:
            # Run transcription in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._model.transcribe, 
                tmp_path
            )
            return result.get("text", "").strip()
        finally:
            import os
            os.unlink(tmp_path)


class DeepgramSTT(STTProvider):
    """Deepgram STT implementation with streaming support."""
    
    def __init__(self, api_key: str):
        """
        Initialize Deepgram STT.
        
        Args:
            api_key: Deepgram API key
        """
        self.api_key = api_key
    
    async def transcribe_stream(
        self, 
        audio_stream: AsyncIterator[bytes]
    ) -> AsyncIterator[str]:
        """Transcribe streaming audio using Deepgram."""
        from deepgram import Deepgram
        
        dg_client = Deepgram(self.api_key)
        
        # Set up streaming transcription
        try:
            async def audio_generator():
                async for chunk in audio_stream:
                    yield chunk
            
            response = await dg_client.transcription.live({
                'punctuate': True,
                'interim_results': False,
            })
            
            async for chunk in audio_generator():
                response.send(chunk)
                
                # Get transcription
                result = await response.get_transcript()
                if result and result.get('channel'):
                    alternatives = result['channel'].get('alternatives', [])
                    if alternatives:
                        transcript = alternatives[0].get('transcript', '')
                        if transcript:
                            yield transcript
            
            response.finish()
            
        except Exception as e:
            raise RuntimeError(f"Deepgram transcription error: {e}")
    
    async def transcribe_file(self, audio_data: bytes) -> str:
        """Transcribe complete audio file using Deepgram."""
        from deepgram import Deepgram
        
        dg_client = Deepgram(self.api_key)
        
        source = {'buffer': audio_data, 'mimetype': 'audio/wav'}
        response = await dg_client.transcription.prerecorded(
            source,
            {'punctuate': True}
        )
        
        # Extract transcript
        results = response.get('results', {})
        channels = results.get('channels', [])
        if channels:
            alternatives = channels[0].get('alternatives', [])
            if alternatives:
                return alternatives[0].get('transcript', '').strip()
        
        return ""


def create_stt_provider(
    provider: str, 
    api_key: Optional[str] = None
) -> STTProvider:
    """
    Factory function to create STT provider.
    
    Args:
        provider: Provider name ('whisper' or 'deepgram')
        api_key: API key for provider (required for deepgram)
        
    Returns:
        STT provider instance
    """
    if provider.lower() == "whisper":
        return WhisperSTT()
    elif provider.lower() == "deepgram":
        if not api_key:
            raise ValueError("API key required for Deepgram")
        return DeepgramSTT(api_key)
    else:
        raise ValueError(f"Unknown STT provider: {provider}")
