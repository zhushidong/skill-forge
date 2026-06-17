# Golden Lifecycle 示例：客户价格异议处理

本文档展示一个 Skill 从原始案例到成熟状态的完整生命周期。

---

## 阶段 1：原始案例

### 文件：samples/case-price.md

```markdown
# 客户嫌贵案例

## 背景
客户：张总，中小企业老板
产品：999元线上课程
来源：小红书广告

## 对话记录

销售：张总您好，看了我们的课程介绍，感觉怎么样？

客户：内容还行，就是价格有点贵。

销售：这个课程是999元，包含30节视频课+1年社群答疑+3次1v1咨询。

客户：我知道，但是999对我们小公司来说还是有点压力。人家XXX的课才299。

销售：张总，您不能这么比。299的课只有视频，没有答疑和咨询。我们这个是全套服务。

客户：但是299的也能学啊，反正都是那些内容。

销售：张总，这个不一样的。我们的课程是实战派，学完就能用。299那个是理论派，学了还是不会用。

客户：你说的有道理，但是我还是觉得贵。

销售：那这样，我给您申请一个优惠，899行不行？

客户：899...还是有点贵。

销售：那我再给您减100，799，这已经是最低价了。

客户：我再考虑考虑吧。

## 结果
客户流失，未成交。
```

---

## 阶段 2：导入案例

### 命令

```bash
skill-forge ingest --type case --title "客户价格异议-小企业老板" --file samples/case-price.md --note "用于提炼价格异议处理Skill"
```

### 输出

```
导入成功：
  - ID: material-20260617-153000
  - 类型: case
  - 标题: 客户价格异议-小企业老板
  - 路径: data/materials/cases/material-20260617-153000.md
```

---

## 阶段 3：提炼 Skill（v0.1.0）

### 命令

```bash
skill-forge distill --material material-20260617-153000 --problem "客户嫌贵怎么应对" --title "价格异议处理-价值重构法"
```

### 生成的 Skill（v0.1.0）

```markdown
---
id: skill-20260617-153000
name: 价格异议处理-价值重构法
version: 1.0.0
status: draft
domain: sales
problem: 客户以"太贵了"为由拒绝购买
applicable_scenarios:
  - 客户明确表达价格超出预算
  - 客户拿竞品低价压价
not_applicable_scenarios:
  - 客户已明确无需求
  - 客户只是随口说贵
customer_signals:
  - "太贵了"
  - "预算不够"
  - "别人家便宜"
strategy:
  name: 价值重构法
  steps:
    - step: 1
      action: 先认同客户的顾虑
      script: "我理解您的顾虑，价格确实是一个重要考虑因素。"
    - step: 2
      action: 了解客户的真实预算
      script: "您理想的预算是多少？我可以帮您看看有没有合适的方案。"
    - step: 3
      action: 展示价值而非降价
      script: "这个方案可以帮助您平均下来每天只需要3.3元。"
    - step: 4
      action: 提供分期/套餐选项
      script: "我们还有分期付款方案，可以减轻一次性支付的压力。"
forbidden_behaviors:
  - 直接降价
  - 争辩客户不懂价值
  - 过早推套餐
evidence:
  source_materials:
    - material-20260617-153000
  drill_records: []
  review_records: []
metrics:
  drills: 0
  field_tests: 0
  wins: 0
  losses: 0
  avg_score: 0
  last_used_at: ""
created_at: 2026-06-17T15:30:00
updated_at: 2026-06-17T15:30:00
trained_at: ""
tested_at: ""
mature_at: ""
retired_at: ""
---

# 价格异议处理-价值重构法

## 解决的问题
客户以"太贵了"为由拒绝购买时，如何有效回应。

## 信号识别
当客户说出以下关键词时，激活此 Skill：
- "太贵了"
- "预算不够"
- "别人家便宜"

## 执行步骤

### 步骤 1：认同顾虑
"我理解您的顾虑，价格确实是一个重要考虑因素。"

### 步骤 2：了解真实预算
"您理想的预算是多少？我可以帮您看看有没有合适的方案。"

### 步骤 3：展示价值
"这个方案可以帮助您平均下来每天只需要3.3元。"

### 步骤 4：提供选项
"我们还有分期付款方案，可以减轻一次性支付的压力。"

## 禁用行为
- 直接降价
- 争辩客户不懂价值
- 过早推套餐

## 验证方式
- 客户是否继续对话
- 客户是否询问更多细节
- 最终是否成交
```

