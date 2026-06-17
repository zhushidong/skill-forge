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

    # Save skill draft
    skill_id = timestamp_id("skill")
    out_path = SKILLS_DIR / "draft" / f"{skill_id}.md"
    frontmatter = {
        "id": skill_id,
        "name": title or f"从 {mat_title} 提炼",
        "version": "0.1.0",
        "status": "draft",
        "source_ids": [fm.get("id", "")],
        "source_type": "material",
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
