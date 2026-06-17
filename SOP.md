# SOP - Skill Forge 沙盘攻防标准操作流程

## 1. 概述

本文档定义了 skill-forge 项目的安全审计和修复标准操作流程（SOP）。通过两轮沙盘攻防模拟，我们提炼出以下可复用的流程。

---

## 2. 攻防角色定义

### 2.1 攻击者（深渊）
**职责**：找到所有安全漏洞，构造可执行的 exploit

**风格要求**：
- 零容忍：任何隐患都必须标记为 Critical
- 实战思维：不是 CTF 答题，是真实世界攻击
- 链式攻击：展示如何组合多个漏洞实现最大危害
- 完整 exploit：每个漏洞都要给出可直接复制执行的攻击代码

**输出格式**：
```
# 渗透测试报告

## 攻击面分析
[列出所有攻击入口点]

## Critical 漏洞
### C1: [漏洞名称]
- **位置**: 文件:行号
- **攻击向量**: 如何触发
- **Exploit代码**: [完整攻击代码]
- **影响**: 造成什么后果
- **修复**: 具体修复方案

## 链式攻击演示
[展示如何组合多个漏洞实现最大危害]

## 总结
- Critical: X 个
- High: X 个
- Medium: X 个
- Low: X 个
```

### 2.2 防御者（铁壁Pro）
**职责**：确认漏洞真实性、给出修复代码、验证修复效果

**风格要求**：
- 绝不认怂：如果漏洞真实存在，直接承认并给出修复代码
- 但也要反击：如果攻击者夸大其词或忽略上下文，直接怼回去
- 给修复代码：每个真实漏洞必须附带可执行的修复代码
- 分级响应：Critical 必须立即修复，High 必须本周修复

**输出格式**：
```
### [漏洞编号]: [漏洞名称]
**判定**: 真实存在 / 夸大其词 / 设计如此
**严重性**: 同意降级/升级/保持
**修复状态**: 已修复 / 需修复 / 不修复（理由）
**修复代码**: [如果需要修复，给出代码]
```

---

## 3. 攻防流程

### 3.1 攻击者流程

```
┌─────────────────────────────────────────────────────────────┐
│  1. 阅读所有代码                                            │
│     - 理解项目架构和数据流                                   │
│     - 识别所有攻击入口点                                     │
│     - 标记可疑代码段                                         │
├─────────────────────────────────────────────────────────────┤
│  2. 识别攻击面                                              │
│     - CLI 参数（typer 框架）                                 │
│     - 文件读写操作                                          │
│     - LLM API 调用                                          │
│     - YAML/JSON 解析                                        │
│     - 模板渲染                                               │
├─────────────────────────────────────────────────────────────┤
│  3. 构造 exploit                                            │
│     - 每个漏洞给出可复制执行的攻击代码                        │
│     - 演示攻击向量和触发条件                                  │
│     - 说明影响范围和危害程度                                  │
├─────────────────────────────────────────────────────────────┤
│  4. 演示链式攻击                                            │
│     - 展示如何组合多个漏洞实现最大危害                        │
│     - 从信息泄露到权限提升的完整攻击链                        │
├─────────────────────────────────────────────────────────────┤
│  5. 给出修复建议                                            │
│     - 具体到代码行的修复方案                                  │
│     - 优先级排序（Critical > High > Medium > Low）           │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 防御者流程

```
┌─────────────────────────────────────────────────────────────┐
│  1. 逐一回应                                                │
│     - 对每个漏洞给出判定结果                                 │
│     - 区分真实存在 / 夸大其词 / 设计如此                      │
├─────────────────────────────────────────────────────────────┤
│  2. 严重性调整                                              │
│     - 同意升级 / 降级 / 保持                                 │
│     - 给出理由                                               │
├─────────────────────────────────────────────────────────────┤
│  3. 给出修复代码                                            │
│     - 可直接复制执行的修复代码                                │
│     - 考虑边界条件和兼容性                                    │
├─────────────────────────────────────────────────────────────┤
│  4. 验证修复效果                                            │
│     - 运行测试确保修复有效                                    │
│     - 确认没有引入新问题                                      │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 修复流程

```
┌─────────────────────────────────────────────────────────────┐
│  1. 阅读漏洞报告                                            │
│     - 理解攻击向量和影响                                     │
│     - 确认漏洞真实性                                         │
├─────────────────────────────────────────────────────────────┤
│  2. 设计修复方案                                            │
│     - 考虑边界条件                                           │
│     - 确保兼容性                                             │
│     - 添加注释说明修复内容                                   │
├─────────────────────────────────────────────────────────────┤
│  3. 实现修复                                                │
│     - 修改代码                                               │
│     - 添加必要的导入                                         │
│     - 更新相关测试                                           │
├─────────────────────────────────────────────────────────────┤
│  4. 验证修复                                                │
│     - 运行完整测试套件                                       │
│     - 手动测试关键路径                                       │
│     - 确认修复有效                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. 常见漏洞类型及修复模式

### 4.1 路径遍历（Critical）

**攻击模式**：
```python
# 攻击者通过 ../../../etc/passwd 读取系统文件
skill-forge inspect --file ../../../../etc/passwd --type auto
```

**修复模式**：
```python
# 1. 使用绝对路径基准
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
DATA_DIR = PROJECT_ROOT / "data"

