# Skill Forge 搭建全记录：从零到一

> 写给完全没有编程经验的朋友。我会尽可能用大白话解释每件事。

---

## 目录

1. [这个项目是干嘛的？](#1-这个项目是干嘛的)
2. [你需要什么工具](#2-你需要什么工具)
3. [项目是怎么搭起来的](#3-项目是怎么搭起来的)
4. [核心概念：什么是 Skill？](#4-核心概念什么是-skill)
5. [拆解每个文件](#5-拆解每个文件)
6. [Skill 的一生：状态机](#6-skill-的一生状态机)
7. [安全：黑客来了怎么办](#7-安全黑客来了怎么办)
8. [测试：怎么保证代码没坏](#8-测试怎么保证代码没坏)
9. [用这个项目你能学会什么](#9-用这个项目你能学会什么)

---

## 1. 这个项目是干嘛的？

### 现实中的问题

想象你是卖课的销售。客户说"太贵了"，你该怎么办？

老销售知道怎么回答，新销售不知道。老销售的经验只在脑子里，没法复制。如果把老销售的成功话术**结构化**成一份文档，新人照着练就能学会，那该多好。

Skill Forge 就是做这件事的——**把经验变成结构化的 "Skill"（技能）**。

### 具体场景

你可以把以下几种东西变成 Skill：

| 原始材料 | 变成 Skill 后 | 用途 |
|---------|--------------|------|
| 一段聊天记录（客户嫌贵） | "价格异议处理 Skill" | 下次遇到同样情况，知道该说什么 |
| 一个培训文档 | "客户分类 Skill" | 新销售可以照着练 |
| 一个 AI Agent 的配置文件 | "智能问答 Skill" | 把外部工具的经验吸收进来 |

### 三个关键词

1. **提炼**（Distill）：把案例/材料变成 Skill
2. **演练**（Drill）：假装你是客户，和 Skill 对练
3. **复盘**（Review）：复盘真实对话，看看 Skill 哪里需要改进

---

## 2. 你需要什么工具

### 必装

| 工具 | 版本 | 怎么装 | 为什么用 |
|------|------|--------|---------|
| **Python** | 3.10+ | 去 python.org 下载安装 | 项目是用 Python 写的 |
| **Git** | 任意 | 去 git-scm.com 下载安装 | 用来下载代码和版本管理 |

### 安装后验证

打开 cmd，输入：

```cmd
python --version
```
应该显示 `Python 3.10.x` 或更新的。

```cmd
git --version
```
应该显示 `git version 2.x.x`。

### 可选

| 工具 | 用途 |
|------|------|
| VS Code | 写代码的编辑器，推荐 |
| OpenAI API Key | 如果想自动调用 AI，需要花钱买（但项目没 Key 也能用） |

---

## 3. 项目是怎么搭起来的

### 3.1 初始状态：空目录

最开始只有一个想法："我要做一个把经验变成 Skill 的工具"。目录里什么都没有。

### 3.2 项目骨架

首先搭起最基本的架子：

```
skill-forge/
├── skill_forge/           # 核心代码（Python 包）
│   └── cli.py            # CLI 入口——用户敲命令的地方
├── pyproject.toml         # 项目配置文件
├── README.md              # 说明文档
└── .gitignore             # 哪些文件不提交到 Git
```

**什么叫 Python 包？**
- 就是一堆 `.py` 文件的文件夹
- 最下面有个 `__init__.py` 文件（可以是空的），告诉 Python "这个文件夹里的代码可以导入使用"

### 3.3 增加功能模块

随着需求变多，代码越来越多，需要分类放：

```
skill_forge/
├── cli.py                  # 命令入口——每条命令绑定到这里
├── commands/               # 各个命令的具体实现
│   ├── _promote.py        # 晋升引擎（共享逻辑）
│   ├── apply_review.py    # 应用复盘建议
│   ├── distill.py         # 提炼案例->Skill
│   ├── drill.py            # 演练
│   ├── field_log.py        # 记录实战结果
│   ├── ingest.py           # 导入资料
│   ├── init_cmd.py         # 初始化
│   ├── inspect_cmd.py      # 检查外部资产
│   ├── melt.py             # 熔炼外部文件
│   ├── promote.py          # 手动晋升
│   ├── propose_update.py   # 生成更新提案
│   ├── recommend.py        # 推荐下一招
│   ├── review.py           # 复盘
│   ├── search.py           # 搜索
│   └── version_cmd.py      # 版本管理
├── adapters/               # 适配器——把不同格式转成统一文本
│   ├── constants.py        # 常量定义
│   ├── generic_agent.py    # Agent/Skill 文档适配器
│   ├── json_adapter.py     # JSON 适配器
│   ├── markdown.py         # Markdown 适配器
│   ├── prompt_adapter.py   # Prompt 适配器
│   └── yaml_adapter.py     # YAML 适配器
├── config.py               # 全局配置
├── llm.py                  # AI 调用封装
├── models.py               # 旧的数据模型（逐渐淘汰）
├── parsers.py              # 文件解析器
├── skill_manager.py        # Skill 管理（指标更新）
├── storage.py              # 文件存储层
├── template_content.py     # 内置 Prompt 模板
├── templates.py            # 模板渲染引擎
└── validation.py           # Schema 校验
```

### 3.4 数据文件

用户创建的数据存在这里（已被 `.gitignore` 忽略，不会提交到 Git）：

```
data/
├── materials/              # 导入的原始材料
│   └── cases/             # 案例
├── skills/                 # Skill 文件
│   ├── draft/             # 草稿
│   ├── trained/           # 已训练
│   ├── tested/            # 已测试
│   └── mature/            # 成熟
├── drills/                 # 演练记录
├── field_logs/             # 实战记录
├── reviews/                # 复盘记录
├── recommendations/        # 推荐记录
└── proposals/              # 更新提案
```

### 3.5 测试文件

```
tests/
├── test_absorbed.py        # 核心功能测试（38个）
├── test_attack_defense.py  # 安全攻击测试（47个）
├── test_golden_lifecycle.py# 完整生命周期测试
├── test_llm.py             # AI 相关测试
├── test_storage.py         # 存储层测试
└── test_validation.py     # Schema 校验测试
```

### 3.6 文档示例

```
examples/
├── comparison.md           # 和同类项目对比
├── golden-lifecycle.md     # 完整生命周期示例
├── quickstart.md           # 快速开始
├── scenarios/              # 各种场景的示例
│   ├── sales-scenarios.md
│   ├── support-scenarios.md
│   └── training-scenarios.md
├── scoring-rubric.md       # 评分标准
├── skill-format.md         # Skill 格式规范
└── skill-schema.md         # Schema 详解

samples/
├── case-price.md           # 示例案例
├── current-chat.md         # 示例对话
├── external-agent.md       # 示例 Agent 文件
├── external-agent.yaml     # 示例 YAML
└── skill-price-objection.md # 示例 Skill
```

---

## 4. 核心概念：什么是 Skill？

### 4.1 文件格式

每个 Skill 是一个 Markdown 文件（`.md`），里面有两大块：

```
---
id: skill-abc123
name: 价格异议处理
version: 1.0.0
status: draft
---                         ← YAML Front Matter（元数据）
                           ← 分隔线
# 价格异议处理 Skill        ← 正文（Markdown）
```

**YAML Front Matter** 是什么？
- 文件最上面用 `---` 包起来的区块
- 里面是键值对（key: value），写的是元数据（metadata，关于数据的数据）
- 格式叫 YAML，一种人类易读的数据格式

**正文** 就是普通的 Markdown，用来写详细描述。

### 4.2 YAML 基础

```yaml
# 这是注释
name: 价格异议处理          # 字符串
age: 5                      # 数字
is_active: true              # 布尔值（true/false）
tags:                       # 列表
  - 价格
  - 异议
metrics:                    # 嵌套结构（字典套字典）
  drills: 3
  wins: 2
```

### 4.3 Skill 的完整结构

```yaml
id: skill-xxx-001           # 唯一 ID（必填）
name: 价格异议处理 Skill     # 名称（必填）
version: "1.0.0"            # 语义化版本号
status: draft               # 当前状态

# 定位
domain: sales               # 领域
problem: 客户嫌贵怎么应对    # 解决什么问题
goal: 把焦点从价格转移到价值  # 要达到的目标

# 客户画像
customer_types:             # 什么样的客户适用
  - 中小企业主
customer_stages:            # 客户处在什么阶段
  - 价格谈判

# 场景与信号
applicable_scenarios:       # 什么情况下用
  - 客户说太贵
not_applicable_scenarios:   # 什么情况下不用
  - 客户已决定购买
customer_signals:           # 客户说什么话触发这个 Skill
  - "太贵了"

# 策略（四维度）
strategy:
  diagnosis: 判断客户真没钱还是只是砍价
  response_quality: 用确认-重构-量化-推进四步法
  next_step_control: 每次回应都争取下一步
  risk_control: 不主动降价

# 内容
steps:                      # 执行步骤
  - 确认客户真实顾虑
  - 重构比较维度
example_lines:              # 示例话术
  - "我理解您的顾虑..."
forbidden_behaviors:        # 禁止做的事
  - 直接降价

# 指标（系统自动更新）
metrics:
  drills: 3                 # 演练次数
  field_tests: 5            # 实战次数
  wins: 3                   # 成功次数
  losses: 2                 # 失败次数
  avg_score: 75.0           # 平均评分
```

### 4.4 什么叫嵌套？

就像俄罗斯套娃——字典里面还有字典。比如 `metrics` 里面又有 `drills`、`wins` 等字段。用 Python 获取值的写法是：

```python
fm["metrics"]["drills"]     # 先取 metrics，再取 drills
```

---

## 5. 拆解每个文件

我会从"用户敲了一个命令"开始，追踪代码的执行路径。

### 5.1 用户敲命令：cli.py

当用户输入 `skill-forge distill --material xxx --problem xxx` 时：

```python
# cli.py（简化版）
@app.command()              # 声明这是一个命令
def distill(                # 函数名就是命令名
    material: str = ...,    # --material 参数
    problem: str = ...,     # --problem 参数
    title: str = "",        # --title 参数（可选）
):
    from .commands.distill import distill_command
    result = distill_command(material=material, problem=problem, title=title)
    console.print(result)   # 输出结果给用户
```

**用了什么？**
- `typer` 库：一个 Python 库，让写命令行的项目变得极其简单
- `@app.command()` 叫**装饰器**（decorator），就是给函数贴个标签，说"这是个命令"

### 5.2 配置中心：config.py

所有全局配置集中在这里：

```python
# 加载 .env 文件（如果有）
load_dotenv()

# 项目根目录 = 用户执行命令时的目录
PROJECT_ROOT = Path.cwd()

# API 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
```

**重要的设计决策**：
- `PROJECT_ROOT = Path.cwd()` 而不是 `Path(__file__).parent.parent`
  - `cwd()` = 用户运行命令时所在的目录
  - 这样用户不管从哪里运行 `skill-forge`，数据都写在他想写的地方
  - 如果用 `__file__`（代码所在的目录），那装到系统里后数据会写到安装目录，可能没有写权限

### 5.3 存储层：storage.py

负责读写文件。核心函数：

```python
def read_markdown(path) -> (dict, str):
    """读一个 Markdown 文件，返回 (frontmatter, body)。"""
    content = path.read_text(encoding="utf-8")
    # 用正则解析 --- 之间的 YAML
    fm = yaml.safe_load(frontmatter_text)
    return fm, body

def write_markdown(path, frontmatter: dict, body: str):
    """写一个 Markdown 文件。"""
    safe_path = _validate_path(path)  # 安全检查
    # 把字典转成 YAML 文本
    fm_text = yaml.safe_dump(frontmatter, allow_unicode=True)
    # 组合成 --- \n YAML \n --- \n 正文
    path.write_text(f"---\n{fm_text}---\n{body}", encoding="utf-8")
```

**什么是 `yaml.safe_dump`？**
- `dump` = 把 Python 字典转成 YAML 文本
- `safe` = 安全的，不会执行 YAML 里面的危险代码（比如 `!!python/object:...`）

### 5.4 AI 调用：llm.py

```python
def run_llm(prompt: str) -> str:
    """如果设置了 API Key，调 AI；否则给用户返回完整 Prompt。"""
    if not has_api_key():
        return _fallback_prompt(prompt)
    
    client = OpenAI(
        api_key=config.OPENAI_API_KEY,
        base_url=config.OPENAI_BASE_URL,  # 支持代理
    )
    response = client.chat.completions.create(
        model=config.DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return sanitize_llm_output(response.choices[0].message.content)
```

**无 Key 模式**：这是 Skill Forge 的一个重要设计——即使你没有 OpenAI 账号，所有命令都能工作。它会输出完整的 Prompt，你可以手动复制到 ChatGPT/Claude 等工具。

### 5.5 Schema 校验：validation.py

用 Pydantic 库定义数据结构：

```python
class SkillFrontMatter(BaseModel):
    id: str = Field(..., min_length=1)    # ... 表示必填
    name: str = Field(..., min_length=1)
    version: str = Field(default="1.0.0")
    status: str = Field(..., pattern=r'^(draft|trained|tested|mature|retired)$')
    metrics: SkillMetrics = Field(default_factory=SkillMetrics)  # 嵌套
```

**什么是 Pydantic？**
- 一个 Python 库，用来做数据校验
- 你定义好数据结构（字段名、类型、默认值），它自动检查输入是否合法
- 比如 `status` 字段只能填 `draft/trained/tested/mature/retired` 之一，填其他就报错

**为什么用"可选链"写法？**
```python
fm.get("metrics", {})        # 安全获取 metrics
fm.get("applicable_scenarios", []) or fm.get("scenes", [])  # 新字段不存在就试旧字段
```

### 5.6 模板引擎：templates.py

```
{{skill_name}}  → 替换成具体的内容
```

比如模板里写 `你好，{{name}}`，传 `{"name": "张三"}`，就变成 `你好，张三`。

```python
def render_template(template_name: str, variables: dict) -> str:
    for key, value in variables.items():
        text = text.replace("{{" + key + "}}", str(value))
    return text
```

**安全考虑**：如果变量的值里包含 `{{xxx}}`，会被转义成 HTML 实体 `&#123;`，防止模板注入攻击。

### 5.7 适配器：adapters/

为什么要适配器？因为用户要导入的文件格式可能不同：JSON、YAML、Markdown...

```
用户输入一个 .json 文件 → parser 解析 → 适配器转成统一文本 → LLM 处理
```

```python
# adapters/__init__.py
def to_text(parsed_asset: dict, asset_type: str = "auto") -> str:
    file_type = parsed_asset.get("type", "text")
    if file_type == "json":
        return json_to_text(parsed_asset)
    if file_type == "yaml":
        return yaml_to_text(parsed_asset)
    if file_type == "markdown":
        return markdown_to_text(parsed_asset)
```

### 5.8 晋升引擎：_promote.py

这是 Skill 状态自动晋升的核心逻辑：

```python
# 晋升规则字典
_AUTO_PROMOTE_RULES = {
    "draft": {
        "to": "trained",
        "check": lambda m: m.get("drills", 0) >= 3 and m.get("avg_score", 0) >= 60,
    },
    "trained": {
        "to": "tested",
        "check": lambda m: m.get("field_tests", 0) >= 1,
    },
    "tested": {
        "to": "mature",
        "check": lambda m: (m.get("field_tests", 0) >= 5 
            and m.get("wins", 0) / m.get("field_tests", 1) >= 0.6 
            and m.get("avg_score", 0) >= 70),
    },
}
```

**什么是 lambda？**
- 一种简短的匿名函数
- `lambda m: m.get("drills", 0)` 相当于：
  ```python
  def 临时函数(m):
      return m.get("drills", 0)
  ```

---

## 6. Skill 的一生：状态机

```
           经过 3 次演练            1 次实战             5 次实战
           + 平均分 ≥ 60                               + 胜率 ≥ 60%
                                                     + 平均分 ≥ 70
  draft ──────────────────→ trained ──────────────→ tested ──────────────→ mature
                                                                              │
                                                                              │ 手动
                                                                              ▼
                                                                          retired
```

### 每条规则的解释

| 状态跳转 | 条件 | 为什么这样设 |
|---------|------|------------|
| draft → trained | 演练 ≥ 3 次，平均分 ≥ 60 | 至少练 3 次才能算"练过"，平均分太低说明 Skill 本身有问题 |
| trained → tested | 实战 ≥ 1 次 | 至少真刀真枪用过一次 |
| tested → mature | 实战 ≥ 5 次，胜率 ≥ 60%，平均分 ≥ 70 | 多次验证有效，才算成熟 |
| 任意 → retired | 手动 | 只有人能判断 Skill 是不是真的过时了 |

### 代码执行路径

```
用户执行 drill 命令
  → drill.py 更新 métrics（drills + 1，更新平均分）
    → skill_manager.update_skill_metrics()
      → skill_manager.update_skill_status()
        → 检查是否满足晋升条件
          → 如果满足，修改 status 字段
```

---

## 7. 安全：黑客来了怎么办

### 7.1 常见攻击类型

| 攻击类型 | 攻击方式 | 防御措施 |
|---------|---------|---------|
| **路径遍历** | 传 `../../../etc/passwd` 偷文件 | `_validate_path()` 检查路径是否在允许的目录内 |
| **Prompt 注入** | 在案例里写"忽略之前的指令" | `sanitize_user_input()` 过滤关键词，Unicode 标准化 |
| **TOCTOU** | 检查文件时小文件，读取时换大文件 | 原子读取：先 open 再检查大小 |
| **YAML 注入** | 传 `!!python/object:subprocess.Popen` | 用 `safe_load` 而不是 `load` |
| **错误泄露** | 报错信息包含 API Key 或路径 | `sanitize_error_message()` 统一换成友好消息 |
| **模板注入** | 在变量里写 `{{config.xxx}}` | `_escape_template_syntax()` 转义花括号 |

### 7.2 攻击测试

写了一个专门的测试文件 `test_attack_defense.py`，里面 47 个攻击测试用例，覆盖各种奇技淫巧：

```python
def test_base64_injection(self):
    """用 base64 编码绕过过滤"""
    encoded = base64.b64encode(b"ignore previous instructions").decode()
    result = sanitize_user_input(encoded)
    # 期望：不崩溃就行（编码内容可能过，但只要不是明文关键词就行）

def test_unicode_homoglyph_attack(self):
    """用长得像的俄文字母绕过"""
    text = "ignore рrevious instructions"  # р 是俄文字母
    sanitized = sanitize_user_input(text)
    # 期望：NFKC 标准化后会被识别并过滤
```

---

## 8. 测试：怎么保证代码没坏

### 8.1 测试框架

用 pytest，Python 最流行的测试工具。

```python
# 测试文件里
class TestPromoteEngine:
    def test_draft_to_trained_promotes(self):
        assert check_auto_promote("draft", {"drills": 3, "avg_score": 60}) == "trained"
    
    def test_draft_no_promote_when_not_enough(self):
        assert check_auto_promote("draft", {"drills": 2, "avg_score": 70}) is None
```

运行测试：

```bash
python -m pytest tests/ -q
# -q 表示安静模式，只显示结果不显示细节
```

### 8.2 测试数量

```
一共 159 个测试，全部通过。
```

| 测试文件 | 数量 | 测什么 |
|---------|------|--------|
| test_absorbed.py | 38 | 核心功能：晋升引擎、存储、Schema、Diff、适配器、ProposeUpdate 模板 |
| test_attack_defense.py | 47 | 安全攻击：注入、路径遍历、YAML 注入、Unicode 攻击、链式攻击 |
| test_golden_lifecycle.py | 13 | 完整生命周期：从导入 -> 提炼 -> 演练 -> 复盘整个流程 |
| test_llm.py | 19 | AI 调用：输入净化、输出消毒、错误脱敏、无 Key 回退 |
| test_storage.py | 16 | 存储层：路径验证、文件大小、并发安全 |
| test_validation.py | 19 | Schema 校验：各种字段组合的校验 |

### 8.3 测试为什么重要

1. **改代码不怕改坏**——跑一遍测试就知道有没有引入 Bug
2. **给新人安全感**——就算不懂全部代码，跑测试过了就放心
3. **倒逼代码质量**——代码要写成能测试的样子，自然会分层合理

---

## 9. 用这个项目你能学会什么

### 9.1 Python 基础知识

| 概念 | 在项目哪里用到 |
|------|-------------|
| 变量和类型 | 到处都是：`name = "张三"` |
| 列表 List | `customer_types: list[str] = []` |
| 字典 Dict | `m.get("drills", 0)` |
| 函数 def | `def distill_command(...):` |
| 类 class | `class SkillFrontMatter(BaseModel):` |
| 模块导入 | `from ..config import SKILLS_DIR` |
| 异常处理 | `try: ... except ValueError: ...` |
| 类型提示 | `def func(name: str) -> dict:` |
| 生成器/迭代器 | `for status_dir in SKILLS_DIR.iterdir():` |

### 9.2 项目结构概念

| 概念 | 说明 |
|------|------|
| Package | 多个 `.py` 文件的文件夹，有 `__init__.py` |
| CLI | Command Line Interface，命令行界面 |
| 路由 | 不同的命令走向不同的处理函数 |
| 配置中心 | 所有配置集中到一个文件，好管理 |
| 分层 | commands/（业务逻辑）、storage/（数据持久化）、parsers/（格式解析） |
| 适配器模式 | 不同格式（JSON/YAML/MD）统一接口 |

### 9.3 工程实践

| 实践 | 说明 |
|------|------|
| Git 版本控制 | `git add/commit/push` |
| 语义化版本 | `1.0.0` → `1.1.0` → `2.0.0` |
| 测试驱动 | 先想好怎么测，再写代码 |
| 安全审计 | 模拟黑客攻击，找到漏洞 |
| Schema 校验 | 用 Pydantic 保证数据格式正确 |
| 防御性编程 | 假设输入都是恶意的，做了各种保护 |

### 9.4 什么是"设计决策"？为什么做这些选择？

每一个设计决策背后都有原因。这里记录一些关键的：

```
Q: 为什么要用 Path.cwd() 而不是 Path(__file__).parent？
A: 因为用户应该在任意目录运行此工具，数据写到他当前目录

Q: 为什么不用数据库（比如 SQLite）而用文件系统？
A: 为了简单——每个 Skill 就是一个 .md 文件，用 VS Code 就能改

Q: 为什么不用向量搜索做推荐？
A: 向量搜索需要 embedding 模型，依赖外部服务。关键词搜索零依赖

Q: 为什么 Schema 加了 extra='allow'？
A: 用户可能想扩展字段，不用改代码就能加。灵活比死板好

Q: 为什么外部文件读取不限制路径了？
A: 用户用 inspect/melt 命令时，心智模型是“我要读我的文件”，
   限制在 workspace 里会困惑。但写入仍然严格限制。
```

---

## 10. 总结

Skill Forge 从零到最终形态经历了：

1. **搭骨架**：CLI + 配置 + 存储
2. **加功能**：提炼/演练/复盘/推荐/搜索/版本管理
3. **做安全**：两轮地狱级攻防，堵住各种漏洞
4. **对齐 Schema**：确保所有命令用的数据结构一致
5. **写测试**：159 个测试覆盖核心功能和安全边界
6. **出文档**：README、示例、这个复盘文档

从一个空目录到 **35 个文件、2292 行新增代码**，最终变成一个有完整功能的 CLI 工具。

---

*文档日期：2026-06-18*
*项目地址：https://github.com/zhushidong/skill-forge*
