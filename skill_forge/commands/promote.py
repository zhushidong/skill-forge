"""promote command: manually promote Skill status."""
from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from .. import config, storage
from ..models import now_iso
from ._promote import (
    append_version_record,
    move_skill_file,
    resolve_skill_file,
    validate_manual_promote,
    write_back_skill,
)

console = Console()


def promote(
    skill: str = typer.Option(..., "--skill", "-s", help="skill id or file path"),
    to: str = typer.Option(..., "--to", "-t", help="target status: draft|trained|tested|mature|retired"),
):
    """Manually promote Skill status."""
    if not storage.workspace_initialized():
        console.print("[red]Workspace not initialized. Run: skill-forge init[/red]")
        raise typer.Exit(1)

    skill_file = resolve_skill_file(skill)
    if not skill_file:
        console.print(f"[red]Skill not found: {skill}[/red]")
        console.print("You can:")
        console.print("  1. Use full file path")
        console.print("  2. Run skill-forge distill/melt first")
        raise typer.Exit(1)

    fm, body = storage.read_markdown(skill_file)
    skill_id = fm.get("id", skill_file.stem)
    current_status = fm.get("status", "draft")

    ok, reason = validate_manual_promote(current_status, to)
    if not ok:
        console.print(f"[red]Promotion failed: {reason}[/red]")
        raise typer.Exit(1)

    fm["status"] = to
    new_body = append_version_record(
        body, f"Manual promotion: {current_status} -> {to} ({now_iso()})"
    )

    write_back_skill(skill_file, fm, new_body, update_timestamp=True)
    new_path = move_skill_file(skill_file, to)

    console.print("[bold green]Skill promoted:[/bold green]")
    console.print(f"  Skill: {fm.get('name', skill_id)} ({skill_id})")
    console.print(f"  Status: {current_status} -> {to}")
    if new_path != skill_file:
        console.print(f"  Path: {skill_file}")
        console.print(f"       -> {new_path}")
    else:
        console.print(f"  Path: {new_path}")