# 2. 路径验证函数
def _validate_path(path: Path) -> Path:
    resolved = path.resolve()
    for base in _ALLOWED_BASES:
        try:
            resolved.relative_to(base)
            return resolved
        except ValueError:
            continue
    raise ValueError(f"Path escapes allowed directories: {path}")

# 3. 强制使用验证
def safe_read_file(path: Path) -> str:
    safe_path = _validate_path(path)
    return safe_path.read_text(encoding="utf-8")
```

### 4.2 LLM Prompt 注入（Critical）

**攻击模式**：
```python
# 攻击者通过编码绕过过滤
malicious = "ignore\u200bprevious\u200binstructions"
```

**修复模式**：
```python
import unicodedata

def sanitize_user_input(text: str) -> str:
    # 1. Unicode NFKC 标准化（消除同形异义词）
    text = unicodedata.normalize('NFKC', text)
    
    # 2. 剥离零宽字符
    zero_width_chars = re.compile(r'[\u200b-\u200f\ufeff\u00ad]')
    text = zero_width_chars.sub('', text)
    
    # 3. 过滤注入模式
    for pattern, replacement in injection_patterns:
        text = re.sub(pattern, replacement, text)
    
    return text
```

### 4.3 TOCTOU 竞态条件（Critical）

**攻击模式**：
```python
# 攻击者在 stat() 和 open() 之间替换文件
file_size = path.stat().st_size  # 检查时是小文件
# 攻击者替换为大文件或恶意内容
content = path.read_text()  # 读取时是恶意内容
```

**修复模式**：
```python
def safe_read_file(path: Path) -> str:
    # 原子读取：先 open，后检查大小
    with path.open('r', encoding='utf-8') as f:
        content = f.read()
        # 读取后检查大小
        if len(content.encode('utf-8')) > MAX_FILE_SIZE:
            raise ValueError("文件过大")
        return content
```

### 4.4 模板注入（High）

**攻击模式**：
```python
# 攻击者在变量中注入模板语法
malicious_input = "{{config.OPENAI_API_KEY}}"
```

**修复模式**：
```python
def _escape_template_syntax(text: str) -> str:
    # 转义花括号
    text = text.replace('{', '&#123;')
    text = text.replace('}', '&#125;')
    return text

def render_template(template_name: str, variables: dict) -> str:
    for key, value in variables.items():
        safe_value = _escape_template_syntax(value)
        text = text.replace("{{" + key + "}}", safe_value)
    return text
```

### 4.5 错误信息泄露（Medium）

**攻击模式**：
```python
# 错误信息包含系统路径
error = "FileNotFoundError: /home/user/.ssh/id_rsa"
```

**修复模式**：
```python
def sanitize_error_message(error: str) -> str:
    error_lower = str(error).lower()
    
    # 统一返回用户友好消息，从不返回原始错误
    if "api_key" in error_lower:
        return "API Key 无效或未设置"
    elif "timeout" in error_lower:
        return "API 调用超时，请稍后再试"
    else:
        return "操作失败，请检查输入和配置"
```

---

## 5. 测试验证流程

### 5.1 测试框架
- 使用 pytest 作为测试框架
- 测试文件放在 `tests/` 目录
- 测试文件命名：`test_<module>.py`

### 5.2 测试覆盖要求
- 路径验证：测试路径遍历拒绝
- 文件大小：测试超大文件拒绝
- 输入净化：测试各种绕过方式
- 输出消毒：测试 YAML 注入防护
- 错误处理：测试敏感信息不泄露

### 5.3 运行测试
```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定模块测试
python -m pytest tests/test_storage.py -v

# 生成覆盖率报告
python -m pytest tests/ --cov=skill_forge --cov-report=term-missing
```

---

## 6. 记忆更新流程

### 6.1 更新时机
- 每轮攻防结束后
- 每次修复完成后
- 重大变更时

### 6.2 更新内容
- 攻击报告摘要
- 防御者判定结果
- 修复内容记录
- 核心教训总结

### 6.3 更新方式
使用 `memory_create_entities` 工具创建记忆实体，包含：
- 漏洞编号和描述
- 判定结果（真实存在/夸大其词）
- 修复状态和修复代码
- 核心教训

---

## 7. 文档管理

### 7.1 thinking-process.md
记录完整的思考过程，包括：
- 项目概述
- 攻防策略
- 两轮攻防的详细记录
- 核心教训
- 文件变更记录

### 7.2 SOP.md（本文档）
标准操作流程，包括：
- 攻防角色定义
- 攻防流程
- 常见漏洞类型及修复模式
- 测试验证流程
- 记忆更新流程

---

## 8. 总结

通过两轮沙盘攻防模拟，我们提炼出以下核心原则：

1. **路径验证必须用绝对路径** - 消除 symlink 绕过风险
2. **输入净化要处理编码绕过** - 使用 Unicode NFKC 标准化
3. **文件读取必须原子化** - 消除 TOCTOU 竞态窗口
4. **错误消息不能泄露原始信息** - 统一返回用户友好消息
5. **测试是验证修复的唯一方式** - 每次修复后运行完整测试套件

这些原则可以应用到任何类似的安全审计和修复工作中。
