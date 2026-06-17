"""apply-review command: apply review findings to create new Skill version."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

import typer
from rich.console import Console

from .. import config, storage, templates, llm
from ..models import now_iso

console = Console()

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


def _bump_version(old_version: str) -> str:
    """Bump minor version, reset patch."""
    if not old_version:
        return "0.2.0"
    parts = old_version.split(".")
    if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
        major = parts[0]
        minor = str(int(parts[1]) + 1)
        if len(parts) >= 3:
            return f"{major}.{minor}.0"
        return f"{major}.{minor}"
    return old_version + ".1"


def _resolve_file(base_dir: Path, target: str) -> Path | None:
    """Find by path or ID."""
    p = Path(target)
    if p.exists() and p.is_file():
        return p
    return storage.find_by_id(base_dir, target)


def _strip_frontmatter(text: str) -> str:
    """Strip frontmatter from LLM output."""
    m = _FM_RE.match(text.strip())
    if m:
        return m.group(2).strip()
    return text.strip()


def _backup_then_write(skill_file: Path, fm: dict, body: str, old_id: str) -> None:
    """Backup then write with integrity verification."""
    backup_dir = config.DATA_DIR / "imports"
    backup_dir.mkdir(parents=True, exist_ok=True)
    ts = now_iso().replace(":", "").replace("-", "").replace("T", "")
    backup_path = backup_dir / f"{old_id}_backup_{ts}.md"

    try:
        shutil.copy2(skill_file, backup_path)
    except OSError as e:
        console.print(f"[red]Backup failed: {e}[/red]")
        console.print("[red]Aborted. Old file unchanged.[/red]")
        raise typer.Exit(1)

    if not backup_path.exists() or backup_path.stat().st_size == 0:
        console.print(f"[red]Backup verification failed: {backup_path}[/red]")
        console.print("[red]Aborted. Old file unchanged.[/red]")
        raise typer.Exit(1)

    console.print(f"[dim]Backed up to: {backup_path}[/dim]")

    try:
        storage.write_markdown(skill_file, fm, body)
    except OSError as e:
        console.print(f"[red]Write failed: {e}[/red]")
        console.print("[yellow]Restoring from backup...[/yellow]")
        try:
            shutil.copy2(backup_path, skill_file)
            console.print(f"[green]Restored from backup[/green]")
        except OSError as ee:
            console.print(f"[red]Restore failed: {ee}[/red]")
            console.print(f"[red]Please manually restore from {backup_path}[/red]")
        raise typer.Exit(1)


def apply_review(
    review: str = typer.Option(..., "--review", "-r", help="review id or file path"),
    skill: str = typer.Option(..., "--skill", "-s", help="skill id or file path"),
    note: str = typer.Option("", "--note", "-n", help="update note"),
):
    """Apply review findings to create new Skill version."""
    if not storage.workspace_initialized():
        console.print("[red]Workspace not initialized. Run: skill-forge init[/red]")
        raise typer.Exit(1)

    review_file = _resolve_file(config.DATA_DIR / "reviews", review)
    if not review_file:
        console.print(f"[red]Review not found: {review}[/red]")
        console.print("You can:")
        console.print("  1. Use full file path")
        console.print("  2. Run skill-forge review first")
        raise typer.Exit(1)

    skill_file = _resolve_file(config.DATA_DIR / "skills", skill)
    if not skill_file:
        console.print(f"[red]Skill not found: {skill}[/red]")
        console.print("You can:")
        console.print("  1. Use full file path")
        console.print("  2. Run skill-forge distill first")
        raise typer.Exit(1)

    review_fm, review_body = storage.read_markdown(review_file)
    skill_fm, skill_body = storage.read_markdown(skill_file)

    skill_name = skill_fm.get("name", skill_file.stem)
    old_version = skill_fm.get("version", "0.1.0")
    old_id = skill_fm.get("id", skill_file.stem)
    review_id = review_fm.get("id", review_file.stem)

    prompt = templates.render_template("apply_review.md", {
        "skill_name": skill_name,
        "skill_body": skill_body,
        "review_body": review_body,
        "note": note or "(no note)",
    })

    console.print("[dim]Applying review to Skill...[/dim]")
    new_body = llm.run_llm(prompt)
    new_body = _strip_frontmatter(new_body)

    new_id = storage.timestamp_id("skill")
    new_version = _bump_version(old_version)
    now = now_iso()

    # Inherit metrics from old version
    old_metrics = skill_fm.get("metrics") or {
        "drills": 0, "field_tests": 0, "wins": 0, "losses": 0
    }
    inherited_metrics = {
        "drills": int(old_metrics.get("drills", 0) or 0),
        "field_tests": int(old_metrics.get("field_tests", 0) or 0),
        "wins": int(old_metrics.get("wins", 0) or 0),
        "losses": int(old_metrics.get("losses", 0) or 0),
    }

    new_fm = {
        "id": new_id,
        "name": skill_fm.get("name", skill_name),
        "version": new_version,
        "status": "draft",
        "source_ids": skill_fm.get("source_ids", []),
        "source_type": skill_fm.get("source_type", "material"),
        "scenes": skill_fm.get("scenes", []),
        "customer_stages": skill_fm.get("customer_stages", []),
        "customer_types": skill_fm.get("customer_types", []),
        "signals": skill_fm.get("signals", []),
        "avoid_when": skill_fm.get("avoid_when", []),
        "metrics": inherited_metrics,
        "inherited_metrics": True,
        "supersedes": old_id,
        "created_at": now,
        "updated_at": now,
    }

    version_log = (
        "\n\n## 版本记录\n\n"
        f"- v{old_version} -> v{new_version}\n"
        f"- Based on review: {review_id}\n"
        f"- Note: {note or '(none)'}\n"
        f"- Time: {now}\n"
        f"- Inherited metrics: drills={inherited_metrics['drills']}, "
        f"field_tests={inherited_metrics['field_tests']}, "
        f"wins={inherited_metrics['wins']}, "
        f"losses={inherited_metrics['losses']}\n"
    )
    new_body_with_log = new_body.rstrip() + version_log

    new_path = storage.skill_path_by_status("draft", new_id)
    storage.write_markdown(new_path, new_fm, new_body_with_log)

    skill_fm["superseded_by"] = new_id
    skill_fm["updated_at"] = now
    _backup_then_write(skill_file, skill_fm, skill_body, old_id)

    console.print("[bold green]Skill updated to new version:[/bold green]")
    console.print(f"  New ID: {new_id}")
    console.print(f"  Version: v{old_version} -> v{new_version}")
    console.print(f"  Path: {new_path}")
    console.print(f"  Metrics inherited: drills={inherited_metrics['drills']}, wins={inherited_metrics['wins']}, losses={inherited_metrics['losses']}")
    console.print(f"  Old {old_id} marked superseded_by: {new_id}")

    if not llm.has_api_key():
        console.print("[yellow]No API Key detected. Full prompt generated.[/yellow]")
        console.print("Copy the prompt from the new Skill file to any LLM, then manually replace the body.")