---

## 阶段 4：演练（Drill）

### Drill 1

**命令**：
```bash
skill-forge drill --skill skill-20260617-153000 --persona "预算不足型客户" --rounds 3
```

**结果**：
- Diagnosis: 75
- Response Quality: 70
- Next Step Control: 65
- Risk Control: 80
- **平均分: 72.5**
- **结果: 部分成功**

**演练记录**：
```yaml
---
id: drill-20260617-160000
skill_id: skill-20260617-153000
created_at: 2026-06-17T16:00:00
scenario: 预算不足型客户
rating: 72
result: partial_success
scores:
  diagnosis: 75
  response_quality: 70
  next_step_control: 65
  risk_control: 80
feedback: "客户表达了预算顾虑，但销售在步骤3展示了价值后，客户仍然犹豫。建议在步骤2后增加预算分期的选项。"
---
```

### Drill 2

**结果**：
- Diagnosis: 80
- Response Quality: 75
- Next Step Control: 70
- Risk Control: 85
- **平均分: 77.5**
- **结果: 成功**

### Drill 3

**结果**：
- Diagnosis: 85
- Response Quality: 80
- Next Step Control: 80
- Risk Control: 90
- **平均分: 83.75**
- **结果: 成功**

---

## 阶段 5：状态流转 → trained

**系统检测**：
- drills >= 3 ✅
- avg_score >= 60 ✅
- schema 校验通过 ✅
- applicable_scenarios 至少 1 个 ✅
- customer_signals 至少 1 个 ✅
- forbidden_behaviors 至少 1 个 ✅

**自动流转**：`draft` → `trained`

**更新后的 Skill**：
```yaml
status: trained
metrics:
  drills: 3
  field_tests: 0
  wins: 2
  losses: 1
  avg_score: 77.9
trained_at: 2026-06-17T16:30:00
```

---

## 阶段 6：实战复盘（Review）

### Review 1

**命令**：
```bash
skill-forge review --file samples/current-chat.md --result "推进" --skill skill-20260617-153000
```

**复盘记录**：
```yaml
---
id: review-20260617-170000
skill_id: skill-20260617-153000
created_at: 2026-06-17T17:00:00
outcome:
  next_step: true
  deal_progress: advanced
  customer_sentiment: neutral_positive
adherence:
  followed_steps:
    - 1
    - 2
    - 3
  missed_steps:
    - 4
failure_points:
  - 销售没有主动提供分期选项
skill_defects:
  - 缺少"客户犹豫时如何推进"分支
update_recommendations:
  - 在步骤3和步骤4之间增加"客户犹豫时的追问"步骤
scores:
  adherence: 75
  outcome: 80
  improvement: 70
  skill_defect: 60
total_score: 72
result: advance
---
```

**复盘结果分析**：

| 维度 | 分数 | 说明 |
|------|------|------|
| adherence | 75 | 执行了3/4步骤 |
| outcome | 80 | 推进到下一步 |
| improvement | 70 | 相比演练有进步 |
| skill_defect | 60 | Skill 缺少分支 |

**可执行更新建议**：

1. 在步骤3和步骤4之间增加步骤：
   ```yaml
   - step: 3.5
     action: 追问客户犹豫原因
     script: "您还有其他顾虑吗？除了价格之外。"
   ```

2. 补充"客户犹豫时"分支：
   ```yaml
   applicable_scenarios:
     - 客户表达预算顾虑后犹豫
   ```

