# Skill 输出格式规范

## 文件格式

每个 Skill 是一个 Markdown 文件，包含 YAML Front Matter 和正文。

## YAML Front Matter Schema

```yaml
---
# 必填字段
id: string                    # 唯一标识符，格式: skill-YYYYMMDD-HHMMSS
name: string                  # Skill 名称，1-200 字符
version: int                  # 版本号，从 1 开始
status: string                # 状态: draft | trained | tested | mature | retired

# 可选字段
scenes: list[string]          # 适用场景列表
signals: list[string]         # 触发信号列表（关键词）
customer_types: list[string]  # 目标客户类型
customer_stages: list[string] # 目标客户阶段
avoid_when: list[string]      # 不适用场景

# 指标字段（系统自动维护）
drills: int                   # 演练次数
field_tests: int              # 实战次数
wins: int                     # 胜利次数
losses: int                   # 失败次数

# 时间字段
created_at: string            # 创建时间，ISO 8601 格式
trained_at: string            # 训练时间
tested_at: string             # 测试时间
updated_at: string            # 更新时间
---
```

## 字段说明

### 必填字段

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `id` | string | 唯一标识符 | `skill-20260617-153000` |
| `name` | string | Skill 名称 | `价格异议处理` |
| `version` | int | 版本号 | `1` |
| `status` | string | 状态 | `draft` |

### 可选字段

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `scenes` | list | 适用场景 | `["客户说太贵", "预算不足"]` |
| `signals` | list | 触发信号 | `["价格", "贵", "预算"]` |
| `customer_types` | list | 客户类型 | `["价格敏感型", "预算有限型"]` |
| `customer_stages` | list | 客户阶段 | `["异议处理", "成交阶段"]` |
| `avoid_when` | list | 不适用场景 | `["客户已决定购买"]` |

### 指标字段

| 字段 | 类型 | 说明 | 自动更新 |
|------|------|------|---------|
| `drills` | int | 演练次数 | ✅ drill 命令 |
| `field_tests` | int | 实战次数 | ✅ review 命令 |
| `wins` | int | 胜利次数 | ✅ review 命令 |
| `losses` | int | 失败次数 | ✅ review 命令 |

### 时间字段

| 字段 | 格式 | 说明 |
|------|------|------|
| `created_at` | ISO 8601 | `2026-06-17T15:30:00` |
| `trained_at` | ISO 8601 | 首次 drill 时间 |
| `tested_at` | ISO 8601 | 首次 review 时间 |
| `updated_at` | ISO 8601 | 最近更新时间 |

## 正文格式

```markdown
# Skill 名称

## 解决的问题
描述这个 Skill 解决什么问题。

## 信号识别
当遇到以下场景时，激活此 Skill：
- 场景 1
- 场景 2

## 执行步骤

### 步骤 1：xxx
具体操作说明。

### 步骤 2：xxx
具体操作说明。

## 核心原则
1. 原则 1
2. 原则 2

## 验证方式
- 如何验证这个 Skill 有效
```

## 状态流转

```
draft → trained → tested → mature → retired
```

| 状态 | 条件 | 说明 |
|------|------|------|
| `draft` | 初始状态 | 草稿，未演练 |
| `trained` | drills >= 3 | 经过至少 3 次演练 |
| `tested` | field_tests >= 1 | 经过至少 1 次实战 |
| `mature` | field_tests >= 5 且 wins/field_tests >= 60% | 多次实战有效 |
| `retired` | 手动设置 | 过时或效果差 |

## 示例

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
created_at: 2026-06-17T15:30:00
trained_at: 2026-06-17T16:00:00
tested_at: 2026-06-17T17:00:00
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

### 步骤 1：认同顾虑
"我理解您的顾虑，价格确实是一个重要考虑因素。"

### 步骤 2：了解真实预算
"您理想的预算是多少？我可以帮您看看有没有合适的方案。"

### 步骤 3：展示价值
"这个方案可以帮助您 [具体价值]，平均下来每天只需要 [金额]。"

### 步骤 4：提供选项
"我们还有分期付款/套餐方案，可以减轻一次性支付的压力。"

## 核心原则
1. 先认同，再引导
2. 展示价值，而非降价
3. 提供选项，而非强迫选择

## 验证方式
- 客户是否继续对话
- 客户是否询问更多细节
- 最终是否成交
```
