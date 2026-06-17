# Skill Schema 规范

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

## YAML Front Matter Schema

```yaml
---
# === 必填字段 ===
id: string                    # 唯一标识符，格式: skill-YYYYMMDD-HHMMSS
name: string                  # Skill 名称，1-200 字符
version: string               # 语义化版本号，格式: major.minor.patch
status: draft | trained | tested | mature | retired
domain: string                # 业务领域: sales | support | training | other
problem: string               # 解决的核心问题，一句话描述

# === 适用场景 ===
applicable_scenarios:         # 适用场景列表
  - string
not_applicable_scenarios:     # 不适用场景列表
  - string

# === 客户信号 ===
customer_signals:             # 触发此 Skill 的客户关键词/行为
  - string

# === 应对策略 ===
strategy:
  name: string                # 策略名称
  steps:                      # 执行步骤
    - step: int               # 步骤序号
      action: string          # 具体动作
      script: string          # 示例话术（可选）
      risk: string            # 风险提示（可选）

# === 禁用行为 ===
forbidden_behaviors:          # 绝对不能做的事
  - string

# === 版本信息 ===
parent_version: string        # 上一版本号（可选）
change_type: major | minor | patch | initial
change_reason: string         # 变更原因（可选）
changed_by: string            # 变更来源: drill-xxx | review-xxx | manual

# === 证据链 ===
evidence:
  source_materials:           # 来源材料 ID
    - string
  drill_records:              # 演练记录 ID
    - string
  review_records:             # 复盘记录 ID
    - string

# === 指标（系统自动维护）===
metrics:
  drills: int                 # 演练次数
  field_tests: int            # 实战次数
  wins: int                   # 胜利次数
  losses: int                 # 失败次数
  avg_score: float            # 平均评分（0-100）
  last_used_at: string        # 最近使用时间

# === 时间字段 ===
created_at: string            # 创建时间，ISO 8601
updated_at: string            # 更新时间，ISO 8601
trained_at: string            # 首次训练时间
tested_at: string             # 首次实战时间
mature_at: string             # 达到成熟时间
retired_at: string            # 退役时间
---
```

## 正文结构

```markdown
# Skill 名称

## 解决的问题
[一句话描述核心问题]

## 信号识别
当遇到以下场景时，激活此 Skill：
- [信号 1]
- [信号 2]

## 执行步骤

### 步骤 1：[步骤名称]
[具体操作说明]

**示例话术：**
> "[话术内容]"

**风险提示：**
> [风险说明]

### 步骤 2：[步骤名称]
...

## 禁用行为
- [绝对不能做的事 1]
- [绝对不能做的事 2]

## 验证方式
- [如何验证这个 Skill 有效]
```

## 生命周期流转规则

### draft → trained

**触发条件**（必须全部满足）：

1. 通过 schema 校验（所有必填字段完整）
2. 完成至少 3 轮 drill
3. drill 平均分 >= 60
4. 没有未解决的高危安全问题
5. `applicable_scenarios` 至少有 1 个
6. `customer_signals` 至少有 1 个
7. `forbidden_behaviors` 至少有 1 个

**自动流转**：系统检测到条件满足时自动流转

### trained → tested

**触发条件**（必须全部满足）：

1. 至少被 1 次真实对话复盘（review）
2. review 结果为"推进"或"成交"
3. `evidence.review_records` 至少有 1 条
4. 有版本记录

**自动流转**：系统检测到条件满足时自动流转

### tested → mature

**触发条件**（必须全部满足）：

1. field_tests >= 5
2. wins / field_tests >= 0.6（胜率 60%）
3. 近 3 次 review 没有"严重失败"
4. `metrics.avg_score` >= 70

**自动流转**：系统检测到条件满足时自动流转

### mature → retired

**触发条件**（满足任一）：

1. 连续 90 天无使用
2. 近 5 次 review 中 3 次以上"失败"
3. 被新版本 Skill 替代（`parent_version` 指向此版本）
4. 手动标记

**手动触发**：`skill-forge retire --skill <id> --reason "原因"`

### 降级机制

任何状态都可以手动降级：

```bash
# 从 mature 降级到 tested（需要重新验证）
skill-forge demote --skill <id> --to tested --reason "策略变更需重新验证"

# 从 trained 降级到 draft（需要重新演练）
skill-forge demote --skill <id> --to draft --reason "发现重大缺陷"
```

## 评分维度

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
| outcome | 30% | 最终结果（推进/成交/流失） |
| improvement | 20% | 相比上次是否有进步 |
| skill_defect | 20% | Skill 本身的缺陷（越低越好） |

### Recommend 评分

| 维度 | 说明 |
|------|------|
| relevance | 推荐 Skill 与当前场景的相关度 |
| confidence | 推荐置信度（0-1） |
| risk_warning | 是否包含风险提醒 |
| explanation | 推荐理由是否清晰 |

## Skill 缺陷类型

| 类型 | 说明 | 修复方式 |
|------|------|---------|
| missing_scenario | 缺少适用场景 | 补充 applicable_scenarios |
| missing_signal | 缺少客户信号 | 补充 customer_signals |
| weak_steps | 步骤不够具体 | 细化 strategy.steps |
| no_forbidden | 缺少禁用行为 | 补充 forbidden_behaviors |
| wrong_order | 步骤顺序错误 | 调整 steps 顺序 |
| incomplete_script | 缺少示例话术 | 补充 script 字段 |
| no_risk_warning | 缺少风险提示 | 补充 risk 字段 |
| outdated | 内容过时 | 更新版本 |
