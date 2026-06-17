# Skill Forge

商业 Skill 炼丹炉 - 把资料、客户对话、外部 Agent/Prompt/Skill 熔炼成可演练、可复盘、可推荐的商业 Skill。

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-49%20passed-brightgreen.svg)](#测试)

## 解决什么问题？

**问题**：销售/客服团队有大量经验（聊天记录、案例、培训材料），但这些经验：
- 散落在各处，无法复用
- 只在老员工脑子里，难以传承
- 遇到新客户场景时，不知道该用哪招
- 培训新人靠"师父带"，效率低、质量不稳定

**解决方案**：Skill Forge 把这些散落的经验"熔炼"成标准化的 Skill，每个 Skill 是一个：
- **可训练的**：通过演练（drill）不断优化
- **可复盘的**：每次真实使用后复盘效果
- **可推荐的**：根据当前客户对话，自动推荐最合适的 Skill

## 适合谁？

- **销售团队**：把成功案例提炼成可复用的销售技巧
- **客服团队**：把常见问题处理流程标准化
- **培训部门**：用 Skill 演练替代传统培训
- **个人创业者**：把自己的经验产品化

## 和同类项目有什么不同？

| 特性 | Skill Forge | PromptForge | Sklm | skills-management |
|------|-------------|-------------|------|-------------------|
| **核心目标** | 商业 Skill 管理 | Prompt 版本控制 | AI Agent 管理 | 符号链接管理 |
| **输出格式** | Markdown + YAML | JSON | 多格式 | 符号链接 |
| **演练机制** | ✅ 回合制演练 | ❌ | ❌ | ❌ |
| **复盘系统** | ✅ 真实沟通复盘 | ❌ | ❌ | ❌ |
| **推荐引擎** | ✅ 基于对话推荐 | ❌ | ❌ | ❌ |
| **状态机** | ✅ draft→trained→tested→mature | ❌ | ❌ | ❌ |
| **无 API Key 使用** | ✅ 输出完整 Prompt | ❌ | ❌ | ❌ |
| **安全审计** | ✅ 3 轮攻防修复 | ❌ | ❌ | ❌ |

**核心差异**：Skill Forge 不只是"生成 Prompt"，而是构建一个完整的**商业 Skill 生命周期管理系统**。

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

## 输入/输出格式

### 输入

| 类型 | 格式 | 示例 |
|------|------|------|
| 案例 | Markdown | `samples/case-price.md` |
| 聊天记录 | Markdown | `samples/current-chat.md` |
| 外部 Agent | Markdown/JSON/YAML | `samples/external-agent.md` |
| 外部 Skill | JSON | `samples/external-skill.json` |

### 输出

| 类型 | 格式 | 位置 |
|------|------|------|
| Skill | Markdown + YAML | `data/skills/draft/` |
| 演练记录 | Markdown + YAML | `data/drills/` |
| 复盘记录 | Markdown + YAML | `data/reviews/` |
| 推荐记录 | Markdown + YAML | `data/recommendations/` |

### Skill 输出格式

```markdown
---
id: skill-20260617-153000
name: 价格异议处理
version: 1
status: trained
scenes:
  - 客户说太贵
  - 预算不足
signals:
  - 价格
  - 贵
  - 预算
customer_types:
  - 价格敏感型客户
drills: 3
field_tests: 2
wins: 2
losses: 0
---

# 价格异议处理 Skill

## 解决的问题
客户以"太贵了"为由拒绝购买时，如何有效回应。

## 信号识别
当客户说出以下关键词时，激活此 Skill：
- "太贵了"
- "预算不够"
- "能不能便宜点"

## 执行步骤
1. 先认同客户的顾虑
2. 了解客户的真实预算
3. 展示价值而非降价
4. 提供分期/套餐选项
```

## 安全特性

- **路径验证**：防止目录遍历攻击
- **LLM 输入净化**：防止 Prompt 注入（Unicode NFKC 标准化 + 零宽字符剥离）
- **原子读取**：防止 TOCTOU 竞态条件
- **模板注入防护**：防止模板语法注入
- **错误信息脱敏**：防止敏感信息泄露

经过 3 轮沙盘攻防测试，修复了 15+ 个安全漏洞。

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

- `draft`: 草稿，未演练
- `trained`: 经过至少 3 次 drill
- `tested`: 经过至少 1 次真实 review
- `mature`: 多次实战有效（胜率 > 60%）
- `retired`: 过时或效果差

系统会自动根据 drill/review 次数和结果更新状态。

## 产品原则

- 不欺骗客户
- 不编造案例
- 不制造虚假稀缺
- 不诱导明显不适合的人购买
- 优先理解客户真实需求
- 让人和 Agent 一起变强

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

- [ ] Skill 版本 diff
- [ ] MCP/Agent 调用接口
- [ ] Web UI
- [ ] 向量检索
- [ ] 多模型支持
- [ ] CI/CD 自动化测试

## 贡献

欢迎提交 Issue 和 Pull Request！

## License

[MIT](LICENSE)
