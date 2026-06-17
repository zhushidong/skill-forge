"""Distill command: convert material to Skill draft.

Uses unified schema from validation.py.
"""
from __future__ import annotations
from pathlib import Path

from ..config import SKILLS_DIR, MATERIAL_DIR
from ..storage import write_markdown, read_markdown, find_by_id, timestamp_id
from ..templates import render_template
from ..llm import run_llm


def distill_command(material: str, problem: str, title: str = "") -> str:
    """Distill a material into a Skill draft."""
    # Find the material
    material_path = None
    if Path(material).exists():
        material_path = Path(material)
    else:
        # Try to find by ID
        for subdir in MATERIAL_DIR.iterdir():
            if subdir.is_dir():
                found = find_by_id(subdir, material)
                if found:
                    material_path = found
                    break

    if not material_path or not material_path.exists():
        return (
            f"找不到 material：{material}\n\n"
            "你可以：\n"
            "1. 使用文件路径\n"
            "2. 先运行 skill-forge ingest 导入资料"
        )

    fm, body = read_markdown(material_path)
    mat_title = fm.get("title", material_path.stem)

    # Render distill template
    prompt = render_template("distill.md", {
        "problem": problem,
        "title": title or mat_title,
        "content": body,
    })

    # Run LLM
    result = run_llm(prompt)

    # Save skill draft with unified schema
    skill_id = timestamp_id("skill")
    out_path = SKILLS_DIR / "draft" / f"{skill_id}.md"
    frontmatter = {
        "id": skill_id,
        "name": title or f"从 {mat_title} 提炼",
        "version": "1.0.0",
        "status": "draft",
        "domain": "other",
        "problem": problem,
        "applicable_scenarios": [],
        "not_applicable_scenarios": [],
        "customer_signals": [],
        "strategy": {"name": "", "steps": []},
        "forbidden_behaviors": [],
        "evidence": {
            "source_materials": [fm.get("id", "")],
            "drill_records": [],
            "review_records": [],
        },
        "metrics": {
            "drills": 0,
            "field_tests": 0,
            "wins": 0,
            "losses": 0,
            "avg_score": 0,
            "last_used_at": "",
        },
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }
    write_markdown(out_path, frontmatter, result)

    lines = [
        "提炼完成：",
        f"  - Skill 路径: {out_path}",
        f"  - 来源: {material_path}",
        "",
        "下一步建议：",
        f"  skill-forge drill --skill {skill_id} --persona \"目标客户类型\" --rounds 5",
    ]
    return "\n".join(lines)


def _now_iso() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
