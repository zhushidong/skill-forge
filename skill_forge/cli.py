from __future__ import annotations
import typer
from rich.console import Console

app = typer.Typer(
    name="skill-forge",
    help="面向销售、客服、培训团队的商业经验结构化工具",
    no_args_is_help=True,
)
console = Console()


@app.command()
def init(
    force: bool = typer.Option(False, "--force", "-f", help="覆盖已有模板"),
):
    """初始化目录结构和默认模板。"""
    from .commands.init_cmd import init_command
    result = init_command(force=force)
    console.print(result)


@app.command()
def ingest(
    type: str = typer.Option(..., "--type", "-t", help="资料类型"),
    title: str = typer.Option(..., "--title", help="资料标题"),
    file: str = typer.Option(None, "--file", "-f", help="文件路径"),
    text: str = typer.Option(None, "--text", help="文本内容"),
    note: str = typer.Option("", "--note", "-n", help="备注"),
    tags: str = typer.Option("", "--tags", help="标签，逗号分隔"),
):
    """导入普通资料。"""
    from .commands.ingest import ingest_command
    result = ingest_command(material_type=type, title=title, file=file, text=text, note=note, tags=tags)
    console.print(result)


@app.command(name="inspect")
def inspect_cmd(
    file: str = typer.Option(..., "--file", "-f", help="文件路径"),
    type: str = typer.Option("auto", "--type", "-t", help="资产类型"),
):
    """检查外部 Agent/Skill/Prompt，判断可熔炼能力。"""
    from .commands.inspect_cmd import inspect_command
    result = inspect_command(file=file, asset_type=type)
    console.print(result)


@app.command()
def melt(
    file: str = typer.Option(..., "--file", "-f", help="文件路径"),
    type: str = typer.Option("auto", "--type", "-t", help="资产类型"),
    problem: str = typer.Option("", "--problem", "-p", help="要解决的问题"),
    target_scene: str = typer.Option("", "--target-scene", "-s", help="目标场景"),
    title: str = typer.Option("", "--title", help="Skill 标题"),
):
    """熔炼外部 Agent/Skill/Prompt 为本地 Skill 草稿。"""
    from .commands.melt import melt_command
    result = melt_command(file=file, asset_type=type, problem=problem, target_scene=target_scene, title=title)
    console.print(result)


@app.command()
def distill(
    material: str = typer.Option(..., "--material", "-m", help="Material ID 或文件路径"),
    problem: str = typer.Option(..., "--problem", "-p", help="要解决的问题"),
    title: str = typer.Option("", "--title", help="Skill 标题"),
):
    """把普通资料转成 Skill 草稿。"""
    from .commands.distill import distill_command
    result = distill_command(material=material, problem=problem, title=title)
    console.print(result)


@app.command()
def drill(
    skill: str = typer.Option(..., "--skill", "-s", help="Skill ID 或文件路径"),
    persona: str = typer.Option("", "--persona", "-p", help="客户人格"),
    rounds: int = typer.Option(5, "--rounds", "-r", help="演练轮数"),
    non_interactive: bool = typer.Option(False, "--non-interactive", help="非交互模式（无 API Key 时自动使用）"),
):
    """基于 Skill 做回合制演练。"""
    from .commands.drill import drill_command
    result = drill_command(skill=skill, persona=persona, rounds=rounds, non_interactive=non_interactive)
    console.print(result)


@app.command()
def review(
    file: str = typer.Option(..., "--file", "-f", help="聊天记录文件"),
    result: str = typer.Option(..., "--result", "-r", help="沟通结果"),
    skill: str = typer.Option("", "--skill", "-s", help="关联 Skill ID"),
):
    """复盘真实客户沟通。"""
    from .commands.review import review_command
    result_text = review_command(file=file, result=result, skill=skill)
    console.print(result_text)


@app.command()
def recommend(
    file: str = typer.Option(..., "--file", "-f", help="当前聊天记录文件"),
    context: str = typer.Option("", "--context", "-c", help="背景信息"),
):
    """根据当前客户沟通记录推荐下一招。"""
    from .commands.recommend import recommend_command
    result = recommend_command(file=file, context=context)
    console.print(result)


