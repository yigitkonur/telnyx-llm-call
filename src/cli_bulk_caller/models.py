"""
Data models for Telnyx Transcribe.

Provides type-safe representations of calls, transcriptions, and related data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class CallStatus(str, Enum):
    """Status of a call in the system."""
    
    PENDING = "pending"
    INITIATED = "initiated"
    RINGING = "ringing"
    ANSWERED = "answered"
    RECORDING = "recording"
    COMPLETED = "completed"
    FAILED = "failed"
    TRANSCRIBING = "transcribing"
    TRANSCRIBED = "transcribed"
    
    def __str__(self) -> str:
        return self.value


class TranscriptionStatus(str, Enum):
    """Status of a transcription job."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    
    def __str__(self) -> str:
        return self.value


@dataclass
class Call:
    """
    Represents an active or completed call.
    
    Attributes:
        call_control_id: Unique identifier for call control operations.
        to_number: The destination phone number (E.164 format).
        from_number: The originating phone number (E.164 format).
        status: Current status of the call.
        initiated_at: When the call was initiated.
        answered_at: When the call was answered (if applicable).
        ended_at: When the call ended (if applicable).
        duration_seconds: Total duration of the call in seconds.
        recording_url: URL to download the call recording.
        transcription: The transcribed text (if transcription completed).
        error_message: Error message if the call failed.
    """
    
    call_control_id: str
    to_number: str
    from_number: str
    status: CallStatus = CallStatus.PENDING
    initiated_at: datetime = field(default_factory=datetime.now)
    answered_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    recording_url: Optional[str] = None
    transcription: Optional[str] = None
    error_message: Optional[str] = None
    
    def mark_answered(self) -> None:
        """Mark the call as answered."""
        self.status = CallStatus.ANSWERED
        self.answered_at = datetime.now()
    
    def mark_recording(self) -> None:
        """Mark the call as recording."""
        self.status = CallStatus.RECORDING
    
    def mark_completed(self, duration: Optional[float] = None) -> None:
        """Mark the call as completed."""
        self.status = CallStatus.COMPLETED
        self.ended_at = datetime.now()
        if duration is not None:
            self.duration_seconds = duration
        elif self.answered_at:
            self.duration_seconds = (self.ended_at - self.answered_at).total_seconds()
    
    def mark_failed(self, error: str) -> None:
        """Mark the call as failed with an error message."""
        self.status = CallStatus.FAILED
        self.ended_at = datetime.now()
        self.error_message = error
    
    def mark_transcribed(self, text: str) -> None:
        """Mark the call as transcribed with the resulting text."""
        self.status = CallStatus.TRANSCRIBED
        self.transcription = text
    
    @property
    def is_active(self) -> bool:
        """Check if the call is still active (not completed or failed)."""
        return self.status not in (CallStatus.COMPLETED, CallStatus.FAILED, CallStatus.TRANSCRIBED)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "call_control_id": self.call_control_id,
            "to_number": self.to_number,
            "from_number": self.from_number,
            "status": str(self.status),
            "initiated_at": self.initiated_at.isoformat() if self.initiated_at else None,
            "answered_at": self.answered_at.isoformat() if self.answered_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_seconds": self.duration_seconds,
            "recording_url": self.recording_url,
            "transcription": self.transcription,
            "error_message": self.error_message,
        }


@dataclass
class TranscriptionResult:
    """
    Represents a transcription result.
    
    Attributes:
        filename: Source audio filename or call identifier.
        text: The transcribed text.
        status: Status of the transcription.
        duration_seconds: Duration of the audio in seconds.
        language: Detected language of the audio.
        created_at: When the transcription was created.
        error_message: Error message if transcription failed.
    """
    
    filename: str
    text: str = ""
    status: TranscriptionStatus = TranscriptionStatus.PENDING
    duration_seconds: Optional[float] = None
    language: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
    
    @classmethod
    def success(
        cls,
        filename: str,
        text: str,
        duration: Optional[float] = None,
        language: Optional[str] = None,
    ) -> TranscriptionResult:
        """Create a successful transcription result."""
        return cls(
            filename=filename,
            text=text,
            status=TranscriptionStatus.COMPLETED,
            duration_seconds=duration,
            language=language,
        )
    
    @classmethod
    def failure(cls, filename: str, error: str) -> TranscriptionResult:
        """Create a failed transcription result."""
        return cls(
            filename=filename,
            status=TranscriptionStatus.FAILED,
            error_message=error,
        )
    
    @property
    def is_success(self) -> bool:
        """Check if the transcription was successful."""
        return self.status == TranscriptionStatus.COMPLETED
    
    def to_row(self) -> list[str]:
        """Convert to a row for TSV output."""
        return [
            self.filename,
            self.text,
            str(self.duration_seconds or ""),
            self.language or "",
        ]


@dataclass
class CallTranscriptionResult:
    """
    Combined result of a call and its transcription.
    
    This is the final output format written to the results file.
    """
    
    from_number: str
    to_number: str
    transcription: str
    duration_seconds: float
    call_control_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_row(self) -> list[str]:
        """Convert to a row for TSV output."""
        return [
            self.from_number,
            self.to_number,
            self.transcription,
            f"{self.duration_seconds:.2f}",
        ]
    
    @staticmethod
    def header() -> list[str]:
        """Get the TSV header row."""
        return ["From Number", "To Number", "Transcription", "Duration (seconds)"]
