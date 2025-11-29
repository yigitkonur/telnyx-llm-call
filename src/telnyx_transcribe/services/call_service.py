"""
Telnyx Call Service.

Handles all call-related operations using the Telnyx API.
"""

from __future__ import annotations

import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Iterator, Optional

import telnyx

from telnyx_transcribe.config import Settings
from telnyx_transcribe.exceptions import CallError, TelnyxAPIError
from telnyx_transcribe.models import Call, CallStatus

logger = logging.getLogger(__name__)


class CallService:
    """
    Service for managing Telnyx calls.
    
    Provides methods for initiating calls, managing recordings,
    and tracking active calls.
    
    Attributes:
        settings: Application settings.
        active_calls: Dictionary of active calls keyed by call_control_id.
    """
    
    def __init__(self, settings: Settings) -> None:
        """
        Initialize the call service.
        
        Args:
            settings: Application settings with Telnyx credentials.
        """
        self.settings = settings
        self.active_calls: dict[str, Call] = {}
        self._lock = threading.Lock()
        
        # Configure Telnyx API
        telnyx.api_key = settings.telnyx_api_key
        
        logger.info("CallService initialized")
    
    def initiate_call(self, to_number: str) -> Call:
        """
        Initiate a call to the specified number.
        
        Args:
            to_number: The destination phone number (E.164 format).
            
        Returns:
            Call object representing the initiated call.
            
        Raises:
            CallError: If the call cannot be initiated.
            TelnyxAPIError: If the Telnyx API returns an error.
        """
        try:
            logger.info(f"Initiating call to {to_number}")
            
            telnyx_call = telnyx.Call.create(
                connection_id=self.settings.telnyx_connection_id,
                to=to_number,
                from_=self.settings.telnyx_from_number,
            )
            
            call = Call(
                call_control_id=telnyx_call.call_control_id,
                to_number=to_number,
                from_number=self.settings.telnyx_from_number,
                status=CallStatus.INITIATED,
            )
            
            with self._lock:
                self.active_calls[call.call_control_id] = call
            
            logger.info(f"Call initiated: {call.call_control_id}")
            return call
            
        except telnyx.error.TelnyxError as e:
            error_msg = f"Failed to initiate call to {to_number}: {e}"
            logger.error(error_msg)
            raise TelnyxAPIError(error_msg, api_error=str(e))
        except Exception as e:
            error_msg = f"Unexpected error initiating call to {to_number}: {e}"
            logger.error(error_msg)
            raise CallError(error_msg, phone_number=to_number)
    
    def start_playback(self, call_control_id: str) -> None:
        """
        Start audio playback on an active call.
        
        Args:
            call_control_id: The call control ID.
            
        Raises:
            CallError: If the call is not found or playback fails.
        """
        call = self.get_call(call_control_id)
        if not call:
            raise CallError(f"Call not found: {call_control_id}", call_control_id=call_control_id)
        
        try:
            logger.info(f"Starting playback on call {call_control_id}")
            
            telnyx_call = telnyx.Call()
            telnyx_call.call_control_id = call_control_id
            telnyx_call.playback_start(audio_url=self.settings.audio_url)
            
            logger.info(f"Playback started on call {call_control_id}")
            
        except telnyx.error.TelnyxError as e:
            error_msg = f"Failed to start playback: {e}"
            logger.error(error_msg)
            raise TelnyxAPIError(error_msg, api_error=str(e))
    
    def start_recording(self, call_control_id: str) -> None:
        """
        Start recording an active call.
        
        Args:
            call_control_id: The call control ID.
            
        Raises:
            CallError: If the call is not found or recording fails.
        """
        call = self.get_call(call_control_id)
        if not call:
            raise CallError(f"Call not found: {call_control_id}", call_control_id=call_control_id)
        
        try:
            logger.info(f"Starting recording on call {call_control_id}")
            
            telnyx_call = telnyx.Call()
            telnyx_call.call_control_id = call_control_id
            telnyx_call.record_start(
                format=self.settings.recording_format,
                channels=self.settings.recording_channels,
            )
            
            call.mark_recording()
            logger.info(f"Recording started on call {call_control_id}")
            
        except telnyx.error.TelnyxError as e:
            error_msg = f"Failed to start recording: {e}"
            logger.error(error_msg)
            raise TelnyxAPIError(error_msg, api_error=str(e))
    
    def handle_call_answered(self, call_control_id: str) -> None:
        """
        Handle a call being answered.
        
        Starts playback and recording automatically.
        
        Args:
            call_control_id: The call control ID.
        """
        call = self.get_call(call_control_id)
        if call:
            call.mark_answered()
            
        # Start playback and recording
        self.start_playback(call_control_id)
        self.start_recording(call_control_id)
    
    def handle_call_hangup(
        self,
        call_control_id: str,
        duration: Optional[float] = None,
    ) -> Optional[Call]:
        """
        Handle a call being hung up.
        
        Args:
            call_control_id: The call control ID.
            duration: Optional call duration in seconds.
            
        Returns:
            The completed Call object, or None if not found.
        """
        call = self.get_call(call_control_id)
        if call:
            call.mark_completed(duration)
            logger.info(f"Call completed: {call_control_id}, duration: {call.duration_seconds}s")
        return call
    
    def set_recording_url(self, call_control_id: str, recording_url: str) -> Optional[Call]:
        """
        Set the recording URL for a completed call.
        
        Args:
            call_control_id: The call control ID.
            recording_url: URL to the recording file.
            
        Returns:
            The updated Call object, or None if not found.
        """
        call = self.get_call(call_control_id)
        if call:
            call.recording_url = recording_url
            logger.info(f"Recording URL set for call {call_control_id}")
        return call
    
    def remove_call(self, call_control_id: str) -> Optional[Call]:
        """
        Remove a call from the active calls dictionary.
        
        Args:
            call_control_id: The call control ID.
            
        Returns:
            The removed Call object, or None if not found.
        """
        with self._lock:
            return self.active_calls.pop(call_control_id, None)
    
    def get_call(self, call_control_id: str) -> Optional[Call]:
        """
        Get a call by its control ID.
        
        Args:
            call_control_id: The call control ID.
            
        Returns:
            The Call object, or None if not found.
        """
        with self._lock:
            return self.active_calls.get(call_control_id)
    
    def get_all_active_calls(self) -> list[Call]:
        """
        Get all active calls.
        
        Returns:
            List of all active Call objects.
        """
        with self._lock:
            return list(self.active_calls.values())
    
    def initiate_calls_batch(
        self,
        numbers: list[str],
        on_call_initiated: Optional[Callable[[Call], None]] = None,
        on_call_failed: Optional[Callable[[str, Exception], None]] = None,
    ) -> list[Call]:
        """
        Initiate calls to multiple numbers using thread pool.
        
        Args:
            numbers: List of phone numbers to call.
            on_call_initiated: Optional callback when a call is initiated.
            on_call_failed: Optional callback when a call fails.
            
        Returns:
            List of successfully initiated Call objects.
        """
        initiated_calls: list[Call] = []
        
        def process_number(number: str) -> Optional[Call]:
            try:
                call = self.initiate_call(number)
                if on_call_initiated:
                    on_call_initiated(call)
                return call
            except Exception as e:
                logger.error(f"Failed to initiate call to {number}: {e}")
                if on_call_failed:
                    on_call_failed(number, e)
                return None
        
        with ThreadPoolExecutor(max_workers=self.settings.max_workers) as executor:
            futures = {executor.submit(process_number, num): num for num in numbers}
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    initiated_calls.append(result)
        
        logger.info(f"Initiated {len(initiated_calls)}/{len(numbers)} calls successfully")
        return initiated_calls


def load_numbers_from_file(filepath: str) -> list[str]:
    """
    Load phone numbers from a text file.
    
    Args:
        filepath: Path to the file containing one number per line.
        
    Returns:
        List of phone numbers.
    """
    with open(filepath) as f:
        numbers = [line.strip() for line in f if line.strip()]
    
    logger.info(f"Loaded {len(numbers)} numbers from {filepath}")
    return numbers
