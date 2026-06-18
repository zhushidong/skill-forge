from __future__ import annotations
from pathlib import Path

from ..config import SKILLS_DIR
from ..storage import write_markdown, timestamp_id, extract_frontmatter
from ..parsers import parse_external_file
from ..adapters import to_text
from ..templates import render_template
from ..llm import run_llm


def _default_skill_fm(skill_id: str, name: str, source_path: str) -> dict:
    """Build default skill frontmatter with unified schema."""
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    return {
        "id": skill_id,
        "name": name,
        "version": "1.0.0",
        "status": "draft",
        "domain": "other",
        "category": "",
        "problem": "",
        "goal": "",
        "applicable_scenarios": [],
        "not_applicable_scenarios": [],
        "customer_stages": [],
        "customer_types": [],
        "customer_signals": [],
        "strategy": {"name": "", "steps": []},
        "forbidden_behaviors": [],
        "steps": [],
        "example_lines": [],
        "drill_personas": [],
        "evidence": {
            "source_materials": [source_path] if source_path else [],
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
        "created_at": now,
        "updated_at": now,
    }


def _merge_llm_frontmatter(default_fm: dict, llm_fm: dict) -> dict:
    """Merge LLM-extracted frontmatter into default, preferring LLM values."""
    merged = dict(default_fm)
    override_fields = {
        "name", "version", "domain", "category", "problem", "goal",
        "applicable_scenarios", "not_applicable_scenarios",
        "customer_stages", "customer_types", "customer_signals",
        "strategy", "forbidden_behaviors",
        "steps", "example_lines", "drill_personas",
    }
    for key in override_fields:
        if key in llm_fm and llm_fm[key]:
            merged[key] = llm_fm[key]
    return merged


def melt_command(
    file: str,
    asset_type: str = "auto",
    problem: str = "",
    target_scene: str = "",
    title: str = "",
) -> str:
    """Melt an external asset into Skill draft(s)."""
    path = Path(file)
    try:
        parsed = parse_external_file(path, asset_type)
    except (ValueError, FileNotFoundError, OSError) as e:
        return f"文件读取失败: {e}"

    # Convert to unified text
    unified_text = to_text(parsed)

    # Render melt template
    prompt = render_template("melt.md", {
        "asset_type": parsed.get("asset_type", parsed["type"]),
        "problem": problem or "（未指定，由 LLM 判断）",
        "context": target_scene or "（未指定，由 LLM 判断）",
        "content": unified_text,
    })

    # Run LLM
    result = run_llm(prompt)

    # Try to extract frontmatter from LLM output
    llm_fm, llm_body = extract_frontmatter(result)

    # Save result
    melt_id = timestamp_id("skill")
    out_path = SKILLS_DIR / "draft" / f"{melt_id}.md"
    default_fm = _default_skill_fm(
        melt_id,
        title or f"从 {parsed['title']} 熔炼",
        path.name,
    )
    frontmatter = _merge_llm_frontmatter(default_fm, llm_fm)
    # Mark source type as external
    frontmatter["evidence"]["source_materials"].append(path.name)

    write_markdown(out_path, frontmatter, llm_body)

    lines = [
        "熔炼完成：",
        f"  - 路径: {out_path}",
        f"  - 来源类型: {parsed['type']}",
        "",
        "下一步建议：",
        f'  skill-forge drill --skill {melt_id} --persona "目标客户类型" --rounds 5',
    ]
    return "\n".join(lines)
