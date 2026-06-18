"""propose-update command: generate update proposals based on field data."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime

from ..config import SKILLS_DIR, FIELD_LOGS_DIR, REVIEWS_DIR, PROPOSALS_DIR
from ..storage import write_markdown, read_markdown, timestamp_id, list_markdown_files
from ..skill_manager import find_skill
from ..templates import render_template
from ..llm import run_llm


def _find_related_records(skill_id: str):
    """Find reviews and field logs related to a skill."""
    reviews = []
    field_logs = []

    for md_file in list_markdown_files(REVIEWS_DIR):
        try:
            fm, body = read_markdown(md_file)
            if fm.get("skill_id") == skill_id:
                reviews.append((fm, body))
        except Exception:
            continue

    for md_file in list_markdown_files(FIELD_LOGS_DIR):
        try:
            fm, body = read_markdown(md_file)
            if fm.get("skill_id") == skill_id:
                field_logs.append((fm, body))
        except Exception:
            continue

    return reviews, field_logs


def _summarize_reviews(reviews: list) -> str:
    """Summarize review records for prompt."""
    if not reviews:
        return "（无复盘记录）"
    lines = []
    for fm, body in reviews[:5]:
        lines.append(f"- 结果: {fm.get('result', '未知')}")
        lines.append(f"  评分: {fm.get('total_score', 'N/A')}")
        lines.append(f"  内容摘要: {body[:200].replace(chr(10), ' ')}...")
    return "\n".join(lines)


def _summarize_field_logs(field_logs: list) -> str:
    """Summarize field log records for prompt."""
    if not field_logs:
        return "（无实战日志）"
    lines = []
    for fm, body in field_logs[:10]:
        lines.append(f"- 结果: {fm.get('result', '未知')}, 客户类型: {fm.get('customer_type', '未指定')}, 场景: {fm.get('scene', '未指定')}")
        if body.strip():
            lines.append(f"  内容: {body[:150].replace(chr(10), ' ')}...")
    return "\n".join(lines)


def _generate_proposal(skill_path: Path, skill_fm: dict, skill_body: str, reviews: list, field_logs: list, note: str = "") -> Path:
    """Generate and save a proposal for a skill."""
    wins = 0
    losses = 0
    for fm, _ in field_logs:
        result = fm.get("result", "")
        if result in ("成交", "推进"):
            wins += 1
        elif result in ("失败", "流失", "搁置", "停滞"):
            losses += 1

    reviews_summary = _summarize_reviews(reviews)
    field_logs_summary = _summarize_field_logs(field_logs)

    prompt = render_template("propose_update.md", {
        "skill_name": skill_fm.get("name", skill_path.stem),
        "skill_body": skill_body,
        "wins": wins,
        "losses": losses,
        "reviews_summary": reviews_summary,
        "field_logs_summary": field_logs_summary,
    })

    result = run_llm(prompt)

    proposal_id = timestamp_id("proposal")
    PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROPOSALS_DIR / f"{proposal_id}.md"
    frontmatter = {
        "id": proposal_id,
        "type": "proposal",
        "skill_id": skill_fm.get("id", ""),
        "skill_name": skill_fm.get("name", ""),
        "wins": wins,
        "losses": losses,
        "note": note,
        "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }
    write_markdown(out_path, frontmatter, result)
    return out_path


def propose_update_command(skill: str = "", reason: str = "", limit: int = 5) -> str:
    """Generate update proposals for mature/tested skills or a single skill."""
    if skill:
        skill_path = find_skill(skill) if not Path(skill).exists() else Path(skill)
        if not skill_path or not skill_path.exists():
            return (
                f"找不到 skill：{skill}\n\n"
                "你可以：\n"
                "1. 检查 data/skills/ 目录\n"
                "2. 使用完整文件路径\n"
                "3. 先运行 skill-forge distill 生成 Skill"
            )
        fm, body = read_markdown(skill_path)
        reviews, field_logs = _find_related_records(fm.get("id", ""))
        out_path = _generate_proposal(skill_path, fm, body, reviews, field_logs, reason)
        return (
            f"更新提案已生成：\n"
            f"  - 路径: {out_path}\n"
            f"  - Skill: {fm.get('name', skill)}\n\n"
            f"下一步建议：\n"
            f"  skill-forge apply-review --review <review-id> --skill {fm.get('id', skill)}"
        )

    # Scan all mature/tested skills
    targets = []
    for status in ["mature", "tested"]:
        status_dir = SKILLS_DIR / status
        if not status_dir.exists():
            continue
        for md_file in list_markdown_files(status_dir):
            try:
                fm, body = read_markdown(md_file)
                targets.append((md_file, fm, body))
            except Exception:
                continue

    if not targets:
        return "未找到 mature/tested 状态的 Skill。请先通过 drill/review/field-log 提升 Skill 状态。"

    generated = []
    for skill_path, fm, body in targets[:limit]:
        reviews, field_logs = _find_related_records(fm.get("id", ""))
        # Skip skills with no field data
        if not reviews and not field_logs:
            continue
        out_path = _generate_proposal(skill_path, fm, body, reviews, field_logs, reason)
        generated.append((fm.get("name", skill_path.stem), fm.get("id", ""), out_path))

    if not generated:
        return "找到 mature/tested Skill，但都没有关联的复盘或实战日志，无法生成数据驱动的提案。"

    lines = [f"已生成 {len(generated)} 个更新提案：\n"]
    for name, sid, path in generated:
        lines.append(f"  - {name} ({sid})")
        lines.append(f"    提案: {path}")
    lines.append("\n下一步建议：")
    lines.append("  skill-forge apply-review --review <review-id> --skill <skill-id>")
    return "\n".join(lines)


def apply_update_command(proposal: str, skill: str = "") -> str:
    """Apply a proposed update to a skill (MVP: manual guidance only)."""
    proposal_path = None
    if Path(proposal).exists():
        proposal_path = Path(proposal)
    else:
        for md_file in PROPOSALS_DIR.glob("*.md"):
            try:
                fm, _ = read_markdown(md_file)
                if fm.get("id") == proposal:
                    proposal_path = md_file
                    break
            except Exception:
                continue

    if not proposal_path or not proposal_path.exists():
        return f"找不到提案：{proposal}"

    pm, proposal_body = read_markdown(proposal_path)
    skill_id = pm.get("skill_id", skill)

    if not skill_id:
        return "提案中未关联 Skill，请用 --skill 参数指定。"

    skill_path = find_skill(skill_id)
    if not skill_path or not skill_path.exists():
        return f"找不到 Skill：{skill_id}"

    skill_fm, skill_body = read_markdown(skill_path)

    diff_content = f"""# Skill 更新记录

## 原始 Skill
文件：{skill_path}

## 更新提案
文件：{proposal_path}

## 提案内容
{proposal_body}

---

## 手动更新指引

请根据提案内容手动编辑 Skill 文件，或使用 apply-review 基于复盘自动迭代。

更新后，建议：
1. 运行 drill 验证效果
2. 运行 review 检查实战表现
3. 系统会自动更新 status 和 metrics
"""

    update_id = timestamp_id("update")
    update_dir = SKILLS_DIR / "updates"
    update_dir.mkdir(parents=True, exist_ok=True)
    out_path = update_dir / f"{update_id}-update.md"
    frontmatter = {
        "id": update_id,
        "skill_id": skill_id,
        "proposal_id": pm.get("id", ""),
        "status": "pending_manual",
    }
    write_markdown(out_path, frontmatter, diff_content)

    lines = [
        "更新指引已生成：",
        f"  - 路径: {out_path}",
        f"  - Skill: {skill_fm.get('name', skill_id)}",
        "",
        "当前版本不会自动修改 Skill，请使用 apply-review 命令基于复盘自动迭代，或手动编辑。",
    ]
    return "\n".join(lines)
