import os
from playwright.sync_api import Page
from rich.console import Console

console = Console()

class EscalationManager:
    @staticmethod
    def request_human_intervention(page: Page, reason: str, context: dict) -> bool:
        console.print("\n[bold yellow]════════════════════════════════════════════════════════════[/bold yellow]")
        console.print("[bold red]⚠ HUMAN OPERATOR INTERVENTION TRIGGERED (HITL)[/bold red]")
        console.print(f"[bold white]Reason:[/bold white] {reason}")
        console.print(f"[bold white]Capability:[/bold white] {context.get('capability_id')} | [bold white]Step ID:[/bold white] {context.get('step_id')}")
        console.print(f"[bold white]Active URL:[/bold white] {page.url}")
        console.print("[dim]The live browser window is paused and interactive. The human operator may now act.[/dim]")
        console.print("[bold yellow]════════════════════════════════════════════════════════════[/bold yellow]\n")

        os.makedirs("evidence/escalations", exist_ok=True)
        screenshot_path = f"evidence/escalations/intervention_{context.get('step_id')}.png"
        try:
            page.screenshot(path=screenshot_path)
            console.print(f"[cyan]Diagnostic screenshot persisted to: {screenshot_path}[/cyan]")
        except Exception:
            pass

        choice = input("Enter 'r' to resume deterministic automation, or 'a' to abort session: ").strip().lower()
        if choice == 'r':
            console.print("[bold green]✔ Live session control reclaimed. Resuming automation...[/bold green]\n")
            return True
        else:
            console.print("[bold red]✖ Operation explicitly aborted by human operator.[/bold red]\n")
            return False