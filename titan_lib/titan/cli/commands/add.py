import os
import httpx
import click
from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live

console = Console()

REGISTRY_URL = "https://raw.githubusercontent.com/WaheedFox/titan-registry/main/index.json"


def _fetch_registry() -> dict:
    try:
        response = httpx.get(REGISTRY_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception:
        return {}


def _find_tool(registry: dict, name: str) -> dict | None:
    for tool in registry.get("tools", []):
        if tool["name"] == name:
            return tool
    return None


def _download_tool(repo_url: str, name: str) -> bool:
    raw_url = repo_url.replace(
        "https://github.com/", "https://raw.githubusercontent.com/"
    ) + "/main/main.py"

    try:
        response = httpx.get(raw_url, timeout=15)
        response.raise_for_status()
    except Exception as e:
        console.print(f"[red]Error:[/red] Could not fetch tool: {e}")
        return False

    os.makedirs("tools", exist_ok=True)
    with open(os.path.join("tools", f"{name}.py"), "w") as f:
        f.write(response.text)

    return True


@click.command()
@click.argument("name")
def add(name: str):
    """Install a community tool from the Titan registry or GitHub.

    \b
    Examples:
      titan add welcome-handler
      titan add github:user/repo
    """

    if name.startswith("github:"):
        slug = name[len("github:"):]
        tool_name = slug.split("/")[-1]
        with Live(Spinner("dots", text=f"Installing from GitHub: {slug}"), console=console):
            success = _download_tool(f"https://github.com/{slug}", tool_name)
        if success:
            console.print(f"[green]✓[/green] Installed [bold]{tool_name}[/bold] → tools/{tool_name}.py")
        return

    with Live(Spinner("dots", text="Fetching registry..."), console=console):
        registry = _fetch_registry()

    if not registry:
        console.print("[red]Error:[/red] Could not reach the Titan registry.")
        console.print("[dim]Try: titan add github:<user>/<repo>[/dim]")
        raise SystemExit(1)

    tool = _find_tool(registry, name)

    if not tool:
        console.print(f"[red]Error:[/red] Tool '[bold]{name}[/bold]' not found in registry.")
        console.print("[dim]Run [bold]titan list[/bold] to see available tools.[/dim]")
        raise SystemExit(1)

    with Live(Spinner("dots", text=f"Installing {name}..."), console=console):
        success = _download_tool(tool["repo"], name)

    if success:
        console.print(
            f"[green]✓[/green] Installed [bold]{name}[/bold] v{tool['version']} "
            f"by [dim]{tool['author']}[/dim]\n"
            f"  → tools/{name}.py"
        )
