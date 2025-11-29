"""
Tests for data models.
"""

from datetime import datetime

import pytest

from telnyx_transcribe.models import (
    Call,
    CallStatus,
    CallTranscriptionResult,
    TranscriptionResult,
    TranscriptionStatus,
)


class TestCallStatus:
    """Tests for CallStatus enum."""
    
    def test_string_conversion(self):
        """Test string conversion of status."""
        assert str(CallStatus.PENDING) == "pending"
        assert str(CallStatus.ANSWERED) == "answered"
        assert str(CallStatus.COMPLETED) == "completed"


class TestCall:
    """Tests for Call dataclass."""
    
    def test_creation(self):
        """Test creating a Call instance."""
        call = Call(
            call_control_id="test_id",
            to_number="+1234567890",
            from_number="+0987654321",
        )
        
        assert call.call_control_id == "test_id"
        assert call.to_number == "+1234567890"
        assert call.from_number == "+0987654321"
        assert call.status == CallStatus.PENDING
        assert call.is_active
    
    def test_mark_answered(self):
        """Test marking a call as answered."""
        call = Call(
            call_control_id="test_id",
            to_number="+1234567890",
            from_number="+0987654321",
        )
        
        call.mark_answered()
        
        assert call.status == CallStatus.ANSWERED
        assert call.answered_at is not None
        assert call.is_active
    
    def test_mark_completed(self):
        """Test marking a call as completed."""
        call = Call(
            call_control_id="test_id",
            to_number="+1234567890",
            from_number="+0987654321",
        )
        
        call.mark_answered()
        call.mark_completed(duration=60.0)
        
        assert call.status == CallStatus.COMPLETED
        assert call.duration_seconds == 60.0
        assert call.ended_at is not None
        assert not call.is_active
    
    def test_mark_failed(self):
        """Test marking a call as failed."""
        call = Call(
            call_control_id="test_id",
            to_number="+1234567890",
            from_number="+0987654321",
        )
        
        call.mark_failed("Connection error")
        
        assert call.status == CallStatus.FAILED
        assert call.error_message == "Connection error"
        assert not call.is_active
    
    def test_to_dict(self):
        """Test converting call to dictionary."""
        call = Call(
            call_control_id="test_id",
            to_number="+1234567890",
            from_number="+0987654321",
        )
        
        data = call.to_dict()
        
        assert data["call_control_id"] == "test_id"
        assert data["to_number"] == "+1234567890"
        assert data["status"] == "pending"


class TestTranscriptionResult:
    """Tests for TranscriptionResult dataclass."""
    
    def test_success_factory(self):
        """Test creating a successful result."""
        result = TranscriptionResult.success(
            filename="test.mp3",
            text="Hello world",
            duration=5.0,
            language="en",
        )
        
        assert result.is_success
        assert result.filename == "test.mp3"
        assert result.text == "Hello world"
        assert result.duration_seconds == 5.0
        assert result.language == "en"
        assert result.status == TranscriptionStatus.COMPLETED
    
    def test_failure_factory(self):
        """Test creating a failed result."""
        result = TranscriptionResult.failure(
            filename="test.mp3",
            error="File not found",
        )
        
        assert not result.is_success
        assert result.filename == "test.mp3"
        assert result.error_message == "File not found"
        assert result.status == TranscriptionStatus.FAILED
    
    def test_to_row(self):
        """Test converting result to row."""
        result = TranscriptionResult.success(
            filename="test.mp3",
            text="Hello",
            duration=5.0,
            language="en",
        )
        
        row = result.to_row()
        
        assert row[0] == "test.mp3"
        assert row[1] == "Hello"
        assert row[2] == "5.0"
        assert row[3] == "en"


class TestCallTranscriptionResult:
    """Tests for CallTranscriptionResult dataclass."""
    
    def test_creation(self):
        """Test creating a call transcription result."""
        result = CallTranscriptionResult(
            from_number="+1234567890",
            to_number="+0987654321",
            transcription="Test transcription",
            duration_seconds=120.5,
        )
        
        assert result.from_number == "+1234567890"
        assert result.to_number == "+0987654321"
        assert result.transcription == "Test transcription"
        assert result.duration_seconds == 120.5
    
    def test_to_row(self):
        """Test converting to row."""
        result = CallTranscriptionResult(
            from_number="+1234567890",
            to_number="+0987654321",
            transcription="Hello",
            duration_seconds=60.0,
        )
        
        row = result.to_row()
        
        assert row == ["+1234567890", "+0987654321", "Hello", "60.00"]
    
    def test_header(self):
        """Test header generation."""
        header = CallTranscriptionResult.header()
        
        assert len(header) == 4
        assert "From Number" in header
        assert "To Number" in header
