"""
Console utilities for Telnyx Transcribe.

Provides rich terminal output with progress bars and formatted tables.
"""

from __future__ import annotations

from typing import Any, Optional

from rich.console import Console as RichConsole
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.theme import Theme


# Custom theme for consistent styling
THEME = Theme({
    "info": "cyan",
    "success": "green",
    "warning": "yellow",
    "error": "red bold",
    "highlight": "magenta",
})


class Console:
    """
    Rich console wrapper for beautiful terminal output.
    
    Provides consistent styling and helper methods for
    common output patterns.
    """
    
    def __init__(self) -> None:
        """Initialize the console with custom theme."""
        self._console = RichConsole(theme=THEME)
    
    def print(self, *args: Any, **kwargs: Any) -> None:
        """Print to the console."""
        self._console.print(*args, **kwargs)
    
    def info(self, message: str) -> None:
        """Print an info message."""
        self._console.print(f"[info]ℹ[/info] {message}")
    
    def success(self, message: str) -> None:
        """Print a success message."""
        self._console.print(f"[success]✓[/success] {message}")
    
    def warning(self, message: str) -> None:
        """Print a warning message."""
        self._console.print(f"[warning]⚠[/warning] {message}")
    
    def error(self, message: str) -> None:
        """Print an error message."""
        self._console.print(f"[error]✗[/error] {message}")
    
    def header(self, title: str, subtitle: Optional[str] = None) -> None:
        """Print a styled header."""
        content = f"[bold]{title}[/bold]"
        if subtitle:
            content += f"\n[dim]{subtitle}[/dim]"
        self._console.print(Panel(content, expand=False))
    
    def table(
        self,
        data: list[list[str]],
        headers: list[str],
        title: Optional[str] = None,
    ) -> None:
        """
        Print a formatted table.
        
        Args:
            data: List of rows (each row is a list of strings).
            headers: Column headers.
            title: Optional table title.
        """
        table = Table(title=title, show_header=True, header_style="bold magenta")
        
        for header in headers:
            table.add_column(header)
        
        for row in data:
            table.add_row(*[str(cell) for cell in row])
        
        self._console.print(table)
    
    def results_table(
        self,
        results: list[dict],
        title: str = "Results",
    ) -> None:
        """
        Print a results table from a list of dictionaries.
        
        Args:
            results: List of result dictionaries.
            title: Table title.
        """
        if not results:
            self.warning("No results to display")
            return
        
        headers = list(results[0].keys())
        data = [[str(r.get(h, "")) for h in headers] for r in results]
        self.table(data, headers, title)
    
    def status(self, message: str):
        """Create a status context for long-running operations."""
        return self._console.status(f"[bold green]{message}[/bold green]")
    
    @property
    def raw(self) -> RichConsole:
        """Access the underlying Rich console."""
        return self._console


def create_progress_bar(
    description: str = "Processing",
    total: Optional[int] = None,
) -> Progress:
    """
    Create a rich progress bar.
    
    Args:
        description: Description text for the progress bar.
        total: Total number of items (None for indeterminate).
        
    Returns:
        Configured Progress instance.
    """
    columns = [
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        TaskProgressColumn(),
        TextColumn("•"),
        TimeElapsedColumn(),
        TextColumn("•"),
        TimeRemainingColumn(),
    ]
    
    return Progress(*columns)


def print_banner() -> None:
    """Print the application banner."""
    console = Console()
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ████████╗███████╗██╗     ███╗   ██╗██╗   ██╗██╗  ██╗      ║
║   ╚══██╔══╝██╔════╝██║     ████╗  ██║╚██╗ ██╔╝╚██╗██╔╝      ║
║      ██║   █████╗  ██║     ██╔██╗ ██║ ╚████╔╝  ╚███╔╝       ║
║      ██║   ██╔══╝  ██║     ██║╚██╗██║  ╚██╔╝   ██╔██╗       ║
║      ██║   ███████╗███████╗██║ ╚████║   ██║   ██╔╝ ██╗      ║
║      ╚═╝   ╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝      ║
║                                                              ║
║              TRANSCRIBE • Call & Transcribe                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    console.print(f"[bold cyan]{banner}[/bold cyan]")
