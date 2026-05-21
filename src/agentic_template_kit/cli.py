from __future__ import annotations

import difflib
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .bake import build_initial_config, dump_bake_file, load_bake_file, resolve_target
from .lockfile import load_lockfile, managed_files_by_path, sha256_text, write_lockfile
from .models import parse_platforms
from .renderer import render_files
from .validator import validate_project

app = typer.Typer(help="Generate agentic DevSecOps SDLC templates for multiple agent platforms.")
console = Console()

MAX_DIFF_LINES_PER_FILE = 120


def _unified_diff(old: str, new: str, path: str, *, max_lines: int | None = None) -> str:
    diff_lines = list(
        difflib.unified_diff(
            old.splitlines(),
            new.splitlines(),
            fromfile=f"a/{path}",
            tofile=f"b/{path}",
            lineterm="",
        )
    )
    if max_lines is not None and len(diff_lines) > max_lines:
        trimmed = diff_lines[:max_lines]
        trimmed.append("... (diff truncated)")
        diff_lines = trimmed
    return "\n".join(diff_lines)


@app.command()
def init(
    target: Path = typer.Option(Path("."), "--target", "-t", help="Target repository path."),
    platform: Optional[str] = typer.Option(
        None,
        "--platform",
        help='Comma-separated platforms, e.g. "gitlab-duo,codex,github-copilot".',
    ),
    preset: Optional[str] = typer.Option(None, "--preset", help="Preset: minimal, gitlab, enterprise, local-ai, all."),
    project_name: Optional[str] = typer.Option(None, "--project-name", help="Project name used in rendered templates."),
    owner_team: str = typer.Option("platform-engineering", "--owner-team", help="Owning team."),
    language: str = typer.Option("de", "--language", help="Default documentation language."),
    governance_level: str = typer.Option("standard", "--governance-level", help="relaxed, standard, strict."),
    force: bool = typer.Option(False, "--force", help="Overwrite existing agentic.bake.yaml."),
) -> None:
    target = target.resolve()
    target.mkdir(parents=True, exist_ok=True)
    bake_path = target / "agentic.bake.yaml"

    if bake_path.exists() and not force:
        raise typer.BadParameter(f"{bake_path} already exists. Use --force to overwrite.")

    platforms = parse_platforms(platform)
    if project_name is None:
        project_name = target.name

    config = build_initial_config(
        platforms=platforms,
        project_name=project_name,
        owner_team=owner_team,
        language=language,
        governance_level=governance_level,
        preset=preset,
    )
    dump_bake_file(config, bake_path)
    console.print(f"[green]Created[/green] {bake_path}")


@app.command("list-targets")
def list_targets(target: Path = typer.Option(Path("."), "--target", "-t", help="Target repository path.")) -> None:
    config = load_bake_file(target / "agentic.bake.yaml")
    table = Table(title="Agentic Bake Targets")
    table.add_column("Target")
    table.add_column("Description")
    table.add_column("Platforms / Inherits")

    for name, cfg in config.targets.items():
        value = ", ".join(cfg.platforms or cfg.inherits)
        table.add_row(name, cfg.description, value)

    console.print(table)


@app.command()
def bake(
    name: str = typer.Argument("default", help="Target name from agentic.bake.yaml."),
    target: Path = typer.Option(Path("."), "--target", "-t", help="Target repository path."),
    plan: bool = typer.Option(False, "--plan", help="Show generated files without writing."),
    detailed_diff: bool = typer.Option(
        False,
        "--detailed-diff",
        help="Show full unified diffs in --plan (no truncation).",
    ),
    write: bool = typer.Option(False, "--write", help="Write files to target repository."),
) -> None:
    if not plan and not write:
        plan = True

    target = target.resolve()
    config = load_bake_file(target / "agentic.bake.yaml")
    resolved = resolve_target(config, name)
    files = render_files(config, resolved)
    lockfile = load_lockfile(target)
    state_files = managed_files_by_path(lockfile)
    planned_files = {str(rendered.destination): rendered for rendered in files}

    table = Table(title=f"Bake target: {name}")
    table.add_column("Action")
    table.add_column("Platform")
    table.add_column("Path")

    for rendered in files:
        path = target / rendered.destination
        action = "create"
        if path.exists():
            existing = path.read_text(encoding="utf-8")
            action = "unchanged" if existing == rendered.content else "update"
        table.add_row(action, rendered.platform, str(rendered.destination))

    console.print(table)

    state_table = Table(title="State Plan (.agentic-template.lock)")
    state_table.add_column("Action")
    state_table.add_column("Platform")
    state_table.add_column("Path")
    state_counts = {"create": 0, "update": 0, "delete": 0, "noop": 0}

    for path, rendered in planned_files.items():
        checksum = sha256_text(rendered.content)
        previous = state_files.get(path)
        if previous is None:
            action = "create"
        elif previous.get("checksum") == checksum:
            action = "noop"
        else:
            action = "update"
        state_counts[action] += 1
        state_table.add_row(action, rendered.platform, path)

    for path, previous in state_files.items():
        if path in planned_files:
            continue
        state_counts["delete"] += 1
        state_table.add_row("delete", str(previous.get("platform", "-")), path)

    console.print(state_table)
    console.print(
        "Plan summary: "
        f"{state_counts['create']} to create, "
        f"{state_counts['update']} to update, "
        f"{state_counts['delete']} to delete, "
        f"{state_counts['noop']} unchanged in state."
    )

    if plan:
        changed_paths: list[str] = []
        for path, rendered in planned_files.items():
            candidate = target / path
            if not candidate.exists():
                continue
            if candidate.read_text(encoding="utf-8") != rendered.content:
                changed_paths.append(path)

        for path in changed_paths:
            rendered = planned_files[path]
            current_text = (target / path).read_text(encoding="utf-8")
            max_lines = None if detailed_diff else MAX_DIFF_LINES_PER_FILE
            diff_text = _unified_diff(
                current_text,
                rendered.content,
                path,
                max_lines=max_lines,
            )
            if diff_text:
                console.print(f"\n[bold]Diff:[/bold] {path}")
                console.print(diff_text)

        deleted_paths = [path for path in state_files if path not in planned_files]
        if deleted_paths:
            console.print(
                "\n[bold]State-only files (would be removed from state if applied):[/bold]"
            )
            for path in deleted_paths:
                console.print(f"- {path}")

        console.print("\n[yellow]Dry run only. Use --write to write files.[/yellow]")
        return

    for rendered in files:
        path = target / rendered.destination
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered.content, encoding="utf-8")

    write_lockfile(target, files, name)
    console.print(f"[green]Wrote {len(files)} files and .agentic-template.lock[/green]")


@app.command()
def validate(target: Path = typer.Option(Path("."), "--target", "-t", help="Target repository path.")) -> None:
    errors = validate_project(target.resolve())
    if errors:
        for error in errors:
            console.print(f"[red]ERROR[/red] {error}")
        raise typer.Exit(1)

    console.print("[green]Validation passed[/green]")


if __name__ == "__main__":
    app()
