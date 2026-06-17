from __future__ import annotations
from pathlib import Path
import os

from ..config import SKILLS_DIR, DRILLS_DIR
from ..storage import write_markdown, read_markdown, timestamp_id
from ..templates import render_template
from ..llm import run_llm, run_llm_with_history
from ..skill_manager import find_skill, update_skill_metrics, update_skill_status


def drill_command(skill: str, persona: str = "", rounds: int = 5, non_interactive: bool = False) -> str:
    """Run a drill session based on a Skill."""
    # Find skill file
    skill_path = find_skill(skill) if not Path(skill).exists() else Path(skill)

    if not skill_path or not skill_path.exists():
        return (
            f"找不到 skill：{skill}\n\n"
            "你可以：\n"
            "1. 检查 data/skills/ 目录\n"
            "2. 使用完整文件路径\n"
            "3. 先运行 skill-forge distill 生成 Skill"
        )

    _, skill_body = read_markdown(skill_path)

    # Render drill prompt
    base_prompt = render_template("drill.md", {
        "skill": skill_body,
        "persona": persona or "普通客户",
        "rounds": str(rounds),
    })

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        drill_id = timestamp_id("drill")
        out_path = DRILLS_DIR / f"{drill_id}.md"
        frontmatter = {
            "id": drill_id,
            "skill_id": skill,
            "persona": persona or "普通客户",
            "rounds": rounds,
        }
        write_markdown(out_path, frontmatter, base_prompt)
        lines = [
            "演练模式（无 API Key）：",
            f"  - Prompt 已保存: {out_path}",
            "",
            "请将以下 Prompt 复制到任意大模型中进行演练。",
            f"  - Skill: {skill}",
            f"  - 客户人格: {persona or '普通客户'}",
            f"  - 轮数: {rounds}",
        ]
        return "\n".join(lines)

    # Interactive drill with API
    print(f"\n{'='*50}")
    print(f"开始演练 - 客户人格：{persona or '普通客户'}，轮数：{rounds}")
    print(f"输入你的回复，输入 'quit' 结束演练。")
    print(f"{'='*50}\n")

    history: list[dict] = []
    dialogue_log = []

    # First call - get customer opening
    opening_prompt = base_prompt + "\n\n请扮演客户，说出你的第一句话。只输出客户说的话。"
    customer_msg = run_llm(opening_prompt)
    print(f"【客户】：{customer_msg}\n")
    dialogue_log.append(f"【客户】：{customer_msg}")
    history.append({"role": "assistant", "content": customer_msg})

    for i in range(rounds):
        try:
            user_input = input(f"【你（第{i+1}/{rounds}轮）】：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n演练结束。")
            break

        if user_input.lower() in ("quit", "exit", "q"):
            print("演练结束。")
            break

        dialogue_log.append(f"【你】：{user_input}")
        history.append({"role": "user", "content": user_input})

        # Get customer response
        context = base_prompt + "\n\n对话历史：\n" + "\n".join(dialogue_log)
        context += "\n\n请继续扮演客户，回应用户。只输出客户说的话。"
        customer_msg = run_llm_with_history(context, history)
        print(f"【客户】：{customer_msg}\n")
        dialogue_log.append(f"【客户】：{customer_msg}")
        history.append({"role": "assistant", "content": customer_msg})

    # Get review
    print(f"\n{'='*50}")
    print("正在生成复盘...")
    print(f"{'='*50}\n")

    review_prompt = (
        base_prompt
        + "\n\n完整对话：\n"
        + "\n".join(dialogue_log)
        + "\n\n请对用户的演练进行复盘评分。输出完整复盘。"
    )
    review = run_llm(review_prompt)

    # Save drill record
    drill_id = timestamp_id("drill")
    out_path = DRILLS_DIR / f"{drill_id}.md"
    full_content = "## 对话记录\n\n" + "\n\n".join(dialogue_log) + "\n\n## 复盘\n\n" + review
    frontmatter = {
        "id": drill_id,
        "skill_id": skill,
        "persona": persona or "普通客户",
        "rounds": rounds,
    }
    write_markdown(out_path, frontmatter, full_content)

    # Update skill metrics
    metrics = update_skill_metrics(skill_path)
    new_status = update_skill_status(skill_path)

    lines = [
        f"\n{'='*50}",
        "演练结束。",
        f"  - 记录已保存: {out_path}",
        f"  - Skill 指标更新: drills={metrics.get('drills', 0)}, wins={metrics.get('wins', 0)}, losses={metrics.get('losses', 0)}",
        f"  - Skill 状态: {new_status}",
        f"{'='*50}",
    ]
    return "\n".join(lines)
