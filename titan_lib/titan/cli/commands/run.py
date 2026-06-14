import subprocess
import sys
import click
from rich.console import Console
from rich.rule import Rule

console = Console()


@click.command()
@click.argument("file", default="main.py")
@click.option("--debug", is_flag=True, help="Enable debug output.")
def run(file: str, debug: bool):
    """Run a Titan bot. Restarts automatically on crash."""

    if not file.endswith(".py"):
        console.print("[red]Error:[/red] File must be a Python file (.py)")
        raise SystemExit(1)

    console.print(Rule(f"[bold cyan]titan run[/bold cyan] [dim]{file}[/dim]"))

    env_flags = ["--debug"] if debug else []

    while True:
        try:
            result = subprocess.run(
                [sys.executable, file] + env_flags,
                check=False,
            )

            if result.returncode == 0:
                console.print("\n[dim]Bot exited cleanly.[/dim]")
                break

            console.print(
                f"\n[yellow]⚠ Bot crashed (exit {result.returncode}). "
                f"Restarting...[/yellow]\n"
            )

        except KeyboardInterrupt:
            console.print("\n[bold red]Stopped.[/bold red]")
            break
