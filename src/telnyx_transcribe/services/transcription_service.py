"""
OpenAI Transcription Service.

Handles all transcription operations using OpenAI's Whisper API.
"""

from __future__ import annotations

import io
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import BinaryIO, Callable, Generator, Optional, Union

import httpx
from openai import OpenAI

from telnyx_transcribe.config import Settings
from telnyx_transcribe.exceptions import RecordingError, TranscriptionError
from telnyx_transcribe.models import TranscriptionResult, TranscriptionStatus

logger = logging.getLogger(__name__)

# Supported audio formats for Whisper
SUPPORTED_AUDIO_FORMATS = frozenset({
    ".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm", ".ogg", ".flac"
})


class TranscriptionService:
    """
    Service for transcribing audio using OpenAI Whisper.
    
    Provides methods for transcribing individual files, URLs,
    and batch processing directories.
    
    Attributes:
        settings: Application settings.
        client: OpenAI client instance.
    """
    
    def __init__(self, settings: Settings) -> None:
        """
        Initialize the transcription service.
        
        Args:
            settings: Application settings with OpenAI credentials.
        """
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key)
        self._http_client = httpx.Client(timeout=60.0)
        
        logger.info("TranscriptionService initialized")
    
    def transcribe_file(
        self,
        filepath: Union[str, Path],
        language: Optional[str] = None,
    ) -> TranscriptionResult:
        """
        Transcribe a local audio file.
        
        Args:
            filepath: Path to the audio file.
            language: Optional language code (e.g., 'en', 'es').
            
        Returns:
            TranscriptionResult with the transcribed text.
            
        Raises:
            TranscriptionError: If transcription fails after all retries.
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            return TranscriptionResult.failure(str(filepath), f"File not found: {filepath}")
        
        if filepath.suffix.lower() not in SUPPORTED_AUDIO_FORMATS:
            return TranscriptionResult.failure(
                str(filepath),
                f"Unsupported audio format: {filepath.suffix}",
            )
        
        logger.info(f"Transcribing file: {filepath}")
        
        for attempt in range(self.settings.max_retries):
            try:
                with open(filepath, "rb") as audio_file:
                    result = self._transcribe_audio_stream(
                        audio_file,
                        filename=filepath.name,
                        language=language,
                    )
                    return TranscriptionResult.success(
                        filename=str(filepath),
                        text=result,
                        language=language,
                    )
                    
            except Exception as e:
                wait_time = self.settings.retry_delay * (2 ** attempt)
                logger.warning(
                    f"Transcription attempt {attempt + 1}/{self.settings.max_retries} "
                    f"failed for {filepath}: {e}. Retrying in {wait_time}s..."
                )
                
                if attempt < self.settings.max_retries - 1:
                    time.sleep(wait_time)
        
        error_msg = f"Transcription failed after {self.settings.max_retries} attempts"
        logger.error(f"{error_msg}: {filepath}")
        return TranscriptionResult.failure(str(filepath), error_msg)
    
    def transcribe_url(
        self,
        url: str,
        filename: Optional[str] = None,
        language: Optional[str] = None,
    ) -> TranscriptionResult:
        """
        Transcribe audio from a URL.
        
        Downloads the audio and transcribes it using Whisper.
        
        Args:
            url: URL of the audio file.
            filename: Optional filename for the result.
            language: Optional language code.
            
        Returns:
            TranscriptionResult with the transcribed text.
            
        Raises:
            RecordingError: If the audio cannot be downloaded.
            TranscriptionError: If transcription fails.
        """
        filename = filename or url.split("/")[-1] or "recording"
        logger.info(f"Transcribing URL: {url}")
        
        for attempt in range(self.settings.max_retries):
            try:
                # Download the audio file
                response = self._http_client.get(url)
                response.raise_for_status()
                
                # Create a file-like object from the response
                audio_data = io.BytesIO(response.content)
                audio_data.name = filename  # OpenAI requires a filename
                
                result = self._transcribe_audio_stream(
                    audio_data,
                    filename=filename,
                    language=language,
                )
                
                return TranscriptionResult.success(
                    filename=filename,
                    text=result,
                    language=language,
                )
                
            except httpx.HTTPError as e:
                error_msg = f"Failed to download audio from {url}: {e}"
                logger.error(error_msg)
                if attempt >= self.settings.max_retries - 1:
                    return TranscriptionResult.failure(filename, error_msg)
                    
            except Exception as e:
                wait_time = self.settings.retry_delay * (2 ** attempt)
                logger.warning(
                    f"Transcription attempt {attempt + 1}/{self.settings.max_retries} "
                    f"failed for {url}: {e}. Retrying in {wait_time}s..."
                )
                
                if attempt < self.settings.max_retries - 1:
                    time.sleep(wait_time)
        
        error_msg = f"Transcription failed after {self.settings.max_retries} attempts"
        logger.error(f"{error_msg}: {url}")
        return TranscriptionResult.failure(filename, error_msg)
    
    def _transcribe_audio_stream(
        self,
        audio_stream: BinaryIO,
        filename: str,
        language: Optional[str] = None,
    ) -> str:
        """
        Transcribe an audio stream using OpenAI Whisper.
        
        Args:
            audio_stream: File-like object containing audio data.
            filename: Name to use for the file.
            language: Optional language code.
            
        Returns:
            Transcribed text.
        """
        # Ensure the stream has a name attribute for OpenAI
        if not hasattr(audio_stream, "name"):
            audio_stream.name = filename
        
        kwargs = {"model": "whisper-1", "file": audio_stream}
        if language:
            kwargs["language"] = language
        
        response = self.client.audio.transcriptions.create(**kwargs)
        return response.text
    
    def transcribe_directory(
        self,
        directory: Union[str, Path],
        language: Optional[str] = None,
        on_complete: Optional[Callable[[TranscriptionResult], None]] = None,
        on_progress: Optional[Callable[[int, int], None]] = None,
    ) -> list[TranscriptionResult]:
        """
        Transcribe all audio files in a directory.
        
        Args:
            directory: Path to the directory containing audio files.
            language: Optional language code for all files.
            on_complete: Callback for each completed transcription.
            on_progress: Callback for progress updates (completed, total).
            
        Returns:
            List of TranscriptionResult objects.
        """
        directory = Path(directory)
        
        if not directory.exists():
            raise TranscriptionError(f"Directory not found: {directory}")
        
        if not directory.is_dir():
            raise TranscriptionError(f"Not a directory: {directory}")
        
        # Find all audio files
        audio_files = list(self._find_audio_files(directory))
        total = len(audio_files)
        
        if total == 0:
            logger.warning(f"No audio files found in {directory}")
            return []
        
        logger.info(f"Found {total} audio files to transcribe in {directory}")
        
        results: list[TranscriptionResult] = []
        completed = 0
        
        def process_file(filepath: Path) -> TranscriptionResult:
            return self.transcribe_file(filepath, language=language)
        
        with ThreadPoolExecutor(max_workers=self.settings.max_workers) as executor:
            futures = {executor.submit(process_file, f): f for f in audio_files}
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                completed += 1
                
                if on_complete:
                    on_complete(result)
                
                if on_progress:
                    on_progress(completed, total)
                
                status = "✓" if result.is_success else "✗"
                logger.info(f"[{completed}/{total}] {status} {result.filename}")
        
        successful = sum(1 for r in results if r.is_success)
        logger.info(f"Transcription complete: {successful}/{total} successful")
        
        return results
    
    def _find_audio_files(self, directory: Path) -> Generator[Path, None, None]:
        """
        Find all supported audio files in a directory.
        
        Args:
            directory: Directory to search.
            
        Yields:
            Paths to audio files.
        """
        for filepath in directory.iterdir():
            if filepath.is_file() and filepath.suffix.lower() in SUPPORTED_AUDIO_FORMATS:
                yield filepath
    
    def close(self) -> None:
        """Clean up resources."""
        self._http_client.close()
    
    def __enter__(self) -> TranscriptionService:
        return self
    
    def __exit__(self, *args) -> None:
        self.close()


def is_audio_file(filepath: Union[str, Path]) -> bool:
    """
    Check if a file is a supported audio format.
    
    Args:
        filepath: Path to check.
        
    Returns:
        True if the file is a supported audio format.
    """
    return Path(filepath).suffix.lower() in SUPPORTED_AUDIO_FORMATS
