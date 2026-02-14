"""Configuration management for SST/TTS Translator."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False
    
    # STT Provider
    stt_provider: str = "whisper"  # whisper or deepgram
    deepgram_api_key: Optional[str] = None
    
    # LLM Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_llm_provider: str = "openai"
    default_llm_model: str = "gpt-4"
    
    # TTS Provider
    tts_provider: str = "piper"  # piper or elevenlabs
    elevenlabs_api_key: Optional[str] = None
    
    # Audio Configuration
    audio_sample_rate: int = 16000
    audio_chunk_size: int = 1024
    max_audio_duration: int = 300  # seconds
    
    # Prompt Configuration
    prompt_template_dir: str = "./templates"
    enable_cot: bool = True  # Chain of Thought
    
    # Session Configuration
    max_sessions: int = 100
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
