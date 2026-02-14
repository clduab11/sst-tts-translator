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
        import os
        
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
        """Transcribe streaming audio using Deepgram v3 SDK."""
        from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions
        
        try:
            # Initialize client
            dg_client = DeepgramClient(self.api_key)
            
            # Connect to live transcription
            dg_connection = dg_client.listen.websocket.v("1")
            
            # Set up event handler for transcription results
            transcripts = []
            
            def on_message(self, result, **kwargs):
                sentence = result.channel.alternatives[0].transcript
                if len(sentence) > 0:
                    transcripts.append(sentence)
            
            # Register event handler
            dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
            
            # Start connection with options
            options = LiveOptions(
                punctuate=True,
                interim_results=False,
            )
            
            if not await dg_connection.start(options):
                raise RuntimeError("Failed to start Deepgram connection")
            
            # Send audio chunks
            async for chunk in audio_stream:
                dg_connection.send(chunk)
            
            # Finish and wait for remaining results
            await dg_connection.finish()
            
            # Yield accumulated transcripts
            for transcript in transcripts:
                yield transcript
                
        except Exception as e:
            raise RuntimeError(f"Deepgram transcription error: {e}")
    
    async def transcribe_file(self, audio_data: bytes) -> str:
        """Transcribe complete audio file using Deepgram v3 SDK."""
        from deepgram import DeepgramClient, PrerecordedOptions
        
        dg_client = DeepgramClient(self.api_key)
        
        # Create payload
        payload = {"buffer": audio_data}
        
        # Configure options
        options = PrerecordedOptions(
            punctuate=True
        )
        
        # Transcribe
        response = dg_client.listen.rest.v("1").transcribe_file(payload, options)
        
        # Extract transcript
        if response and response.results:
            channels = response.results.channels
            if channels and len(channels) > 0:
                alternatives = channels[0].alternatives
                if alternatives and len(alternatives) > 0:
                    return alternatives[0].transcript.strip()
        
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
