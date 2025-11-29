"""
Telnyx Webhook Handlers.

Processes incoming webhook events from Telnyx for call management.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from flask import Blueprint, request, jsonify

from telnyx_transcribe.exceptions import WebhookError
from telnyx_transcribe.models import CallTranscriptionResult

if TYPE_CHECKING:
    from telnyx_transcribe.services import CallService, TranscriptionService, OutputService

logger = logging.getLogger(__name__)


class WebhookHandler:
    """
    Handler for Telnyx webhook events.
    
    Processes call events and triggers appropriate actions
    like playback, recording, and transcription.
    
    Attributes:
        call_service: Service for managing calls.
        transcription_service: Service for transcribing recordings.
        output_service: Service for writing results.
    """
    
    def __init__(
        self,
        call_service: CallService,
        transcription_service: TranscriptionService,
        output_service: OutputService,
    ) -> None:
        """
        Initialize the webhook handler.
        
        Args:
            call_service: Service for managing calls.
            transcription_service: Service for transcriptions.
            output_service: Service for writing results.
        """
        self.call_service = call_service
        self.transcription_service = transcription_service
        self.output_service = output_service
        
        logger.info("WebhookHandler initialized")
    
    def handle_event(self, payload: dict) -> dict:
        """
        Handle an incoming webhook event.
        
        Args:
            payload: The webhook payload from Telnyx.
            
        Returns:
            Response dictionary.
        """
        try:
            data = payload.get("data", {})
            event_type = data.get("event_type", "")
            event_payload = data.get("payload", {})
            
            logger.info(f"Received webhook event: {event_type}")
            
            handlers = {
                "call.initiated": self._handle_call_initiated,
                "call.answered": self._handle_call_answered,
                "call.hangup": self._handle_call_hangup,
                "call.recording.saved": self._handle_recording_saved,
            }
            
            handler = handlers.get(event_type)
            if handler:
                return handler(event_payload)
            else:
                logger.debug(f"Unhandled event type: {event_type}")
                return {"status": "ignored", "event_type": event_type}
                
        except Exception as e:
            logger.error(f"Error handling webhook: {e}")
            raise WebhookError(f"Failed to process webhook: {e}")
    
    def _handle_call_initiated(self, payload: dict) -> dict:
        """Handle call.initiated event."""
        call_control_id = payload.get("call_control_id")
        logger.info(f"Call initiated: {call_control_id}")
        return {"status": "ok", "event": "call.initiated"}
    
    def _handle_call_answered(self, payload: dict) -> dict:
        """Handle call.answered event - start playback and recording."""
        call_control_id = payload.get("call_control_id")
        
        if not call_control_id:
            logger.warning("No call_control_id in call.answered event")
            return {"status": "error", "message": "Missing call_control_id"}
        
        try:
            self.call_service.handle_call_answered(call_control_id)
            logger.info(f"Started playback and recording for call: {call_control_id}")
            return {"status": "ok", "event": "call.answered"}
        except Exception as e:
            logger.error(f"Error handling call.answered: {e}")
            return {"status": "error", "message": str(e)}
    
    def _handle_call_hangup(self, payload: dict) -> dict:
        """Handle call.hangup event."""
        call_control_id = payload.get("call_control_id")
        duration = payload.get("duration_seconds")
        
        if call_control_id:
            call = self.call_service.handle_call_hangup(call_control_id, duration)
            logger.info(f"Call hung up: {call_control_id}, duration: {duration}s")
        
        return {"status": "ok", "event": "call.hangup"}
    
    def _handle_recording_saved(self, payload: dict) -> dict:
        """Handle call.recording.saved event - download and transcribe."""
        call_control_id = payload.get("call_control_id")
        recording_urls = payload.get("public_recording_urls", {})
        recording_url = recording_urls.get("mp3") or recording_urls.get("wav")
        
        if not call_control_id or not recording_url:
            logger.warning("Missing call_control_id or recording_url in recording.saved event")
            return {"status": "error", "message": "Missing required fields"}
        
        call = self.call_service.get_call(call_control_id)
        if not call:
            logger.warning(f"Call not found for recording: {call_control_id}")
            return {"status": "error", "message": "Call not found"}
        
        # Set recording URL
        self.call_service.set_recording_url(call_control_id, recording_url)
        
        try:
            # Transcribe the recording
            logger.info(f"Transcribing recording for call: {call_control_id}")
            result = self.transcription_service.transcribe_url(
                recording_url,
                filename=f"call_{call_control_id}.mp3",
            )
            
            if result.is_success:
                # Update call with transcription
                call.mark_transcribed(result.text)
                
                # Write result to output
                call_result = CallTranscriptionResult(
                    from_number=call.from_number,
                    to_number=call.to_number,
                    transcription=result.text,
                    duration_seconds=call.duration_seconds or 0,
                    call_control_id=call_control_id,
                )
                self.output_service.write_call_result(call_result)
                
                logger.info(f"Transcription complete for call: {call_control_id}")
                
                # Remove from active calls
                self.call_service.remove_call(call_control_id)
                
                return {
                    "status": "ok",
                    "event": "recording.transcribed",
                    "transcription_length": len(result.text),
                }
            else:
                logger.error(f"Transcription failed for call {call_control_id}: {result.error_message}")
                return {"status": "error", "message": result.error_message}
                
        except Exception as e:
            logger.error(f"Error transcribing recording: {e}")
            return {"status": "error", "message": str(e)}


def create_webhook_blueprint(handler: WebhookHandler) -> Blueprint:
    """
    Create a Flask blueprint for Telnyx webhooks.
    
    Args:
        handler: The WebhookHandler instance.
        
    Returns:
        Flask Blueprint configured with webhook routes.
    """
    bp = Blueprint("webhooks", __name__, url_prefix="/webhook")
    
    @bp.route("", methods=["POST"])
    @bp.route("/", methods=["POST"])
    def webhook():
        """Main webhook endpoint for Telnyx events."""
        if not request.is_json:
            return jsonify({"error": "Expected JSON"}), 400
        
        payload = request.get_json()
        result = handler.handle_event(payload)
        return jsonify(result), 200
    
    @bp.route("/call-recording-saved", methods=["POST"])
    def recording_saved():
        """Dedicated endpoint for recording saved events."""
        if not request.is_json:
            return jsonify({"error": "Expected JSON"}), 400
        
        payload = request.get_json()
        # Wrap in expected format if needed
        if "data" not in payload:
            payload = {"data": {"event_type": "call.recording.saved", "payload": payload}}
        
        result = handler.handle_event(payload)
        return jsonify(result), 200
    
    @bp.route("/health", methods=["GET"])
    def health():
        """Health check endpoint."""
        return jsonify({"status": "healthy"}), 200
    
    return bp
