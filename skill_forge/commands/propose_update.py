from __future__ import annotations
from pathlib import Path
from datetime import datetime

from ..config import SKILLS_DIR
from ..storage import write_markdown, read_markdown, timestamp_id
from ..skill_manager import find_skill
from ..llm import run_llm


def propose_update_command(skill: str, reason: str = "") -> str:
    """Generate a proposed update for a skill based on reviews and drills."""
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

    # Build context for LLM
    context = f"""当前 Skill 内容：

{body}

"""
    if reason:
        context += f"更新原因：{reason}\n\n"

    context += """请基于以上内容，提出具体的更新建议。

要求：
1. 不要重写整个 Skill，只提出需要修改的部分
2. 明确标注要修改的章节
3. 给出修改前和修改后的对比
4. 说明修改理由
5. 如果不需要修改，请明确说明

请按以下格式输出：

## 更新提案

### 修改 1：[章节名]
**修改前：**
[原文]

**修改后：**
[新内容]

**理由：**
[为什么这样改]

### 修改 2：[章节名]
...

## 总结
[整体评估和建议]
"""

    result = run_llm(context)

    # Save proposal
    proposal_id = timestamp_id("proposal")
    proposal_dir = SKILLS_DIR / "proposals"
    proposal_dir.mkdir(parents=True, exist_ok=True)
    out_path = proposal_dir / f"{proposal_id}-proposal.md"
    frontmatter = {
        "id": proposal_id,
        "skill_id": skill,
        "skill_name": fm.get("name", ""),
        "reason": reason,
        "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }
    write_markdown(out_path, frontmatter, result)

    lines = [
        "更新提案已生成：",
        f"  - 路径: {out_path}",
        f"  - Skill: {fm.get('name', skill)}",
        "",
        "下一步：",
        "  1. 查看提案内容",
        "  2. 确认修改后运行：",
        f"     skill-forge apply-update --proposal {proposal_id}",
        "  3. 或手动编辑 Skill 文件",
    ]
    return "\n".join(lines)


def apply_update_command(proposal: str, skill: str = "") -> str:
    """Apply a proposed update to a skill. Requires human confirmation."""
    from ..config import SKILLS_DIR as SD
    proposal_dir = SD / "proposals"

    # Find proposal
    proposal_path = None
    if Path(proposal).exists():
        proposal_path = Path(proposal)
    else:
        for md_file in proposal_dir.glob("*.md"):
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

    # For MVP, just save the proposal as a diff file for manual review
    # Auto-apply would be dangerous without human confirmation
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

请根据提案内容手动编辑 Skill 文件。

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
        "当前版本不会自动修改 Skill，请手动编辑后运行 drill 验证。",
    ]
    return "\n".join(lines)
