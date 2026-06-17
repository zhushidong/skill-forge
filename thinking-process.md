# Thinking Process - Skill Forge 沙盘攻防

## 项目概述
skill-forge 是一个本地 CLI 工具，用于将业务资料和外部 Agent 精炼为可训练、可演练、可审核的商业 Skill。

## 攻防策略

### 攻击者角色（深渊）
- **目标**：找到所有安全漏洞，构造可执行的 exploit
- **风格**：零容忍、实战思维、链式攻击
- **输出**：漏洞编号、攻击向量、exploit 代码、影响范围、修复建议

### 防御者角色（铁壁Pro）
- **目标**：确认漏洞真实性、给出修复代码、验证修复效果
- **风格**：绝不认怂、但也要反击夸大其词、给修复代码
- **输出**：判定结果、严重性调整、修复状态、修复代码

---

## 第一轮攻防

### 深渊审计结果
| 级别 | 数量 | 问题 |
|------|------|------|
| Critical | 3 | parsers.py路径未验证、LLM注入绕过、.env泄露 |
| High | 4 | 符号链接绕过、YAML反序列化、TOCTOU、模板注入 |
| Medium | 5 | 错误信息泄露、YAML注入、会话劫持、source_path、目录竞态 |
| Low | 5 | 最佳实践违反 |

### 铁壁Pro判定
| 判定 | 结果 |
|------|------|
| C1 parsers.py | 真实存在，必须立即修复 |
| C2 LLM注入 | 真实存在，必须立即修复 |
| C3 .env泄露 | 夸大其词，.gitignore已防护 |
| H1 符号链接 | 真实存在，本周修复 |
| H2 YAML反序列化 | 夸大其词，yaml.dump是安全的 |
| H3 TOCTOU | 真实存在，本周修复 |
| H4 模板注入 | 真实存在，本周修复 |

### 第一轮修复
1. **C1**: parsers.py 添加 `_validate_path()` 强制路径校验
2. **C2**: llm.py 增强 `sanitize_user_input()` 过滤编码绕过
3. **H1**: storage.py `safe_read_file()` 检查符号链接目标文件大小
4. **H3**: storage.py `safe_read_file()` 使用原子读取避免 TOCTOU
5. **H4**: templates.py `_escape_template_syntax()` 转义模板语法

---

## 第二轮攻防

### 深渊审计结果
| 级别 | 数量 | 问题 |
|------|------|------|
| Critical | 3 | Unicode绕过LLM过滤、错误信息泄露路径、TOCTOU竞态 |

### 铁壁Pro判定
| 判定 | 结果 |
|------|------|
| C1 Unicode绕过 | 真实存在，必须立即修复 |
| C2 错误信息泄露 | 夸大其词，攻击者没读懂代码 |
| C3 TOCTOU竞态 | 真实存在，必须立即修复 |

### 第二轮修复
1. **C1**: llm.py 添加 `unicodedata.normalize('NFKC')` 标准化 + 零宽字符剥离
2. **C3**: storage.py `safe_read_file()` 移除 `stat()` 前置检查，改为先 open 后检查
3. **C2**: llm.py `sanitize_error_message()` 移除死代码，统一返回用户友好消息

---

## 核心教训

### 1. 路径验证必须用绝对路径
- **问题**：使用相对路径 `Path("data")` 依赖 CWD，攻击者可通过 symlink 绕过
- **解决**：使用 `Path(__file__).parent.parent.resolve()` 推导绝对路径

### 2. 输入净化要处理编码绕过
- **问题**：简单的字符串匹配可被 Unicode 同形异义词、零宽空格绕过
- **解决**：添加 `unicodedata.normalize('NFKC')` + 零宽字符剥离

### 3. 文件读取必须原子化
- **问题**：先 `stat()` 检查再 `open()` 读取存在 TOCTOU 竞态窗口
- **解决**：直接 `open()` 读取，读取后再检查大小

### 4. 错误消息不能泄露原始信息
- **问题**：过滤后的错误信息可能仍包含敏感路径
- **解决**：统一返回用户友好消息，从不返回原始错误

### 5. 测试是验证修复的唯一方式
- **问题**：修复可能引入新问题或破坏现有功能
- **解决**：每次修复后运行完整测试套件验证

---

## 攻防流程 SOP

### 攻击者流程
1. **阅读所有代码**：理解项目架构和数据流
2. **识别攻击面**：CLI参数、文件读写、LLM调用、YAML解析
3. **构造exploit**：每个漏洞给出可复制执行的攻击代码
4. **演示链式攻击**：展示如何组合漏洞实现最大危害
5. **给出修复建议**：具体到代码行的修复方案

### 防御者流程
1. **逐一回应**：对每个漏洞给出判定结果
2. **区分真实/夸大**：不认怂但也不背锅
3. **给出修复代码**：可直接复制执行的修复代码
4. **验证修复效果**：运行测试确保修复有效