@app.command(name="search")
def search_cmd(
    query: str = typer.Option("", "--query", "-q", help="搜索关键词"),
    status: str = typer.Option("", "--status", help="按状态筛选"),
):
    """搜索或列出本地 Skill。"""
    from .commands.search import search_command
    result = search_command(query=query, status=status)
    console.print(result)


@app.command(name="propose-update")
def propose_update_cmd(
    skill: str = typer.Option(..., "--skill", "-s", help="Skill ID 或文件路径"),
    reason: str = typer.Option("", "--reason", "-r", help="更新原因"),
):
    """生成 Skill 更新提案。"""
    from .commands.propose_update import propose_update_command
    result = propose_update_command(skill=skill, reason=reason)
    console.print(result)


@app.command(name="apply-update")
def apply_update_cmd(
    proposal: str = typer.Option(..., "--proposal", "-p", help="提案 ID 或文件路径"),
    skill: str = typer.Option("", "--skill", "-s", help="Skill ID（可选）"),
):
    """应用更新提案（需人工确认）。"""
    from .commands.propose_update import apply_update_command
    result = apply_update_command(proposal=proposal, skill=skill)
    console.print(result)


@app.command()
def history(
    skill: str = typer.Option(..., "--skill", "-s", help="Skill ID 或文件路径"),
):
    """查看 Skill 版本历史。"""
    from .commands.version_cmd import history_command
    result = history_command(skill=skill)
    console.print(result)


@app.command()
def diff(
    skill: str = typer.Option(..., "--skill", "-s", help="Skill ID 或文件路径"),
    from_version: str = typer.Option(..., "--from", help="起始版本号"),
    to_version: str = typer.Option("current", "--to", help="目标版本号（默认当前版本）"),
):
    """对比 Skill 两个版本的差异。"""
    from .commands.version_cmd import diff_command
    result = diff_command(skill=skill, from_version=from_version, to_version=to_version)
    console.print(result)


@app.command()
def rollback(
    skill: str = typer.Option(..., "--skill", "-s", help="Skill ID 或文件路径"),
    to_version: str = typer.Option(..., "--to", help="要回滚到的版本号"),
):
    """回滚 Skill 到指定版本。"""
    from .commands.version_cmd import rollback_command
    result = rollback_command(skill=skill, to_version=to_version)
    console.print(result)


@app.command()
def validate(
    file: str = typer.Option(..., "--file", "-f", help="要验证的文件路径"),
    category: str = typer.Option("auto", "--category", "-c", help="资产类型 (auto/materials/skills/drills/reviews)"),
):
    """校验文件是否符合 Schema 规范。"""
    from pathlib import Path
    from .storage import read_markdown
    from .validation import validate_front_matter, SCHEMA_MAP
    
    path = Path(file)
    try:
        fm, body = read_markdown(path)
    except Exception as e:
        console.print(f"[red]文件读取失败: {e}[/red]")
        return
    
    if not fm:
        console.print("[yellow]未找到 YAML front matter[/yellow]")
        return
    
    # Auto-detect category
    if category == "auto":
        if "scores" in fm and "skill_id" in fm:
            if "result" in fm and fm.get("result") in ("推进", "成交", "失败", "流失"):
                category = "reviews"
            else:
                category = "drills"
        elif "customer_signals" in fm or "applicable_scenarios" in fm or fm.get("status") in ("draft", "trained", "tested", "mature", "retired"):
            category = "skills"
        elif "type" in fm and fm.get("type") in ("article", "book", "chatlog", "case", "comment", "prompt", "workflow", "external_agent", "external_skill"):
            category = "materials"
        else:
            category = "materials"
    
    is_valid, errors = validate_front_matter(fm, category)
    
    if is_valid:
        console.print(f"[green]校验通过[/green] (类型: {category})")
        console.print(f"  ID: {fm.get('id', 'N/A')}")
        console.print(f"  Name: {fm.get('name', 'N/A')}")
        if "version" in fm:
            console.print(f"  Version: {fm['version']}")
        if "status" in fm:
            console.print(f"  Status: {fm['status']}")
    else:
        console.print(f"[red]校验失败[/red] (类型: {category})")
        for err in errors:
            console.print(f"  - {err}")


if __name__ == "__main__":
    app()
