print("Testing VS Code...")
from rich.console import Console
from rich.prompt import Prompt

console = Console()
console.print("[bold green]✅ Rich library works![/bold green]")
console.print("[bold cyan]FinalAI Pro is ready![/bold cyan]")

name = Prompt.ask("What's your name?")
console.print(f"[yellow]Hello {name}![/yellow]")