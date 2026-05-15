"""
phase0.cli
----------
CLI entry point for the milestone1 project.
Installed as the `milestone1` command via pyproject.toml [project.scripts].

Commands (Phase 0):
  milestone1 info      — Print project info, stack, and supported fields
  milestone1 doctor    — Run environment health checks

Later phases add sub-commands (ingest-smoke, prefs-parse, prompt-build,
recommend, recommend-run) by importing and registering them here.
"""
from __future__ import annotations

import sys
from typing import Optional

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from milestone1 import __version__
from milestone1.phase0.doctor import Status, run_all_checks, has_failures
from milestone1.phase0.settings import load_settings

app = typer.Typer(
    name="milestone1",
    help="AI-powered restaurant recommendation system (Zomato use case).",
    add_completion=False,
    rich_markup_mode="rich",
)

console = Console()


# ── info ──────────────────────────────────────────────────────────────────

@app.command()
def info() -> None:
    """Print project information, stack decisions, and supported preference fields."""

    settings = load_settings()

    console.print(
        Panel.fit(
            f"[bold]milestone1[/bold]  v{__version__}\n"
            "[dim]AI-powered restaurant recommendation — Zomato use case[/dim]",
            border_style="blue",
        )
    )

    # ── Stack table ────────────────────────────────────────────────────────
    stack = Table(title="Stack", box=box.SIMPLE, show_header=True, header_style="bold cyan")
    stack.add_column("Layer", style="bold")
    stack.add_column("Choice")
    stack.add_column("Notes")

    stack.add_row("Language", "Python 3.11+", "Type hints, match statements")
    stack.add_row("Dependency manager", "pip + pyproject.toml", "setuptools backend")
    stack.add_row("Dataset", "HuggingFace datasets", "ManikaSaini/zomato-restaurant-recommendation")
    stack.add_row("LLM client", "Groq (OpenAI-compatible)", "llama-3.3-70b-versatile by default")
    stack.add_row("Backend (Phase 6)", "FastAPI + uvicorn", "Deployed on Render")
    stack.add_row("Frontend (Phase 7)", "React + Vite", "Deployed on Vercel")
    stack.add_row("Alt deploy (Phase 8)", "Streamlit Community Cloud", "Single-process demo path")
    stack.add_row("Secrets", ".env (local) / env vars (cloud)", "Never committed to git")
    console.print(stack)

    # ── Supported preference fields ────────────────────────────────────────
    fields = Table(
        title="Supported preference fields (v1)",
        box=box.SIMPLE,
        show_header=True,
        header_style="bold cyan",
    )
    fields.add_column("Field", style="bold")
    fields.add_column("Type")
    fields.add_column("Validation")

    fields.add_row("location", "string", "Must match a city in the dataset")
    fields.add_row("budget", "enum", "low | medium | high")
    fields.add_row("cuisines", "list[string]", "One or more cuisine types")
    fields.add_row("min_rating", "float", "0.0 – 5.0 inclusive")
    fields.add_row("additional_preferences", "string (optional)", f"Max {settings.max_free_text_length} chars")
    console.print(fields)

    # ── Product slice + non-goals ─────────────────────────────────────────
    console.print(
        Panel(
            "[bold]Product slice[/bold]\n"
            "The [bold cyan]basic web UI[/bold cyan] (Phase 7: React + Vite) is the sole\n"
            "source of user input and the primary presentation surface for results.\n"
            "All preference fields are collected through the web form.\n"
            "The CLI is for development and diagnostics only.\n\n"
            "[bold]Non-goals for v1 (explicitly deferred)[/bold]\n"
            "• User accounts / authentication\n"
            "• Live Zomato API integration\n"
            "• Maps / geolocation\n"
            "• Restaurant images\n"
            "• Booking / reservation flow\n"
            "• Personalisation across sessions",
            title="Scope",
            border_style="dim",
        )
    )

    # ── Settings summary (no secret values) ───────────────────────────────
    cfg = Table(title="Active configuration", box=box.SIMPLE, header_style="bold cyan")
    cfg.add_column("Setting", style="bold")
    cfg.add_column("Value")

    cfg.add_row("GROQ_API_KEY", "[green]set[/green]" if settings.groq_configured else "[yellow]not set[/yellow]")
    cfg.add_row("HF_TOKEN", "[green]set[/green]" if settings.hf_configured else "[yellow]not set[/yellow]")
    cfg.add_row("load_limit", str(settings.load_limit))
    cfg.add_row("candidate_cap", str(settings.candidate_cap))
    cfg.add_row("groq_model", settings.groq_model)
    console.print(cfg)


# ── doctor ────────────────────────────────────────────────────────────────

@app.command()
def doctor() -> None:
    """Run environment health checks and report any problems."""

    console.print("\n[bold]Running environment checks…[/bold]\n")

    results = run_all_checks()

    STATUS_STYLE = {
        Status.OK:   ("[green]  ✓  [/green]", "green"),
        Status.WARN: ("[yellow]  ⚠  [/yellow]", "yellow"),
        Status.FAIL: ("[red]  ✗  [/red]", "red"),
    }

    for r in results:
        icon, style = STATUS_STYLE[r.status]
        console.print(f"{icon} [bold]{r.name}[/bold]: {r.message}")
        if r.hint:
            console.print(f"       [dim]{r.hint}[/dim]")

    console.print()

    if has_failures(results):
        console.print("[red bold]One or more required checks failed.[/red bold]")
        console.print("Fix the issues above, then run [bold]milestone1 doctor[/bold] again.\n")
        raise typer.Exit(code=1)

    warn_count = sum(1 for r in results if r.status == Status.WARN)
    if warn_count:
        console.print(
            f"[green]All required checks passed[/green] "
            f"[yellow]({warn_count} warning(s) — see above)[/yellow]\n"
        )
    else:
        console.print("[green bold]All checks passed. Environment is ready.[/green bold]\n")


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> None:
    app()


if __name__ == "__main__":
    main()
