"""
Tests for configuration module.
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from telnyx_transcribe.config import Settings, get_settings


class TestSettings:
    """Tests for Settings dataclass."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            
            assert settings.telnyx_api_key == ""
            assert settings.openai_api_key == ""
            assert settings.webhook_port == 5000
            assert settings.webhook_host == "0.0.0.0"
            assert settings.max_workers == 5
            assert settings.recording_format == "mp3"
    
    def test_from_environment(self):
        """Test loading settings from environment variables."""
        env_vars = {
            "TELNYX_API_KEY": "test_telnyx_key",
            "OPENAI_API_KEY": "test_openai_key",
            "WEBHOOK_PORT": "8080",
            "MAX_WORKERS": "10",
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            
            assert settings.telnyx_api_key == "test_telnyx_key"
            assert settings.openai_api_key == "test_openai_key"
            assert settings.webhook_port == 8080
            assert settings.max_workers == 10
    
    def test_validation_missing_keys(self):
        """Test validation returns errors for missing keys."""
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            errors = settings.validate()
            
            assert len(errors) > 0
            assert any("TELNYX_API_KEY" in e for e in errors)
            assert any("OPENAI_API_KEY" in e for e in errors)
    
    def test_validation_all_set(self):
        """Test validation passes with all required keys."""
        env_vars = {
            "TELNYX_API_KEY": "key1",
            "TELNYX_CONNECTION_ID": "conn1",
            "TELNYX_FROM_NUMBER": "+1234567890",
            "OPENAI_API_KEY": "key2",
            "AUDIO_URL": "https://example.com/audio.mp3",
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            errors = settings.validate()
            
            assert len(errors) == 0
            assert settings.is_valid
    
    def test_validate_for_transcription_only(self):
        """Test validation for transcription-only mode."""
        env_vars = {"OPENAI_API_KEY": "test_key"}
        
        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            errors = settings.validate_for_transcription_only()
            
            assert len(errors) == 0
            assert settings.is_valid_for_transcription


class TestGetSettings:
    """Tests for get_settings function."""
    
    def test_returns_settings_instance(self):
        """Test that get_settings returns a Settings instance."""
        settings = get_settings()
        assert isinstance(settings, Settings)
