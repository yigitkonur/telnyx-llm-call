"""
Custom exceptions for Telnyx Transcribe.

Provides clear, specific error types for better error handling.
"""

from __future__ import annotations

from typing import Optional


class TelnyxTranscribeError(Exception):
    """Base exception for all Telnyx Transcribe errors."""
    
    def __init__(self, message: str, details: Optional[dict] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(TelnyxTranscribeError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, missing_keys: Optional[list[str]] = None) -> None:
        super().__init__(message, {"missing_keys": missing_keys or []})
        self.missing_keys = missing_keys or []


class TelnyxAPIError(TelnyxTranscribeError):
    """Raised when a Telnyx API call fails."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        api_error: Optional[str] = None,
    ) -> None:
        super().__init__(message, {"status_code": status_code, "api_error": api_error})
        self.status_code = status_code
        self.api_error = api_error


class CallError(TelnyxTranscribeError):
    """Raised when a call operation fails."""
    
    def __init__(
        self,
        message: str,
        call_control_id: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> None:
        super().__init__(
            message,
            {"call_control_id": call_control_id, "phone_number": phone_number},
        )
        self.call_control_id = call_control_id
        self.phone_number = phone_number


class TranscriptionError(TelnyxTranscribeError):
    """Raised when transcription fails."""
    
    def __init__(
        self,
        message: str,
        filename: Optional[str] = None,
        retry_count: int = 0,
    ) -> None:
        super().__init__(message, {"filename": filename, "retry_count": retry_count})
        self.filename = filename
        self.retry_count = retry_count


class RecordingError(TelnyxTranscribeError):
    """Raised when recording retrieval fails."""
    
    def __init__(
        self,
        message: str,
        recording_url: Optional[str] = None,
        call_control_id: Optional[str] = None,
    ) -> None:
        super().__init__(
            message,
            {"recording_url": recording_url, "call_control_id": call_control_id},
        )
        self.recording_url = recording_url
        self.call_control_id = call_control_id


class WebhookError(TelnyxTranscribeError):
    """Raised when webhook processing fails."""
    
    def __init__(
        self,
        message: str,
        event_type: Optional[str] = None,
        payload: Optional[dict] = None,
    ) -> None:
        super().__init__(message, {"event_type": event_type})
        self.event_type = event_type
        self.payload = payload
