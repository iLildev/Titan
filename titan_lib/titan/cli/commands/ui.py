import json
from pathlib import Path

import click
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import (
    Header,
    Footer,
    DataTable,
    Static,
    Label,
)
from textual.containers import Vertical, Horizontal
from textual.screen import Screen

_BUNDLED = Path(__file__).parent.parent.parent / "registry" / "index.json"

BANNER = """\
 ████████╗██╗████████╗ █████╗ ███╗   ██╗
    ██╔══╝██║╚══██╔══╝██╔══██╗████╗  ██║
    ██║   ██║   ██║   ███████║██╔██╗ ██║
    ██║   ██║   ██║   ██╔══██║██║╚██╗██║
    ██║   ██║   ██║   ██║  ██║██║ ╚████║
    ╚═╝   ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝\
"""


def _load_tools() -> list[dict]:
    try:
        return json.loads(_BUNDLED.read_text()).get("tools", [])
    except Exception:
        return []


class ToolsScreen(Screen):
    BINDINGS = [
        Binding("q", "app.pop_screen", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        table = DataTable()
        table.add_columns("Name", "Type", "Author", "Version", "Description")
        for tool in _load_tools():
            table.add_row(
                tool.get("name", ""),
                tool.get("type", ""),
                tool.get("author", ""),
                tool.get("version", ""),
                tool.get("description", ""),
            )
        yield table
        yield Footer()


class HomeScreen(Screen):
    BINDINGS = [
        Binding("t", "push_screen('tools')", "Tools"),
        Binding("q", "app.exit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="home"):
            yield Static(BANNER, id="banner")
            yield Label(
                "The package manager for Telegram bots.\n"
                "github.com/WaheedFox/titan",
                id="tagline",
            )
            with Horizontal(id="shortcuts"):
                yield Static(
                    "[bold cyan]T[/bold cyan]  Browse tools\n"
                    "[bold cyan]Q[/bold cyan]  Quit",
                    id="keys",
                )
                yield Static(
                    "[dim]titan init <name>[/dim]\n"
                    "[dim]titan run  <file>[/dim]\n"
                    "[dim]titan add  <tool>[/dim]\n"
                    "[dim]titan list[/dim]",
                    id="cmds",
                )
        yield Footer()


class TitanApp(App):
    CSS = """
    Screen { background: #0d0d0d; }

    #home {
        align: center middle;
        height: 100%;
        padding: 2 4;
    }

    #banner {
        color: #00aaff;
        text-align: center;
        padding-bottom: 1;
    }

    #tagline {
        color: #888888;
        text-align: center;
        padding-bottom: 2;
    }

    #shortcuts {
        width: auto;
        align: center middle;
        gap: 6;
    }

    #keys { color: #ffffff; }
    #cmds { color: #555555; }

    DataTable {
        height: 1fr;
    }
    """

    SCREENS = {"tools": ToolsScreen}

    def on_mount(self) -> None:
        self.push_screen(HomeScreen())


@click.command()
def ui():
    """Launch the Titan interactive terminal UI."""
    TitanApp().run()
