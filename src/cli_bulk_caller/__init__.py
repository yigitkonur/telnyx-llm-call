"""
Telnyx Transcribe - Automated call-and-transcribe solution.

A robust Python toolkit that leverages Telnyx API for call management
and OpenAI Whisper for transcription services.
"""

__version__ = "2.0.0"
__author__ = "Yiğit Konur"

from cli_bulk_caller.config import Settings
from cli_bulk_caller.models import Call, CallStatus, TranscriptionResult

__all__ = [
    "Settings",
    "Call",
    "CallStatus",
    "TranscriptionResult",
    "__version__",
]
