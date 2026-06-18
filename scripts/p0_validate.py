#!/usr/bin/env python3
"""P0 validation script: verify workspace, templates, and schema health."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from skill_forge import config, template_content
from skill_forge.storage import ensure_templates, list_markdown_files, read_markdown
from skill_forge.validation import validate_front_matter


def main() -> int:
    errors: list[str] = []

    # 1. Workspace directories
    for d in config.ALL_DIRS:
        p = config.ROOT_DIR / d
        if not p.exists():
            errors.append(f"Missing directory: {d}")

    # 2. Required templates
    required_templates = [
        "distill.md",
        "melt.md",
        "drill.md",
        "review.md",
        "recommend.md",
        "apply_review.md",
        "propose_update.md",
    ]
    for name in required_templates:
        if name not in template_content.TEMPLATES:
            errors.append(f"Missing template: {name}")
        else:
            content = template_content.TEMPLATES[name]
            for placeholder in ("{{", "{%"):
                if placeholder in content:
                    # basic Jinja-style placeholder presence
                    break

    # 3. Schema placeholders in distill template
    distill = template_content.TEMPLATES.get("distill.md", "")
    for keyword in ("applicable_scenarios", "customer_signals", "forbidden_behaviors"):
        if keyword not in distill:
            errors.append(f"distill.md missing new schema keyword: {keyword}")

    # 4. Validate all skill files
    if config.SKILLS_DIR.exists():
        for skill_file in list_markdown_files(config.SKILLS_DIR):
            try:
                fm, _ = read_markdown(skill_file)
                ok, msgs = validate_front_matter(fm, "skills")
                if not ok:
                    errors.append(f"Schema error in {skill_file}: {msgs}")
            except Exception as exc:
                errors.append(f"Failed to read {skill_file}: {exc}")

    # 5. Validate all material files
    if config.MATERIAL_DIR.exists():
        for subdir in config.MATERIAL_DIR.iterdir():
            if subdir.is_dir():
                for mat_file in list_markdown_files(subdir):
                    try:
                        fm, _ = read_markdown(mat_file)
                        ok, msgs = validate_front_matter(fm, "materials")
                        if not ok:
                            errors.append(f"Schema error in {mat_file}: {msgs}")
                    except Exception as exc:
                        errors.append(f"Failed to read {mat_file}: {exc}")

    if errors:
        print("P0 validation FAILED:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("P0 validation PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
