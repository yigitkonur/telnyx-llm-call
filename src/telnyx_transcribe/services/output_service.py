"""
Output Service.

Handles writing transcription results to various output formats.
"""

from __future__ import annotations

import csv
import json
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from telnyx_transcribe.models import CallTranscriptionResult, TranscriptionResult

logger = logging.getLogger(__name__)


class OutputService:
    """
    Service for writing transcription results to files.
    
    Supports TSV, CSV, and JSON output formats with thread-safe operations.
    
    Attributes:
        output_path: Path to the output file.
        format: Output format ('tsv', 'csv', or 'json').
    """
    
    def __init__(
        self,
        output_path: Union[str, Path],
        format: str = "tsv",
        write_header: bool = True,
    ) -> None:
        """
        Initialize the output service.
        
        Args:
            output_path: Path for the output file.
            format: Output format ('tsv', 'csv', or 'json').
            write_header: Whether to write header row for TSV/CSV.
        """
        self.output_path = Path(output_path)
        self.format = format.lower()
        self._lock = threading.Lock()
        self._initialized = False
        self._write_header = write_header
        
        if self.format not in ("tsv", "csv", "json"):
            raise ValueError(f"Unsupported output format: {format}")
        
        logger.info(f"OutputService initialized: {self.output_path} ({self.format})")
    
    def _ensure_initialized(self, header: Optional[list[str]] = None) -> None:
        """Ensure the output file is initialized with header if needed."""
        if self._initialized:
            return
        
        # Create parent directories if needed
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.format in ("tsv", "csv") and self._write_header and header:
            delimiter = "\t" if self.format == "tsv" else ","
            with open(self.output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=delimiter)
                writer.writerow(header)
        elif self.format == "json":
            # Initialize JSON file with empty array
            with open(self.output_path, "w", encoding="utf-8") as f:
                f.write("[\n")
        
        self._initialized = True
    
    def write_call_result(self, result: CallTranscriptionResult) -> None:
        """
        Write a call transcription result.
        
        Args:
            result: The call transcription result to write.
        """
        with self._lock:
            self._ensure_initialized(CallTranscriptionResult.header())
            self._write_row(result.to_row())
        
        logger.debug(f"Wrote call result: {result.to_number}")
    
    def write_transcription_result(self, result: TranscriptionResult) -> None:
        """
        Write a standalone transcription result.
        
        Args:
            result: The transcription result to write.
        """
        header = ["Filename", "Transcription", "Duration (seconds)", "Language"]
        
        with self._lock:
            self._ensure_initialized(header)
            self._write_row(result.to_row())
        
        logger.debug(f"Wrote transcription result: {result.filename}")
    
    def write_results_batch(
        self,
        results: list[Union[CallTranscriptionResult, TranscriptionResult]],
    ) -> None:
        """
        Write multiple results in a batch.
        
        Args:
            results: List of results to write.
        """
        if not results:
            return
        
        # Determine header based on first result type
        if isinstance(results[0], CallTranscriptionResult):
            header = CallTranscriptionResult.header()
        else:
            header = ["Filename", "Transcription", "Duration (seconds)", "Language"]
        
        with self._lock:
            self._ensure_initialized(header)
            for result in results:
                self._write_row(result.to_row())
        
        logger.info(f"Wrote {len(results)} results to {self.output_path}")
    
    def _write_row(self, row: list[str]) -> None:
        """Write a single row to the output file."""
        if self.format in ("tsv", "csv"):
            delimiter = "\t" if self.format == "tsv" else ","
            with open(self.output_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=delimiter)
                writer.writerow(row)
        elif self.format == "json":
            # For JSON, we need to handle the array format
            # Read, append, write back (not ideal for large files)
            data = {"row": row, "timestamp": datetime.now().isoformat()}
            with open(self.output_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(data) + ",\n")
    
    def finalize(self) -> None:
        """Finalize the output file (close JSON array, etc.)."""
        if self.format == "json" and self._initialized:
            with self._lock:
                # Read current content and fix JSON array
                with open(self.output_path, "rb+") as f:
                    f.seek(-2, 2)  # Go back 2 bytes from end
                    f.truncate()
                    f.write(b"\n]")
        
        logger.info(f"Output finalized: {self.output_path}")
    
    @property
    def exists(self) -> bool:
        """Check if the output file exists."""
        return self.output_path.exists()
    
    def get_stats(self) -> dict:
        """
        Get statistics about the output file.
        
        Returns:
            Dictionary with file statistics.
        """
        if not self.exists:
            return {"exists": False, "rows": 0, "size_bytes": 0}
        
        line_count = 0
        with open(self.output_path, "r", encoding="utf-8") as f:
            line_count = sum(1 for _ in f)
        
        # Subtract header row for TSV/CSV
        if self.format in ("tsv", "csv") and self._write_header:
            line_count = max(0, line_count - 1)
        
        return {
            "exists": True,
            "rows": line_count,
            "size_bytes": self.output_path.stat().st_size,
            "path": str(self.output_path),
        }
