# Skill 输出格式规范

## 文件格式

每个 Skill 是一个 Markdown 文件，包含 YAML Front Matter 和正文。

## YAML Front Matter Schema

```yaml
---
# 必填字段
id: string                    # 唯一标识符，格式: skill-YYYYMMDD-HHMMSS
name: string                  # Skill 名称，1-200 字符
version: string               # 语义化版本号，如 "1.0.0"
status: string                # 状态: draft | trained | tested | mature | retired

# 分类字段
domain: string                # 领域: sales | customer_service | training | other
category: string              # 自定义分类标签
problem: string               # 解决的具体问题
goal: string                  # 该 Skill 要达到的目标

# 客户画像（多维度匹配）
customer_types: list[string]  # 目标客户类型，如 ["中小企业主", "采购负责人"]
customer_stages: list[string] # 目标客户阶段，如 ["方案评估", "价格谈判"]

# 场景与信号
applicable_scenarios: list[string]  # 适用场景
not_applicable_scenarios: list[string] # 不适用场景
customer_signals: list[string]      # 触发此 Skill 的客户关键词/行为

# 策略（四维度评估）
strategy:
  name: string                # 策略名称
  diagnosis: string           # 诊断原则
  response_quality: string    # 回应质量原则
  next_step_control: string   # 推进原则
  risk_control: string        # 风险控制原则
  steps: list[dict]           # 执行步骤（旧格式兼容）

# 执行内容
steps: list[string]           # 执行步骤列表
example_lines: list[string]   # 示例话术
drill_personas: list[string]  # 演练客户人格

# 禁用行为
forbidden_behaviors: list[string]   # 禁止的行为

# 版本链（系统维护）
parent_version: string        # 父版本号
supersedes: string            # 取代的旧 Skill ID
superseded_by: string         # 被哪个新 Skill 取代
inherited_metrics: bool       # 是否继承旧版指标
change_type: string           # initial | major | minor | patch | rollback
change_reason: string         # 变更原因
changed_by: string            # 变更来源（review ID / manual）

# 证据链（系统维护）
evidence:
  source_materials: list[string]  # 来源材料 ID 列表
  drill_records: list[string]     # 演练记录 ID 列表
  review_records: list[string]    # 复盘记录 ID 列表

# 指标（系统自动维护，嵌套结构）
metrics:
  drills: int                  # 演练次数
  field_tests: int             # 实战次数
  wins: int                    # 胜利次数
  losses: int                  # 失败次数
  avg_score: float             # 平均评分（0-100）
  last_used_at: string         # 最近使用时间

# 时间字段（系统维护）
created_at: string             # 创建时间，ISO 8601
trained_at: string             # 首次达到 trained 时间
tested_at: string              # 首次达到 tested 时间
mature_at: string              # 首次达到 mature 时间
retired_at: string             # 退役时间
updated_at: string             # 最近更新时间
---
```

## 字段说明

### 必填字段

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `id` | string | 唯一标识符 | `skill-20260617-153000` |
| `name` | string | Skill 名称 | `价格异议处理` |
| `version` | string | 语义化版本号 | `1.0.0` |
| `status` | string | 状态 | `draft` |

### 分类与定位

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `domain` | string | 领域 | `sales` |
| `category` | string | 自定义分类 | `价格谈判` |
| `problem` | string | 解决的问题 | `客户嫌贵怎么应对` |
| `goal` | string | 策略目标 | `把焦点从价格转移到价值` |

### 场景与信号

| 字段 | 类型 | 说明 |
|------|------|------|
| `applicable_scenarios` | list | 适用场景 |
| `not_applicable_scenarios` | list | 不适用场景 |
| `customer_signals` | list | 触发信号（关键词/行为） |
| `customer_types` | list | 目标客户类型 |
| `customer_stages` | list | 目标客户阶段 |

### 策略与指标（嵌套，系统维护）

| 字段 | 类型 | 说明 |
|------|------|------|
| `strategy.diagnosis` | string | 诊断原则 |
| `strategy.response_quality` | string | 回应质量原则 |
| `strategy.next_step_control` | string | 推进原则 |
| `strategy.risk_control` | string | 风险控制原则 |
| `metrics.drills` | int | 演练次数 |
| `metrics.field_tests` | int | 实战次数 |
| `metrics.wins` | int | 胜利次数 |
| `metrics.losses` | int | 失败次数 |
| `metrics.avg_score` | float | 平均评分（0-100） |

## 状态流转

```
draft → trained → tested → mature → retired
```

| 状态 | 条件 | 说明 |
|------|------|------|
| `draft` | 初始状态 | 草稿，未演练 |
| `trained` | drills >= 3 且 avg_score >= 60 | 经过至少 3 次演练且平均分达标 |
| `tested` | field_tests >= 1 | 经过至少 1 次实战 |
| `mature` | field_tests >= 5 且 win_rate >= 60% 且 avg_score >= 70 | 多次实战有效 |
| `retired` | 手动设置 | 过时或效果差 |

## 示例

```markdown
---
id: skill-price-objection-v1
name: 价格异议处理
version: 1.0.0
status: trained
domain: sales
category: 价格谈判
problem: 客户以"太贵了"为由拒绝购买时如何有效回应
goal: 在维护价格体系的前提下，把对话焦点从"价格"转移到"价值"
customer_types:
  - 中小企业主
  - 采购负责人
customer_stages:
  - 方案评估
  - 价格谈判
applicable_scenarios:
  - 客户说太贵
  - 客户拿竞品压价
  - 客户要求打折才签约
not_applicable_scenarios:
  - 客户已明确无需求
customer_signals:
  - "价格"
  - "太贵了"
  - "预算不够"
  - "能不能便宜点"
strategy:
  name: 价值重构法
  diagnosis: 区分客户是预算不足、价值认知不足还是谈判策略
  response_quality: 使用"确认-重构-量化-推进"四步话术
  next_step_control: 每次回应都争取一个明确下一步
  risk_control: 不主动降价，不承诺未授权条件
steps:
  - 确认客户真实顾虑
  - 重构比较维度到总拥有成本
  - 量化隐藏风险
  - 给出推进选项（如试点）
example_lines:
  - "我理解您的顾虑，价格确实重要。除了首年报价，还有哪些成本会影响您的总投入？"
  - "过去 6 个月选择我们的客户，平均把故障停机时间从 8 小时降到了 1 小时。"
forbidden_behaviors:
  - 直接降价
  - 贬低竞品
  - 空泛说"一分钱一分货"
evidence:
  source_materials:
    - material-20260617-153000
  drill_records: []
  review_records: []
metrics:
  drills: 3
  field_tests: 2
  wins: 2
  losses: 0
  avg_score: 77.9
  last_used_at: "2026-06-17T20:00:00"
created_at: "2026-06-17T15:30:00"
trained_at: "2026-06-17T16:30:00"
updated_at: "2026-06-17T20:00:00"
---

# 价格异议处理 Skill

## 解决的问题
客户以"太贵了"为由拒绝购买时，如何有效回应。

## 执行步骤

### 步骤 1：确认顾虑
"您说的贵，是指一次性投入超出预算，还是和竞品对比后觉得不值？"

### 步骤 2：重构比较
"除了价格，您评估方案时还会看哪些成本？"

### 步骤 3：量化风险
用具体数字把隐藏风险显性化，如宕机成本、实施周期等。

### 步骤 4：推进试点
"为了让您降低决策风险，建议先启动一个 14 天试点。"

## 禁用行为
- 未经审批直接降价
- 贬低竞品
- 空泛地说"一分钱一分货"
```
