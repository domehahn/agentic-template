from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from agentic_template_kit import __version__
from agentic_template_kit.bake import DEFAULT_BAKE_FILE, load_bake_file, write_default_bake_file
from agentic_template_kit.lockfile import load_lock_file, update_lock, write_lock_file
from agentic_template_kit.models import PlannedChange
from agentic_template_kit.renderer import apply_files, plan_changes, render_files
from agentic_template_kit.validator import validate_target

app = typer.Typer(
    name="agentic-template",
    help="Bake-style generator for agentic assistant instructions and skills.",
    no_args_is_help=True,
)
console = Console()


def version_callback(value: bool) -> None:
    if value:
        console.print(f"agentic-template-kit {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option("--version", callback=version_callback, is_eager=True, help="Show version."),
    ] = False,
) -> None:
    _ = version


@app.command()
def init(
    target: Annotated[Path, typer.Option("--target", "-t", help="Target repository path.")] = Path("."),
    overwrite: Annotated[bool, typer.Option("--overwrite", help="Overwrite existing bake file.")] = False,
) -> None:
    """Create a starter agentic.bake.yaml in a target repository."""
    target = target.resolve()
    target.mkdir(parents=True, exist_ok=True)
    bake_file = write_default_bake_file(target, overwrite=overwrite)
    console.print(f"[green]Initialized[/green] {bake_file}")


@app.command("list-targets")
def list_targets(
    file: Annotated[
        Path | None,
        typer.Option("--file", "-f", help="Bake file path. Defaults to <target>/agentic.bake.yaml."),
    ] = None,
    target: Annotated[Path, typer.Option("--target", "-t", help="Target repository path.")] = Path("."),
) -> None:
    """List targets from a bake file."""
    bake_path = file or (target / DEFAULT_BAKE_FILE)
    bake = load_bake_file(bake_path)

    table = Table(title=f"Targets in {bake_path}")
    table.add_column("Target")
    table.add_column("Description")
    table.add_column("Platforms")
    table.add_column("Inherits")

    for name, cfg in sorted(bake.targets.items()):
        table.add_row(
            name,
            cfg.description or "",
            ", ".join(cfg.platforms),
            ", ".join(cfg.inherits),
        )
    console.print(table)


@app.command()
def bake(
    target_name: Annotated[str, typer.Argument(help="Bake target name.")],
    target: Annotated[Path, typer.Option("--target", "-t", help="Target repository path.")] = Path("."),
    file: Annotated[
        Path | None,
        typer.Option("--file", "-f", help="Bake file path. Defaults to <target>/agentic.bake.yaml."),
    ] = None,
    write: Annotated[bool, typer.Option("--write", help="Write files. Without this, dry-run only.")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Preview only.")] = False,
    force: Annotated[bool, typer.Option("--force", help="Overwrite unmanaged/conflicting files.")] = False,
) -> None:
    """Render a target from agentic.bake.yaml."""
    target = target.resolve()
    bake_path = file or (target / DEFAULT_BAKE_FILE)
    bake_file = load_bake_file(bake_path)
    resolved = bake_file.resolve_target(target_name)

    lock = load_lock_file(target)
    managed_checksums = {entry.path: entry.checksum for entry in lock.managed_files}

    rendered = render_files(target, resolved, target_name)
    changes = plan_changes(target, rendered, managed_checksums, force=force)

    print_plan(changes, target)

    has_conflict = any(change.action == "conflict" for change in changes)
    if has_conflict and write:
        console.print("[red]Conflicts detected. Resolve them or use --force.[/red]")
        raise typer.Exit(code=2)

    if dry_run or not write:
        console.print("[yellow]Dry-run only. Re-run with --write to apply.[/yellow]")
        return

    apply_files(target, rendered, changes)
    lock = update_lock(lock, target_name, rendered)
    write_lock_file(target, lock)
    console.print("[green]Applied successfully.[/green]")


@app.command()
def diff(
    target_name: Annotated[str, typer.Argument(help="Bake target name.")],
    target: Annotated[Path, typer.Option("--target", "-t", help="Target repository path.")] = Path("."),
    file: Annotated[Path | None, typer.Option("--file", "-f", help="Bake file path.")] = None,
) -> None:
    """Show planned file-level changes for a target."""
    bake(target_name=target_name, target=target, file=file, write=False, dry_run=True, force=False)


@app.command()
def validate(
    target: Annotated[Path, typer.Option("--target", "-t", help="Target repository path.")] = Path("."),
) -> None:
    """Validate generated agentic files in a target repository."""
    target = target.resolve()
    issues = validate_target(target)
    if not issues:
        console.print("[green]Validation passed.[/green]")
        return
    console.print("[red]Validation failed.[/red]")
    for issue in issues:
        console.print(f"- {issue}")
    raise typer.Exit(code=1)


def print_plan(changes: list[PlannedChange], target: Path) -> None:
    table = Table(title=f"Planned changes for {target}")
    table.add_column("Action")
    table.add_column("Path")
    table.add_column("Reason")

    color_by_action = {
        "create": "green",
        "update": "yellow",
        "conflict": "red",
        "skip": "dim",
        "unchanged": "dim",
    }

    for change in changes:
        color = color_by_action.get(change.action, "white")
        table.add_row(
            f"[{color}]{change.action}[/{color}]",
            change.destination.as_posix(),
            change.reason or "",
        )
    console.print(table)
