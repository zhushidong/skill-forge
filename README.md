# Skill Forge

面向销售、客服、培训团队的商业经验结构化工具。

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-49%20passed-brightgreen.svg)](#测试)

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

## 解决什么问题？

**问题**：销售/客服团队有大量经验（聊天记录、案例、培训材料），但这些经验：
- 散落在各处，无法复用
- 只在老员工脑子里，难以传承
- 遇到新客户场景时，不知道该用哪招
- 培训新人靠"师父带"，效率低、质量不稳定

**解决方案**：Skill Forge 把这些散落的经验"结构化"成标准 Skill，通过演练和复盘持续改进。

## 当前能力边界

### 已实现

| 能力 | 说明 | 状态 |
|------|------|------|
| 案例导入 | 把 Markdown/JSON/YAML 导入为材料 | ✅ 可用 |
| Skill 提炼 | 把材料转成结构化 Skill | ✅ 可用 |
| 演练（Drill） | 模拟客户场景演练 Skill | ✅ 可用 |
| 复盘（Review） | 分析真实对话并给出改进建议 | ✅ 可用 |
| 推荐（Recommend） | 根据对话推荐合适的 Skill | ✅ 可用 |
| 搜索（Search） | 按关键词/状态搜索 Skill | ✅ 可用 |
| 版本管理 | Skill 版本号和变更记录 | ✅ 可用 |
| 评分系统 | drill/review/recommend 评分 | ✅ 可用 |
| 状态机 | draft→trained→tested→mature→retired | ✅ 可用 |
| Schema 校验 | Skill 格式校验 | ✅ 可用 |

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
| `drill` | 演练 Skill | Skill ID | 演练记录 |
| `review` | 复盘真实沟通 | 文件 + 结果 | 复盘记录 |
| `recommend` | 推荐下一招 | 文件 + 背景 | 推荐记录 |
| `search` | 搜索本地 Skill | 关键词 | Skill 列表 |
| `propose-update` | 生成更新提案 | Skill ID | 更新提案 |
| `apply-update` | 应用更新提案 | Proposal ID | 更新指引 |

## Skill 状态机

```
draft → trained → tested → mature → retired
```

### 状态流转规则

| 流转 | 条件 |
|------|------|
| draft → trained | 完成 3 次 drill，平均分 >= 60 |
| trained → tested | 完成 1 次真实 review，结果为"推进" |
| tested → mature | field_tests >= 5，胜率 >= 60%，平均分 >= 70 |
| mature → retired | 90 天无使用 或 3/5 次失败 或 手动退役 |

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

当前 49 个测试全部通过，覆盖：
- 路径验证
- 文件大小限制
- LLM 输入/输出净化
- 错误信息脱敏
- Pydantic Schema 校验

## 路线图

### v0.2：质量标准

- [ ] `skill-forge validate`：Skill 格式校验
- [ ] `skill-forge score`：Skill 健康度评分
- [ ] 状态流转规则自动执行
- [ ] 失败原因分类

### v0.3：推荐增强

- [ ] 推荐解释输出
- [ ] 多 Skill 排序
- [ ] 不推荐机制
- [ ] 使用反馈记录

### v0.4：版本管理

- [ ] Skill 版本历史
- [ ] `skill-forge diff`：版本对比
- [ ] `skill-forge history`：变更历史
- [ ] `skill-forge rollback`：版本回滚

### v0.5：业务样例库

- [ ] 10 个销售场景
- [ ] 5 个客服场景
- [ ] 5 个培训场景
- [ ] 每个场景完整链路

## 贡献

欢迎提交 Issue 和 Pull Request！

## License

[MIT](LICENSE)
