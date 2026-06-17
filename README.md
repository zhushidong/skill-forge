# Skill Forge

商业 Skill 炼丹炉 - 把资料、客户对话、外部 Agent/Prompt/Skill 熔炼成可演练、可复盘、可推荐的商业 Skill。

## 安装

```bash
cd skill-forge
pip install -e .
```

## 初始化

```bash
skill-forge init
```

## 配置 LLM

创建 `.env` 文件：

```
OPENAI_API_KEY=你的key
OPENAI_MODEL=gpt-4.1-mini
```

如果没有 key，也可以使用复制 Prompt 模式（所有命令在无 API Key 时会输出完整 Prompt）。

## 命令列表

| 命令 | 用途 |
|------|------|
| `init` | 初始化目录和模板 |
| `ingest` | 导入资料 |
| `inspect` | 检查外部资产 |
| `melt` | 熔炼外部资产为 Skill |
| `distill` | 转资料为 Skill |
| `drill` | 演练 Skill |
| `review` | 复盘真实沟通 |
| `recommend` | 推荐下一招 |
| `search` | 搜索本地 Skill |
| `propose-update` | 生成 Skill 更新提案 |
| `apply-update` | 应用更新提案 |

## 基础链路

### 1. 导入资料

```bash
skill-forge ingest --type case --title "客户嫌贵案例" --file ./samples/case-price.md
```

### 2. 转成 Skill

```bash
skill-forge distill --material material-xxx --problem "客户嫌贵怎么应对"
```

### 3. 演练

```bash
skill-forge drill --skill skill-xxx --persona "预算不足型客户" --rounds 5
```

### 4. 复盘

```bash
skill-forge review --file ./samples/current-chat.md --result "推进" --skill skill-xxx
```

### 5. 推荐

```bash
skill-forge recommend --file ./samples/current-chat.md --context "产品是999元课程，客户来自小红书"
```

## 搜索 Skill

```bash
# 列出所有 Skill
skill-forge search

# 按关键词搜索
skill-forge search --query "价格"

# 按状态筛选
skill-forge search --status draft
```

## 更新 Skill

```bash
# 生成更新提案
skill-forge propose-update --skill skill-xxx --reason "演练中发现需要更多场景"

# 查看提案后，应用更新（需手动编辑）
skill-forge apply-update --proposal proposal-xxx
```

## 外部 Agent 熔炼链路

### 1. 检查

```bash
skill-forge inspect --file ./samples/external-agent.md --type auto
```

### 2. 熔炼

```bash
skill-forge melt --file ./samples/external-agent.md --type agent --target-scene "客户异议处理"
```

### 3. 演练

```bash
skill-forge drill --skill skill-xxx --persona "对比竞品型客户"
```

## 完整链路示例

```
1. skill-forge init
2. skill-forge ingest --type case --title "客户嫌贵推进案例" --file samples/case-price.md --note "用于提炼价格异议处理"
3. skill-forge distill --material material-xxx --problem "客户嫌贵怎么应对"
4. skill-forge drill --skill skill-xxx --persona "预算不足型客户" --rounds 3
5. skill-forge review --file samples/current-chat.md --result "推进" --skill skill-xxx
6. skill-forge recommend --file samples/current-chat.md --context "产品是999元课程，客户来自小红书"
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

## 产品原则

- 不欺骗客户
- 不编造案例
- 不制造虚假稀缺
- 不诱导明显不适合的人购买
- 优先理解客户真实需求
- 让人和 Agent 一起变强

## 后续路线图

- Skill 版本 diff
- MCP/Agent 调用接口
- Web UI
- 向量检索
- 多模型支持
