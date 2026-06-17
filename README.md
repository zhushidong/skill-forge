# Skill Forge

商业 Skill 炼丹炉 - 把资料、客户对话、外部 Agent/Prompt/Skill 熔炼成可演练、可复盘、可推荐的商业 Skill。

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 功能特点

- **11 个 CLI 命令**：完整的 Skill 生命周期管理
- **5 个适配器**：支持 Markdown、JSON、YAML、Prompt、外部 Agent
- **6 个模板**：inspect、melt、distill、drill、review、recommend
- **安全特性**：路径验证、LLM 输入净化、原子读取、模板注入防护
- **无 API Key 也能用**：自动生成完整 Prompt，复制到任意大模型使用

## 快速开始

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

### 配置 LLM（可选）

创建 `.env` 文件：

```
OPENAI_API_KEY=你的key
OPENAI_MODEL=gpt-4.1-mini
```

如果没有 key，所有命令会输出完整 Prompt，你可以复制到 ChatGPT、Claude、Kimi 等任意大模型中使用。

## 命令列表

| 命令 | 用途 | 示例 |
|------|------|------|
| `init` | 初始化目录和模板 | `skill-forge init` |
| `ingest` | 导入资料 | `skill-forge ingest --type case --title "客户嫌贵" --file ./case.md` |
| `inspect` | 检查外部资产 | `skill-forge inspect --file ./agent.md --type auto` |
| `melt` | 熔炼外部资产为 Skill | `skill-forge melt --file ./agent.md --type agent` |
| `distill` | 转资料为 Skill | `skill-forge distill --material material-xxx --problem "客户嫌贵"` |
| `drill` | 演练 Skill | `skill-forge drill --skill skill-xxx --persona "预算不足型"` |
| `review` | 复盘真实沟通 | `skill-forge review --file ./chat.md --result "推进"` |
| `recommend` | 推荐下一招 | `skill-forge recommend --file ./chat.md` |
| `search` | 搜索本地 Skill | `skill-forge search --query "价格"` |
| `propose-update` | 生成更新提案 | `skill-forge propose-update --skill skill-xxx` |
| `apply-update` | 应用更新提案 | `skill-forge apply-update --proposal proposal-xxx` |

## 完整链路示例

```bash
# 1. 初始化
skill-forge init

# 2. 导入案例
skill-forge ingest --type case --title "客户嫌贵推进案例" --file samples/case-price.md

# 3. 转成 Skill
skill-forge distill --material material-xxx --problem "客户嫌贵怎么应对"

# 4. 演练
skill-forge drill --skill skill-xxx --persona "预算不足型客户" --rounds 3

# 5. 复盘
skill-forge review --file samples/current-chat.md --result "推进" --skill skill-xxx

# 6. 推荐
skill-forge recommend --file samples/current-chat.md --context "产品是999元课程"
```

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

## 安全特性

- **路径验证**：防止目录遍历攻击
- **LLM 输入净化**：防止 Prompt 注入
- **原子读取**：防止 TOCTOU 竞态条件
- **模板注入防护**：防止模板语法注入
- **错误信息脱敏**：防止敏感信息泄露

## 产品原则

- 不欺骗客户
- 不编造案例
- 不制造虚假稀缺
- 不诱导明显不适合的人购买
- 优先理解客户真实需求
- 让人和 Agent 一起变强

## 路线图

- [ ] Skill 版本 diff
- [ ] MCP/Agent 调用接口
- [ ] Web UI
- [ ] 向量检索
- [ ] 多模型支持

## 贡献

欢迎提交 Issue 和 Pull Request！

## License

[MIT](LICENSE)
