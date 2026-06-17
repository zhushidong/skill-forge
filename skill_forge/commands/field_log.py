"""field-log command: record field tests, update skill metrics and trigger promotion."""
from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from .. import config, storage
from ..models import now_iso
from ._promote import (
    apply_result_to_metrics,
    promote_skill_after_metric_change,
    resolve_skill_file,
)

console = Console()


def field_log(
    skill: str = typer.Option(..., "--skill", "-s", help="associated skill id or file path"),
    result: str = typer.Option(..., "--result", "-r", help="result: 成交|推进|搁置|失败"),
    file: str = typer.Option(None, "--file", "-f", help="field record file path"),
    note: str = typer.Option("", "--note", "-n", help="note text"),
    customer_type: str = typer.Option("", "--customer-type", "-c", help="customer type"),
    scene: str = typer.Option("", "--scene", help="scene"),
):
    """Record field test, auto-update skill metrics and check promotion."""
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

    sfm, _ = storage.read_markdown(skill_file)
    skill_id = sfm.get("id", skill)
    skill_name = sfm.get("name", skill_id)

    # Read field record body
    record_body = ""
    if file:
        fpath = Path(file)
        if not fpath.exists():
            console.print(f"[red]Record file not found: {file}[/red]")
            raise typer.Exit(1)
        try:
            record_body = fpath.read_text(encoding="utf-8")
        except OSError as e:
            console.print(f"[red]Failed to read record: {e}[/red]")
            raise typer.Exit(1)
    elif note:
        record_body = note
    else:
        record_body = "(No record provided, counting only)"

    # Generate field-log file
    log_id = storage.timestamp_id("field-log")
    out_path = config.DATA_DIR / "field_logs" / f"{log_id}.md"

    fm = {
        "id": log_id,
        "type": "field_log",
        "skill_id": skill_id,
        "result": result,
        "customer_type": customer_type,
        "scene": scene,
        "source_path": str(file) if file else "",
        "created_at": now_iso(),
    }

    body_parts = [
        f"# Field Log: {skill_name}",
        "",
        f"- Skill: `{skill_id}`",
        f"- Result: {result}",
    ]
    if customer_type:
        body_parts.append(f"- Customer type: {customer_type}")
    if scene:
        body_parts.append(f"- Scene: {scene}")
    body_parts.extend(["", "## Record", "", record_body])

    storage.write_markdown(out_path, fm, "\n".join(body_parts))

    console.print("[bold green]Field log created:[/bold green]")
    console.print(f"  Path: {out_path}")
    console.print(f"  Skill: {skill_name} ({skill_id})")
    console.print(f"  Result: {result}")

    # Writeback skill metrics and check promotion
    _writeback_skill_metrics(skill_file, result, skill_id)


def _writeback_skill_metrics(skill_file: Path, result: str, skill_id: str) -> None:
    """Writeback skill metrics after field log."""
    latest_fm, latest_body = storage.read_markdown(skill_file)
    old_status = latest_fm.get("status", "draft")
    old_metrics = latest_fm.get("metrics") or {}
    new_metrics, side = apply_result_to_metrics(old_metrics, result)
    latest_fm["metrics"] = new_metrics
    new_path, new_status = promote_skill_after_metric_change(
        skill_file, latest_fm, latest_body
    )
    console.print(
        f"[dim]metrics: field_tests {old_metrics.get('field_tests', 0)} -> "
        f"{new_metrics.get('field_tests', 0)}, "
        f"wins {old_metrics.get('wins', 0)} -> {new_metrics.get('wins', 0)}, "
        f"losses {old_metrics.get('losses', 0)} -> {new_metrics.get('losses', 0)}[/dim]"
    )
    if new_status:
        console.print(
            f"[bold magenta]Skill {skill_id} promoted: {old_status} -> {new_status}[/bold magenta]"
        )
        console.print(f"[dim]New path: {new_path}[/dim]")