---

## 阶段 7：状态流转 → tested

**系统检测**：
- field_tests >= 1 ✅
- review 结果为"推进" ✅
- evidence.review_records 至少 1 条 ✅

**自动流转**：`trained` → `tested`

---

## 阶段 8：版本更新（v1.1.0）

**根据复盘建议更新 Skill**：

```yaml
version: 1.1.0
parent_version: 1.0.0
change_type: minor
change_reason: 复盘发现缺少"客户犹豫时追问"步骤
changed_by: review-20260617-170000
strategy:
  steps:
    - step: 1
      action: 先认同客户的顾虑
      script: "我理解您的顾虑，价格确实是一个重要考虑因素。"
    - step: 2
      action: 了解客户的真实预算
      script: "您理想的预算是多少？我可以帮您看看有没有合适的方案。"
    - step: 3
      action: 展示价值而非降价
      script: "这个方案可以帮助您平均下来每天只需要3.3元。"
    - step: 4
      action: 追问犹豫原因
      script: "您还有其他顾虑吗？除了价格之外。"
    - step: 5
      action: 提供分期/套餐选项
      script: "我们还有分期付款方案，可以减轻一次性支付的压力。"
```

---

## 阶段 9：多次实战

### Review 2-5

| Review | 结果 | Score | 改进点 |
|--------|------|-------|--------|
| review-2 | 推进 | 78 | 步骤4追问有效 |
| review-3 | 成交 | 85 | 完整执行 |
| review-4 | 推进 | 80 | 客户犹豫时追问 |
| review-5 | 成交 | 88 | 完整执行 |

**累计指标**：
- field_tests: 5
- wins: 3
- losses: 2
- win_rate: 60%
- avg_score: 79.4

---

## 阶段 10：状态流转 → mature

**系统检测**：
- field_tests >= 5 ✅
- wins / field_tests >= 0.6 ✅
- 近 3 次 review 没有"严重失败" ✅
- metrics.avg_score >= 70 ✅

**自动流转**：`tested` → `mature`

**最终状态**：
```yaml
status: mature
metrics:
  drills: 3
  field_tests: 5
  wins: 3
  losses: 2
  avg_score: 79.4
  last_used_at: 2026-06-17T20:00:00
mature_at: 2026-06-17T20:00:00
```

---

## 阶段 11：推荐使用

### 推荐记录

```yaml
---
id: recommend-20260618-100000
created_at: 2026-06-18T10:00:00
source_path: current-chat.md
matched_skills:
  - skill_id: skill-20260617-153000
    skill_name: 价格异议处理-价值重构法
    relevance: 92
    confidence: 0.85
    explanation: |
      1. 当前对话命中客户信号："太贵了"、"预算有限"
      2. 客户仍有购买意向，没有明确拒绝
      3. 当前阶段是方案报价后，适合价值重构
      4. 历史相似场景使用成功率：60%
      5. 风险提醒：不要直接承诺降价
    risk_warnings:
      - 不要直接降价
      - 不要争辩客户不懂价值
---
```

---

## 总结

| 阶段 | 动作 | 状态变化 |
|------|------|---------|
| 1. 原始案例 | - | - |
| 2. 导入案例 | ingest | material-xxx |
| 3. 提炼 Skill | distill | draft |
| 4. 演练 3 次 | drill | draft |
| 5. 状态流转 | 自动 | trained |
| 6. 实战复盘 | review | trained |
| 7. 状态流转 | 自动 | tested |
| 8. 版本更新 | update | v1.1.0 |
| 9. 多次实战 | review x4 | tested |
| 10. 状态流转 | 自动 | mature |
| 11. 推荐使用 | recommend | - |

**关键数据**：
- 从 draft 到 mature：7 次 drill/review
- 版本从 v1.0.0 到 v1.1.0：1 次更新
- 最终胜率：60%
- 最终平均分：79.4
