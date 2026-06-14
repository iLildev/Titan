import click
from rich.console import Console
from titan.cli.commands.init import init
from titan.cli.commands.run import run
from titan.cli.commands.add import add
from titan.cli.commands.list import list_tools

console = Console()

@click.group()
@click.version_option("0.1.0", prog_name="titan")
def cli():
    """
    Titan — The package manager for Telegram bots.

    \b
    Build, extend, and share Telegram bots with a single tool.
    Community tools at: https://github.com/WaheedFox/titan-registry
    """

cli.add_command(init)
cli.add_command(run)
cli.add_command(add)
cli.add_command(list_tools, name="list")
