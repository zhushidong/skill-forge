# Skill Forge

面向销售、客服、培训团队的商业经验结构化工具。

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-passing-brightgreen.svg)](#测试)

## 什么是商业 Skill？

在 Skill Forge 中，一个商业 Skill 是一份**结构化的业务应对策略**，通常来自真实案例、聊天记录或培训材料。它包含：

- 适用场景
- 客户信号
- 应对步骤
- 示例话术
- 禁用行为
- 演练方法
- 复盘指标
- 历史效果

**Skill 不是 Prompt**。Prompt 是给 LLM 的指令，Skill 是给业务人员的可执行策略。

## Skill Forge 的定位：预加工工具

**Skill Forge 做的事**：

```
书/案例 → [skill-forge处理] → 结构化文档
```

**它停在这里了**。输出是**文档**，不是"能力"。

### 你要的"随意调用"还差一步

| 阶段 | 工具 | 输出 | 能调用吗？ |
|------|------|------|-----------|
| 第1步 | Skill Forge | 结构化文档 | ❌ 不能 |
| 第2步 | ？（缺） | AI可调用格式 | ✅ 能 |

### 第2步有3种做法

#### 做法1：转成 WorkBuddy Skill（最简单）
```
Skill Forge 输出 → 手动/自动转成 Skill → 你能直接调用
```
**优点**：快，能用
**缺点**：只限 WorkBuddy

#### 做法2：接入 RAG 知识库（最灵活）
```
书 → 切片 → 向量数据库 → AI 检索后回答
```
**优点**：任何 AI 都能用，支持模糊查询
**缺点**：需要搭建向量库

#### 做法3：转成 MCP 工具（最通用）
```
书 → 封装成 MCP Server → 任何 AI 都能调
```
**优点**：标准化，通用
**缺点**：开发成本高

### 怎么选？

| 你的资料类型 | 推荐路径 |
|-------------|---------|
| 案例/经验类（销售话术、客户异议） | Skill Forge → 转成 Skill → 调用 |
| 理论/知识类（产品手册、行业报告） | 直接用 RAG |
| 混合类型 | Skill Forge 处理案例部分 + RAG 处理理论部分 |

## 解决什么问题？

**问题**：销售/客服团队有大量经验（聊天记录、案例、培训材料），但这些经验：
- 散落在各处，无法复用
- 只在老员工脑子里，难以传承
- 遇到新客户场景时，不知道该用哪招
- 培训新人靠"师父带"，效率低、质量不稳定

**解决方案**：Skill Forge 把这些散落的经验"结构化"成标准 Skill，通过演练和复盘持续改进。

## 当前能力边界

### 能力成熟度

| 能力 | 成熟度 | 说明 |
|------|--------|------|
| 案例导入 | 🟢 可用 | 把 Markdown/JSON/YAML 导入为材料 |
| Skill 提炼 | 🟢 可用 | 把材料转成结构化 Skill，LLM 无 Key 时输出完整 Prompt |
| 演练（Drill） | 🟢 可用 | 模拟客户场景，结构化评分（4维度0-100） |
| 复盘（Review） | 🟢 可用 | 分析真实沟通，输出缺陷分析和更新建议 |
| 推荐（Recommend） | 🟢 可用 | 关键词/标签匹配 + 置信度 + 风险提醒，非向量检索 |
| 搜索（Search） | 🟢 可用 | 多维度搜索（关键词/场景/信号/客户类型/状态） |
| 版本管理 | 🟢 可用 | snapshot + 字段/章节/行级 diff + rollback + history |
| 评分系统 | 🟢 可用 | drill/review 结构化评分，自动汇总到 Skill metrics |
| 状态机 | 🟢 可用 | 代码级强约束，自动晋升，手动退役/降级 |
| Schema 校验 | 🟢 可用 | Pydantic 校验，`skill-forge validate` 命令可用 |

### 未实现 / 有限实现

| 能力 | 当前状态 | 说明 |
|------|---------|------|
| 自动 LLM 调用 | 需要 API Key | 无 Key 时输出完整 Prompt |
| 向量检索 | ❌ 未实现 | 当前是关键词匹配 |
| Web UI | ❌ 未实现 | 只有 CLI |
| 多人协作 | ❌ 未实现 | 只支持本地 |
| 自动退化监控 | ❌ 未实现 | 需要手动检查 |
| 组织偏好配置 | ❌ 未实现 | 所有 Skill 通用 |
| PII 脱敏 | ⚠️ 提示但不自动 | 需要用户自行处理 |
| 审计日志 | ❌ 未实现 | 无操作记录 |

## 能力边界声明

- **默认不联网**：所有数据存储在本地
- **默认不调用 API**：无 API Key 时输出完整 Prompt
- **不执行外部 Agent/Skill**：仅作为文本解析
- **不保证推荐准确**：推荐基于关键词匹配，需要人工判断
- **不保证话术合规**：生成的话术需要用户自行审核
- **不自动脱敏**：聊天记录可能包含敏感信息，需要用户自行处理

## 快速开始（3 分钟）

### 安装

```bash
git clone https://github.com/zhushidong/skill-forge.git
cd skill-forge
pip install -e .
```

### 配置（可选）

复制示例环境文件并填写你的 API Key：

```bash
cp .env.example .env
# 编辑 .env，填写 OPENAI_API_KEY 和可选的 OPENAI_BASE_URL
```

支持的环境变量：
- `OPENAI_API_KEY`：OpenAI 或兼容服务的 API Key
- `OPENAI_MODEL`：模型名称，默认 `gpt-4.1-mini`
- `OPENAI_BASE_URL`：自定义 API 基础地址（代理/转发服务）

**没有 API Key？** 所有命令会输出完整 Prompt，你可以复制到 ChatGPT、Claude、Kimi 等任意大模型中使用。

### 初始化

```bash
skill-forge init
```

### 体验完整链路

```bash
# 1. 导入一个案例
skill-forge ingest --type case --title "客户嫌贵案例" --file samples/case-price.md

# 2. 把案例转成 Skill
skill-forge distill --material material-20260617-153000 --problem "客户嫌贵怎么应对"

# 3. 演练这个 Skill
skill-forge drill --skill skill-20260617-153000 --persona "预算不足型客户" --rounds 3

# 4. 查看 Skill 状态
skill-forge search
```

**没有 API Key？** 没关系！所有命令会输出完整 Prompt，你可以复制到 ChatGPT、Claude、Kimi 等任意大模型中使用。

## 完整生命周期示例

详见 [golden-lifecycle.md](examples/golden-lifecycle.md)

展示一个 Skill 从原始案例到成熟状态的完整过程：
- 原始案例 → 导入 → 提炼 → 演练 → 状态流转 → 实战复盘 → 版本更新 → 多次实战 → 成熟

## 命令列表

| 命令 | 用途 | 输入 | 输出 |
|------|------|------|------|
| `init` | 初始化目录和模板 | - | 目录结构 + 模板文件 |
| `ingest` | 导入资料 | 文件/文本 | Material |
| `inspect` | 检查外部资产 | 文件 | 分析报告 |
| `melt` | 熔炼外部资产为 Skill | 文件 | Skill 草稿 |
| `distill` | 转资料为 Skill | Material ID | Skill 草稿 |
| `drill` | 演练 Skill | Skill ID | 演练记录 + 自动更新 metrics |
| `review` | 复盘真实沟通 | 文件 + 结果 | 复盘记录 |
| `field-log` | 记录实战结果 | Skill ID + 结果 | 实战日志 + 自动更新 metrics/status |
| `apply-review` | 基于复盘自动迭代 Skill | Review ID + Skill ID | 更新后的 Skill |
| `recommend` | 推荐下一招 | 文件 + 背景 | 推荐记录 |
| `search` | 搜索本地 Skill | 关键词/状态/场景 | Skill 列表 |
| `propose-update` | 生成更新提案 | Skill ID / 自动扫描 | 更新提案 |
| `apply-update` | 应用更新提案 | Proposal ID | 更新指引 |
| `promote` | 手动/自动晋升 Skill 状态 | Skill ID + 目标状态 | 状态变更 |
| `history` | 查看 Skill 版本历史 | Skill ID | 版本列表 |
| `diff` | 对比两个版本 | Skill ID + 版本 | 字段/章节/行级差异 |
| `rollback` | 回滚到历史版本 | Skill ID + 版本 | 回滚后的 Skill |
| `validate` | 校验文件格式 | 文件路径 | 校验结果 |

## Skill 状态机

```
draft → trained → tested → mature → retired
```

### 状态流转规则

| 流转 | 条件 |
|------|------|
| draft → trained | 完成 3 次 drill，平均分 >= 60 |
| trained → tested | 完成 1 次 field-log/review |
| tested → mature | field_tests >= 5，胜率 >= 60%，平均分 >= 70 |
| mature → retired | 手动退役（当前不自动触发） |
| 任意 → retired | 允许手动退役 |
| retired → 任意 | 不允许，需新建 Skill |

详见 [skill-schema.md](examples/skill-schema.md)

## 评分系统

### Drill 评分（0-100）

| 维度 | 权重 | 说明 |
|------|------|------|
| diagnosis | 25% | 是否准确识别客户问题 |
| response_quality | 25% | 回应质量和话术水平 |
| next_step_control | 25% | 是否推进到下一步 |
| risk_control | 25% | 是否避免禁用行为 |

### Review 评分（0-100）

| 维度 | 权重 | 说明 |
|------|------|------|
| adherence | 30% | 是否遵循 Skill 步骤 |
| outcome | 30% | 最终结果 |
| improvement | 20% | 相比上次是否有进步 |
| skill_defect | 20% | Skill 本身的缺陷 |

详见 [scoring-rubric.md](examples/scoring-rubric.md)

## 和同类项目对比

| 类型 | 代表项目 | 解决问题 | Skill Forge 差异 |
|------|---------|---------|-----------------|
| Prompt 管理 | PromptLayer / PromptForge | Prompt 版本与评估 | Skill Forge 更偏业务经验结构化 |
| Agent Skill | Claude Code Skills | 工具能力封装 | Skill Forge 更偏销售/客服话术与演练 |
| Workflow | Dify / LangGraph | 应用流程编排 | Skill Forge 更轻量、本地优先 |
| 知识库 | Notion / 飞书文档 | 存储知识 | Skill Forge 强调演练、复盘、推荐 |
| CRM 辅助 | Gong / Chorus | 销售对话分析 | Skill Forge 更偏开源、本地、可定制 |

详见 [comparison.md](examples/comparison.md)

## 项目结构

```
skill-forge/
├── skill_forge/           # 核心代码
│   ├── cli.py            # CLI 入口
│   ├── commands/         # 命令实现
│   ├── adapters/         # 适配器
│   ├── storage.py        # 存储层
│   ├── llm.py            # LLM 调用
│   ├── templates.py      # 模板渲染
│   └── validation.py     # Schema 校验
├── templates/            # Prompt 模板
├── samples/              # 示例文件
├── examples/             # 文档和示例
├── tests/                # 测试
└── data/                 # 用户数据（gitignore）
```

## 测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 生成覆盖率报告
python -m pytest tests/ --cov=skill_forge --cov-report=term-missing
```

完整测试套件覆盖：
- 路径验证与存储安全
- LLM 输入/输出净化与错误脱敏
- Pydantic Schema 校验
- 自动晋升/手动晋升状态机
- 版本 diff（字段/章节/行级）
- 适配器路由与外部文件解析
- 应用复盘自动迭代
- 多维度搜索与推荐
- 实战日志指标回写

## 路线图

### v0.2：质量标准 ✅

- [x] `skill-forge validate`：Skill 格式校验
- [x] 状态流转规则自动执行
- [ ] `skill-forge score`：Skill 健康度评分
- [ ] 失败原因分类

### v0.3：推荐增强 ✅

- [x] 推荐解释输出
- [x] 多 Skill 排序
- [x] 使用反馈记录
- [ ] 不推荐机制

### v0.4：版本管理 ✅

- [x] Skill 版本历史
- [x] `skill-forge diff`：版本对比
- [x] `skill-forge history`：变更历史
- [x] `skill-forge rollback`：版本回滚

### v0.5：业务样例库

- [x] 1 个完整销售链路示例
- [ ] 10 个销售场景
- [ ] 5 个客服场景
- [ ] 5 个培训场景

## 贡献

欢迎提交 Issue 和 Pull Request！

## License

[MIT](LICENSE)