### 修复流程
1. **阅读漏洞报告**：理解攻击向量和影响
2. **设计修复方案**：考虑边界条件和兼容性
3. **实现修复**：修改代码并添加注释
4. **更新测试**：确保修复后测试通过
5. **验证修复**：运行完整测试套件

---

## 文件变更记录

### 第一轮修复
| 文件 | 变更 |
|------|------|
| `.gitignore` | 新增：排除 `.env`、`data/`、Python缓存 |
| `config.py` | 使用 `Path(__file__).parent.parent.resolve()` 推导绝对路径 |
| `storage.py` | 新增 `safe_read_file()` + `_validate_path()` + `MAX_FILE_SIZE` |
| `llm.py` | 新增 `sanitize_user_input()` + `sanitize_error_message()` |
| `parsers.py` | 新增 `_validate_path()` + `MAX_FILE_SIZE` |
| `templates.py` | 新增 `_escape_template_syntax()` |
| `commands/*.py` | 所有命令使用 `safe_read_file()` |

### 第二轮修复
| 文件 | 变更 |
|------|------|
| `llm.py` | 添加 `unicodedata.normalize('NFKC')` + 零宽字符剥离 |
| `llm.py` | `sanitize_error_message()` 移除死代码，统一返回用户友好消息 |
| `storage.py` | `safe_read_file()` 移除 `stat()` 前置检查，改为原子读取 |

---

## 测试覆盖

| 模块 | 测试数 | 覆盖内容 |
|------|--------|---------|
| `test_storage.py` | 20 | 路径校验、文件大小限制、Markdown读写、slugify、timestamp_id |
| `test_llm.py` | 19 | 输入清洗、输出消毒、错误脱敏、fallback prompt |
| `test_validation.py` | 10 | Material/Skill/Drill/Review schema校验 |
| **总计** | **49** | **全部通过** |

---

## 第三轮审计（遗漏检查）

### 审计官发现的问题
| 问题 | 严重性 | 状态 |
|------|--------|------|
| parsers.py `stat()` TOCTOU 未修复 | High | 已修复 |
| templates.py `template_name` 路径遍历 | High | 已修复 |
| parsers.py 与 storage.py 代码重复 | Medium | 已修复 |

### 第三轮修复
1. **parsers.py**: 移除重复的 `_validate_path()` 和 `MAX_FILE_SIZE`，改为从 `storage.py` 导入
2. **parsers.py**: 移除 `stat()` 前置检查，改为原子读取（与 `storage.py` 一致）
3. **templates.py**: 添加 `_validate_template_name()` 验证模板名称，防止路径遍历

---

## 第四轮：Skill 提炼

### 提炼的 Skills
| Skill | 文件 | 用途 |
|-------|------|------|
| 安全审计 | `data/skills/trained/skill-20260617-224100.md` | 系统性发现安全漏洞 |
| 沙盘攻防 | `data/skills/trained/skill-20260617-224200.md` | 模拟真实攻击发现漏洞 |
| 安全修复 | `data/skills/trained/skill-20260617-224300.md` | 安全地修复代码漏洞 |

### Skill 格式规范
- YAML Front Matter: id, name, version, status, scenes, signals, customer_types, drills, field_tests, wins, losses, created_at, trained_at, tested_at
- Markdown Body: 解决的问题、信号识别、执行步骤、核心原则、验证方式

---

## 最终修复汇总

### Critical 漏洞修复（6个）
| 编号 | 修复内容 | 文件 |
|------|---------|------|
| C1 | parsers.py 添加 `_validate_path()` | parsers.py |
| C2 | llm.py 增强 `sanitize_user_input()` | llm.py |
| C3 | Unicode NFKC 标准化 + 零宽字符剥离 | llm.py |
| C4 | 路径穿越（绝对路径） | config.py |
| C5 | 模板注入 | templates.py |
| C6 | 模板路径遍历 | templates.py |

### High 漏洞修复（4个）
| 编号 | 修复内容 | 文件 |
|------|---------|------|
| H1 | 符号链接绕过 | storage.py |
| H2 | TOCTOU 竞态 | storage.py, parsers.py |
| H3 | 模板注入 | templates.py |
| H4 | 模板路径遍历 | templates.py |

### Medium 漏洞修复（3个）
| 编号 | 修复内容 | 文件 |
|------|---------|------|
| M1 | 错误信息泄露 | llm.py |
| M2 | source_path 暴露路径 | commands/*.py |
| M3 | 代码重复 | parsers.py |

---

## 核心原则（最终版）

1. **路径验证必须用绝对路径** - 消除 symlink 绕过风险
2. **输入净化要处理编码绕过** - 使用 Unicode NFKC 标准化
3. **文件读取必须原子化** - 消除 TOCTOU 竞态窗口
4. **错误消息不能泄露原始信息** - 统一返回用户友好消息
5. **模板名称必须验证** - 防止路径遍历攻击
6. **代码不要重复** - 复用已有安全函数
7. **测试是验证修复的唯一方式** - 每次修复后运行完整测试套件
