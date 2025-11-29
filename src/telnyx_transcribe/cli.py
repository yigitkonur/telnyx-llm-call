"""
Command Line Interface for Telnyx Transcribe.

Provides commands for call management, transcription, and server operations.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from telnyx_transcribe import __version__
from telnyx_transcribe.config import Settings, get_settings
from telnyx_transcribe.exceptions import ConfigurationError
from telnyx_transcribe.utils.console import Console, print_banner, create_progress_bar
from telnyx_transcribe.utils.logging import setup_logging

# Create CLI app
app = typer.Typer(
    name="telnyx-transcribe",
    help="🎙️ Automated call-and-transcribe solution using Telnyx & OpenAI Whisper.",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"telnyx-transcribe version [bold cyan]{__version__}[/bold cyan]")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version", "-v",
            help="Show version and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-V", help="Enable verbose logging."),
    ] = False,
) -> None:
    """
    🎙️ Telnyx Transcribe - Automated Call & Transcription Service.
    
    Make calls, play audio, record, and transcribe automatically using
    Telnyx for telephony and OpenAI Whisper for transcription.
    """
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(level=log_level)


@app.command()
def call(
    numbers_file: Annotated[
        Path,
        typer.Argument(
            help="Path to file containing phone numbers (one per line).",
            exists=True,
            readable=True,
        ),
    ],
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output file for transcriptions."),
    ] = Path("results.tsv"),
    workers: Annotated[
        int,
        typer.Option("--workers", "-w", help="Number of concurrent calls."),
    ] = 5,
    no_server: Annotated[
        bool,
        typer.Option("--no-server", help="Don't start the webhook server."),
    ] = False,
) -> None:
    """
    📞 Make calls to numbers from a file and transcribe recordings.
    
    Reads phone numbers from a file, initiates calls, plays audio,
    records the calls, and transcribes the recordings using Whisper.
    """
    print_banner()
    
    # Load settings
    settings = get_settings()
    settings.output_file = output
    settings.max_workers = workers
    settings.numbers_file = numbers_file
    
    # Validate configuration
    errors = settings.validate()
    if errors:
        console.error("Configuration errors:")
        for error in errors:
            console.print(f"  • {error}")
        console.print("\n[dim]Set required environment variables or create a .env file.[/dim]")
        raise typer.Exit(1)
    
    # Load numbers
    from telnyx_transcribe.services.call_service import load_numbers_from_file
    numbers = load_numbers_from_file(str(numbers_file))
    
    if not numbers:
        console.error("No phone numbers found in file.")
        raise typer.Exit(1)
    
    console.info(f"Loaded [bold]{len(numbers)}[/bold] phone numbers from {numbers_file}")
    console.info(f"Output will be written to [bold]{output}[/bold]")
    
    # Initialize application
    from telnyx_transcribe.app import Application
    application = Application(settings)
    
    # Start calls
    console.info("Starting calls...")
    
    with create_progress_bar() as progress:
        task = progress.add_task("Initiating calls", total=len(numbers))
        
        def on_call_initiated(call):
            progress.advance(task)
        
        def on_call_failed(number, error):
            progress.advance(task)
            console.warning(f"Failed to call {number}: {error}")
        
        calls = application.call_service.initiate_calls_batch(
            numbers,
            on_call_initiated=on_call_initiated,
            on_call_failed=on_call_failed,
        )
    
    console.success(f"Initiated [bold]{len(calls)}[/bold] calls successfully")
    
    if not no_server:
        console.info(f"Starting webhook server on port [bold]{settings.webhook_port}[/bold]...")
        console.print("[dim]Press Ctrl+C to stop the server[/dim]\n")
        
        try:
            application.run_server()
        except KeyboardInterrupt:
            console.print("\n")
            console.info("Shutting down...")
        finally:
            application.cleanup()
    
    console.success("Done!")


@app.command()
def transcribe(
    source: Annotated[
        Path,
        typer.Argument(
            help="Path to audio file or directory containing audio files.",
            exists=True,
        ),
    ],
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output file for transcriptions."),
    ] = Path("transcriptions.tsv"),
    workers: Annotated[
        int,
        typer.Option("--workers", "-w", help="Number of concurrent transcriptions."),
    ] = 3,
    language: Annotated[
        Optional[str],
        typer.Option("--language", "-l", help="Language code (e.g., 'en', 'es')."),
    ] = None,
) -> None:
    """
    🎧 Transcribe audio files using OpenAI Whisper.
    
    Transcribe a single audio file or all audio files in a directory.
    Supports MP3, MP4, WAV, M4A, WEBM, OGG, and FLAC formats.
    """
    print_banner()
    
    # Load settings
    settings = get_settings()
    settings.output_file = output
    settings.max_workers = workers
    
    # Validate for transcription
    errors = settings.validate_for_transcription_only()
    if errors:
        console.error("Configuration errors:")
        for error in errors:
            console.print(f"  • {error}")
        console.print("\n[dim]Set OPENAI_API_KEY environment variable or create a .env file.[/dim]")
        raise typer.Exit(1)
    
    console.info(f"Transcribing [bold]{source}[/bold]")
    console.info(f"Output will be written to [bold]{output}[/bold]")
    
    # Initialize services
    from telnyx_transcribe.services import TranscriptionService, OutputService
    
    transcription_service = TranscriptionService(settings)
    output_service = OutputService(output)
    
    try:
        if source.is_file():
            # Single file transcription
            console.info("Transcribing single file...")
            
            with console.status("Transcribing..."):
                result = transcription_service.transcribe_file(source, language=language)
            
            if result.is_success:
                output_service.write_transcription_result(result)
                console.success(f"Transcription complete: {len(result.text)} characters")
                console.print(f"\n[dim]{result.text[:500]}{'...' if len(result.text) > 500 else ''}[/dim]")
            else:
                console.error(f"Transcription failed: {result.error_message}")
                raise typer.Exit(1)
        else:
            # Directory transcription
            console.info("Scanning directory for audio files...")
            
            results = []
            
            with create_progress_bar() as progress:
                task = progress.add_task("Transcribing", total=None)
                
                def on_complete(result):
                    if result.is_success:
                        output_service.write_transcription_result(result)
                    results.append(result)
                
                def on_progress(completed, total):
                    progress.update(task, total=total, completed=completed)
                
                transcription_service.transcribe_directory(
                    source,
                    language=language,
                    on_complete=on_complete,
                    on_progress=on_progress,
                )
            
            # Print summary
            successful = sum(1 for r in results if r.is_success)
            failed = len(results) - successful
            
            console.print("")
            console.success(f"Transcription complete: [bold]{successful}[/bold] successful, [bold]{failed}[/bold] failed")
            
            # Show results table
            if results:
                table_data = [
                    [
                        Path(r.filename).name[:30],
                        "✓" if r.is_success else "✗",
                        f"{len(r.text)} chars" if r.is_success else r.error_message or "Error",
                    ]
                    for r in results[:10]  # Show first 10
                ]
                console.table(
                    table_data,
                    headers=["File", "Status", "Result"],
                    title="Results Summary",
                )
                
                if len(results) > 10:
                    console.print(f"[dim]... and {len(results) - 10} more files[/dim]")
    
    finally:
        transcription_service.close()
        output_service.finalize()
    
    console.success("Done!")


@app.command()
def server(
    port: Annotated[
        int,
        typer.Option("--port", "-p", help="Port to run the server on."),
    ] = 5000,
    host: Annotated[
        str,
        typer.Option("--host", "-h", help="Host to bind the server to."),
    ] = "0.0.0.0",
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output file for transcriptions."),
    ] = Path("results.tsv"),
) -> None:
    """
    🌐 Start the webhook server to receive Telnyx events.
    
    Runs a Flask server that handles incoming webhook events from Telnyx
    for call management and recording transcription.
    """
    print_banner()
    
    # Load settings
    settings = get_settings()
    settings.webhook_port = port
    settings.webhook_host = host
    settings.output_file = output
    
    # Validate configuration
    errors = settings.validate()
    if errors:
        console.warning("Configuration warnings (some features may not work):")
        for error in errors:
            console.print(f"  • {error}")
        console.print("")
    
    console.info(f"Starting webhook server on [bold]{host}:{port}[/bold]")
    console.info(f"Output will be written to [bold]{output}[/bold]")
    console.print("\n[dim]Press Ctrl+C to stop the server[/dim]\n")
    
    from telnyx_transcribe.app import create_app
    
    flask_app = create_app(settings)
    
    try:
        flask_app.run(host=host, port=port, debug=False)
    except KeyboardInterrupt:
        console.print("\n")
        console.info("Shutting down...")
    
    console.success("Server stopped.")


@app.command()
def validate():
    """
    ✅ Validate your configuration and API keys.
    
    Checks that all required environment variables are set
    and optionally tests API connectivity.
    """
    print_banner()
    
    settings = get_settings()
    
    console.header("Configuration Validation")
    
    # Check all settings
    checks = [
        ("TELNYX_API_KEY", bool(settings.telnyx_api_key)),
        ("TELNYX_CONNECTION_ID", bool(settings.telnyx_connection_id)),
        ("TELNYX_FROM_NUMBER", bool(settings.telnyx_from_number)),
        ("OPENAI_API_KEY", bool(settings.openai_api_key)),
        ("AUDIO_URL", bool(settings.audio_url)),
    ]
    
    all_valid = True
    for name, valid in checks:
        status = "[green]✓[/green]" if valid else "[red]✗[/red]"
        console.print(f"  {status} {name}")
        if not valid:
            all_valid = False
    
    console.print("")
    
    if all_valid:
        console.success("All configuration is valid!")
    else:
        console.warning("Some configuration is missing.")
        console.print("\n[dim]Create a .env file with the missing values:[/dim]")
        console.print("""
```
TELNYX_API_KEY=your_telnyx_api_key
TELNYX_CONNECTION_ID=your_connection_id
TELNYX_FROM_NUMBER=+1234567890
OPENAI_API_KEY=your_openai_api_key
AUDIO_URL=https://example.com/audio.mp3
```
""")
        raise typer.Exit(1)


def run() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    run()
