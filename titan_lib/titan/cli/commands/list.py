import json
import httpx
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.spinner import Spinner
from rich.live import Live

console = Console()

REGISTRY_URL = "https://raw.githubusercontent.com/WaheedFox/titan-registry/main/index.json"
_BUNDLED_REGISTRY = Path(__file__).parent.parent.parent / "registry" / "index.json"


def _load_registry() -> dict:
    try:
        response = httpx.get(REGISTRY_URL, timeout=8)
        response.raise_for_status()
        return response.json()
    except Exception:
        pass

    try:
        return json.loads(_BUNDLED_REGISTRY.read_text())
    except Exception:
        return {}


@click.command()
@click.option("--type", "kind", default=None, help="Filter by type: handler, filter, util.")
def list_tools(kind: str | None):
    """List all available tools in the Titan registry."""

    with Live(Spinner("dots", text="Fetching registry..."), console=console):
        registry = _load_registry()

    tools = registry.get("tools", [])

    if kind:
        tools = [t for t in tools if t.get("type") == kind]

    if not tools:
        console.print("[yellow]No tools found.[/yellow]")
        return

    table = Table(show_header=True, header_style="bold cyan", border_style="dim", expand=False)
    table.add_column("Name", style="bold white", no_wrap=True)
    table.add_column("Type", style="cyan", no_wrap=True)
    table.add_column("Author", style="dim", no_wrap=True)
    table.add_column("Version", style="dim", no_wrap=True, justify="right")
    table.add_column("Description", style="white")

    for tool in tools:
        table.add_row(
            tool.get("name", ""),
            tool.get("type", ""),
            tool.get("author", ""),
            tool.get("version", ""),
            tool.get("description", ""),
        )

    console.print(f"\n[bold cyan]Titan Registry[/bold cyan] [dim]— {len(tools)} tool(s)[/dim]\n")
    console.print(table)
    console.print(
        f"\n[dim]Install a tool: [bold]titan add <name>[/bold][/dim]\n"
        f"[dim]Submit your tool: {registry.get('registry', '')}[/dim]\n"
    )
