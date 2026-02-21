"""
Configuration management for Telnyx Transcribe.

Supports environment variables, .env files, and programmatic configuration.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Settings:
    """
    Application settings with smart defaults and environment variable support.
    
    Attributes:
        telnyx_api_key: Telnyx API key for call management.
        telnyx_connection_id: Telnyx connection ID for outbound calls.
        telnyx_from_number: The phone number to make calls from (E.164 format).
        openai_api_key: OpenAI API key for Whisper transcription.
        audio_url: URL of the audio file to play during calls.
        webhook_port: Port for the Flask webhook server.
        webhook_host: Host for the Flask webhook server.
        output_file: Path to the output TSV file for transcriptions.
        numbers_file: Path to the file containing phone numbers.
        max_workers: Maximum concurrent calls/transcriptions.
        recording_format: Audio format for call recordings.
        recording_channels: Audio channels for recordings.
        max_retries: Maximum retries for API calls.
        retry_delay: Base delay between retries (exponential backoff).
    """
    
    # Required API credentials
    telnyx_api_key: str = field(default_factory=lambda: os.getenv("TELNYX_API_KEY", ""))
    telnyx_connection_id: str = field(default_factory=lambda: os.getenv("TELNYX_CONNECTION_ID", ""))
    telnyx_from_number: str = field(default_factory=lambda: os.getenv("TELNYX_FROM_NUMBER", ""))
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    
    # Call configuration
    audio_url: str = field(default_factory=lambda: os.getenv("AUDIO_URL", ""))
    
    # Server configuration
    webhook_port: int = field(default_factory=lambda: int(os.getenv("WEBHOOK_PORT", "5000")))
    webhook_host: str = field(default_factory=lambda: os.getenv("WEBHOOK_HOST", "0.0.0.0"))
    
    # Output configuration
    output_file: Path = field(default_factory=lambda: Path(os.getenv("OUTPUT_FILE", "results.tsv")))
    numbers_file: Optional[Path] = field(default=None)
    
    # Performance configuration
    max_workers: int = field(default_factory=lambda: int(os.getenv("MAX_WORKERS", "5")))
    
    # Recording configuration
    recording_format: str = field(default_factory=lambda: os.getenv("RECORDING_FORMAT", "mp3"))
    recording_channels: str = field(default_factory=lambda: os.getenv("RECORDING_CHANNELS", "single"))
    
    # Retry configuration
    max_retries: int = field(default_factory=lambda: int(os.getenv("MAX_RETRIES", "10")))
    retry_delay: float = field(default_factory=lambda: float(os.getenv("RETRY_DELAY", "2.0")))
    
    @classmethod
    def from_env(cls, env_file: Optional[Path] = None) -> Settings:
        """
        Load settings from environment variables, optionally loading a .env file first.
        
        Args:
            env_file: Optional path to a .env file to load.
            
        Returns:
            Settings instance populated from environment.
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()  # Try to load .env from current directory
        
        return cls()
    
    def validate(self) -> list[str]:
        """
        Validate that all required settings are present.
        
        Returns:
            List of validation error messages. Empty if valid.
        """
        errors: list[str] = []
        
        if not self.telnyx_api_key:
            errors.append("TELNYX_API_KEY is required")
        if not self.telnyx_connection_id:
            errors.append("TELNYX_CONNECTION_ID is required")
        if not self.telnyx_from_number:
            errors.append("TELNYX_FROM_NUMBER is required")
        if not self.openai_api_key:
            errors.append("OPENAI_API_KEY is required")
        if not self.audio_url:
            errors.append("AUDIO_URL is required for call playback")
            
        return errors
    
    def validate_for_transcription_only(self) -> list[str]:
        """
        Validate settings for standalone transcription mode (no Telnyx required).
        
        Returns:
            List of validation error messages. Empty if valid.
        """
        errors: list[str] = []
        
        if not self.openai_api_key:
            errors.append("OPENAI_API_KEY is required")
            
        return errors
    
    @property
    def is_valid(self) -> bool:
        """Check if all required settings are valid."""
        return len(self.validate()) == 0
    
    @property
    def is_valid_for_transcription(self) -> bool:
        """Check if settings are valid for transcription-only mode."""
        return len(self.validate_for_transcription_only()) == 0


def get_settings() -> Settings:
    """
    Get the global settings instance.
    
    This is the recommended way to access settings throughout the application.
    
    Returns:
        Configured Settings instance.
    """
    return Settings.from_env()
