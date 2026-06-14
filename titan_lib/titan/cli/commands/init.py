import os
import click
from rich.console import Console
from rich.panel import Panel

console = Console()

STARTER = '''\
from titan.bot import Titan

bot = Titan(token="YOUR_BOT_TOKEN")


@bot.command("start")
async def start(ctx):
    await ctx.reply("Hello! I am powered by Titan.")


bot.run()
'''


@click.command()
@click.argument("name")
def init(name: str):
    """Create a new Titan bot project."""

    if os.path.exists(name):
        console.print(f"[red]Error:[/red] Directory '{name}' already exists.")
        raise SystemExit(1)

    os.makedirs(name)

    main_path = os.path.join(name, "main.py")
    with open(main_path, "w") as f:
        f.write(STARTER)

    tools_path = os.path.join(name, "tools")
    os.makedirs(tools_path)

    gitkeep = os.path.join(tools_path, ".gitkeep")
    open(gitkeep, "w").close()

    console.print(Panel(
        f"[bold green]✓[/bold green] Created [bold]{name}/[/bold]\n\n"
        f"  [dim]main.py[/dim]       ← your bot entry point\n"
        f"  [dim]tools/[/dim]        ← community tools go here\n\n"
        f"[bold]Next steps:[/bold]\n"
        f"  1. Add your token to [bold]{name}/main.py[/bold]\n"
        f"  2. [bold]titan run {name}/main.py[/bold]",
        title="[bold cyan]titan init[/bold cyan]",
        border_style="cyan",
    ))
