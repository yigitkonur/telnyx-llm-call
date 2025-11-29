"""
Telnyx Transcribe - Automated call-and-transcribe solution.

A robust Python toolkit that leverages Telnyx API for call management
and OpenAI Whisper for transcription services.
"""

__version__ = "2.0.0"
__author__ = "Yiğit Konur"

from telnyx_transcribe.config import Settings
from telnyx_transcribe.models import Call, CallStatus, TranscriptionResult

__all__ = [
    "Settings",
    "Call",
    "CallStatus",
    "TranscriptionResult",
    "__version__",
]
