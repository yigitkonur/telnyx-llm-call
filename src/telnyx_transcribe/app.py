"""
Flask Application Factory.

Creates and configures the Flask application for webhook handling.
"""

from __future__ import annotations

import logging
from typing import Optional

from flask import Flask

from telnyx_transcribe.config import Settings
from telnyx_transcribe.services import CallService, TranscriptionService, OutputService
from telnyx_transcribe.webhooks import create_webhook_blueprint, WebhookHandler

logger = logging.getLogger(__name__)


def create_app(settings: Optional[Settings] = None) -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        settings: Optional settings instance. If not provided,
                 settings will be loaded from environment.
                 
    Returns:
        Configured Flask application.
    """
    from telnyx_transcribe.config import get_settings
    
    if settings is None:
        settings = get_settings()
    
    # Validate settings
    errors = settings.validate()
    if errors:
        logger.warning(f"Configuration warnings: {errors}")
    
    # Create Flask app
    app = Flask(__name__)
    app.config["SETTINGS"] = settings
    
    # Initialize services
    call_service = CallService(settings)
    transcription_service = TranscriptionService(settings)
    output_service = OutputService(settings.output_file)
    
    # Store services on app for access in views
    app.config["CALL_SERVICE"] = call_service
    app.config["TRANSCRIPTION_SERVICE"] = transcription_service
    app.config["OUTPUT_SERVICE"] = output_service
    
    # Create webhook handler
    webhook_handler = WebhookHandler(
        call_service=call_service,
        transcription_service=transcription_service,
        output_service=output_service,
    )
    
    # Register webhooks blueprint
    webhook_bp = create_webhook_blueprint(webhook_handler)
    app.register_blueprint(webhook_bp)
    
    # Root health check
    @app.route("/")
    def root():
        return {"status": "ok", "service": "telnyx-transcribe"}, 200
    
    @app.route("/health")
    def health():
        return {
            "status": "healthy",
            "active_calls": len(call_service.get_all_active_calls()),
        }, 200
    
    logger.info("Flask application created")
    return app


class Application:
    """
    Main application class for Telnyx Transcribe.
    
    Coordinates all services and provides a high-level API
    for call-and-transcribe operations.
    """
    
    def __init__(self, settings: Optional[Settings] = None) -> None:
        """
        Initialize the application.
        
        Args:
            settings: Optional settings instance.
        """
        from telnyx_transcribe.config import get_settings
        
        self.settings = settings or get_settings()
        self.call_service = CallService(self.settings)
        self.transcription_service = TranscriptionService(self.settings)
        self.output_service = OutputService(self.settings.output_file)
        
        logger.info("Application initialized")
    
    def start_calls(self, numbers: list[str]) -> list:
        """
        Start calls to a list of numbers.
        
        Args:
            numbers: List of phone numbers to call.
            
        Returns:
            List of initiated Call objects.
        """
        return self.call_service.initiate_calls_batch(numbers)
    
    def transcribe_directory(self, directory: str) -> list:
        """
        Transcribe all audio files in a directory.
        
        Args:
            directory: Path to directory containing audio files.
            
        Returns:
            List of TranscriptionResult objects.
        """
        from pathlib import Path
        
        results = self.transcription_service.transcribe_directory(Path(directory))
        
        # Write results to output
        for result in results:
            if result.is_success:
                self.output_service.write_transcription_result(result)
        
        return results
    
    def run_server(self) -> None:
        """Run the Flask webhook server."""
        app = create_app(self.settings)
        app.run(
            host=self.settings.webhook_host,
            port=self.settings.webhook_port,
            debug=False,
        )
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self.transcription_service.close()
        self.output_service.finalize()
        logger.info("Application cleanup complete")
