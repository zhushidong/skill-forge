# Quick Start Guide

3 分钟体验 Skill Forge 完整链路。

## 前置条件

- Python 3.10+
- pip

## 步骤 1：安装

```bash
# 克隆仓库
git clone https://github.com/zhushidong/skill-forge.git
cd skill-forge

# 安装
pip install -e .
```

## 步骤 2：初始化

```bash
skill-forge init
```

输出：
```
✅ 已创建目录: data/materials/articles
✅ 已创建目录: data/skills/draft
...
✅ 已创建模板: templates/inspect.md
...
初始化完成！
```

## 步骤 3：导入一个案例

```bash
skill-forge ingest --type case --title "客户嫌贵案例" --file samples/case-price.md
```

输出：
```
导入成功：
  - ID: material-20260617-153000
  - 类型: case
  - 标题: 客户嫌贵案例
  - 路径: data/materials/cases/material-20260617-153000.md
```

## 步骤 4：把案例转成 Skill

```bash
skill-forge distill --material material-20260617-153000 --problem "客户嫌贵怎么应对"
```

**没有 API Key？** 命令会输出完整 Prompt，你可以：
1. 复制 Prompt 到 ChatGPT/Claude/Kimi
2. 把大模型的回复保存到文件
3. 再次运行命令，使用保存的文件

**有 API Key？** 创建 `.env` 文件：
```
OPENAI_API_KEY=你的key
OPENAI_MODEL=gpt-4.1-mini
```

## 步骤 5：演练 Skill

```bash
skill-forge drill --skill skill-20260617-153000 --persona "预算不足型客户" --rounds 3
```

这会模拟一个预算不足的客户，和你演练 3 轮。

## 步骤 6：查看结果

```bash
# 查看所有 Skill
skill-forge search

# 查看特定 Skill
skill-forge inspect --file data/skills/draft/skill-20260617-153000.md
```

## 完整示例脚本

```bash
#!/bin/bash
set -e

echo "=== Skill Forge Quick Start ==="

# 1. 初始化
echo "1. 初始化..."
skill-forge init

# 2. 导入案例
echo "2. 导入案例..."
skill-forge ingest --type case --title "客户嫌贵案例" --file samples/case-price.md

# 3. 查看导入的资料
echo "3. 查看资料..."
skill-forge search

# 4. 转成 Skill（需要 API Key 或手动复制 Prompt）
echo "4. 转成 Skill..."
echo "   如果没有 API Key，请手动复制 Prompt 到大模型"

# 5. 查看 Skill
echo "5. 查看 Skill..."
skill-forge search

echo "=== 完成！==="
```

## 下一步

- [阅读完整文档](../README.md)
- [了解 Skill 格式](skill-format.md)
- [查看安全特性](security.md)
