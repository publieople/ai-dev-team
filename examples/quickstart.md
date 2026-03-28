# 快速开始指南

5 分钟上手 AI Dev Team，让你的项目拥有自主开发能力！

---

## 前提条件

1. **Git 仓库** - 项目必须已初始化 Git
2. **OpenClaw** - 已安装 OpenClaw 并配置好技能系统
3. **Python 3.8+** - 运行 Agent 脚本

---

## Step 1: 安装技能

```bash
# 如果从 ClawHub 安装
clawhub install ai-dev-team

# 或本地使用（已在本 workspace）
# 技能位置：skills/ai-dev-team/
```

---

## Step 2: 初始化项目

```bash
# 进入你的项目目录
cd /path/to/your/project

# 初始化 AI Dev Team
@ai-dev-team init
```

**输出示例：**
```
[OK] 创建配置：.ai-dev-team/config.json
[OK] 创建状态：.ai-dev-team/state.json
[OK] 更新 .gitignore

[DONE] 项目初始化完成!
   目录：/path/to/your/project/.ai-dev-team

下一步：运行 '@ai-dev-team analyze' 开始项目分析
```

---

## Step 3: 分析项目

```bash
@ai-dev-team analyze
```

**主 Agent 将：**
1. 扫描项目文件结构
2. 识别技术栈（Python/JS/Rust 等）
3. 发现潜在优化点
4. 生成《项目分析报告》

**输出示例：**
```
🔍 开始项目分析...
✅ 分析完成！报告：.ai-dev-team/reports/project-analysis-20260328-210000.md

{
  "status": "success",
  "report": {
    "name": "my-project",
    "tech_stack": [{"name": "Python", "confidence": "high"}],
    "potential_tasks": [
      {"title": "创建 .gitignore 文件", "priority": "high"},
      {"title": "添加测试目录", "priority": "normal"}
    ]
  }
}
```

---

## Step 4: 生成规划

```bash
@ai-dev-team plan
```

**输出示例：**
```
{
  "status": "success",
  "plan_file": ".ai-dev-team/reports/dev-plan-v1.md",
  "task_count": 2,
  "message": "开发规划已生成，共 2 个任务",
  "next_step": "运行 '@ai-dev-team start' 开始开发循环"
}
```

---

## Step 5: 开始开发

### 方式 A：手动批准（推荐）

```bash
@ai-dev-team start
```

主 Agent 会等待你批准每个任务：

```
⏳ 等待人类批准任务：t-1234567890
   标题：创建 .gitignore 文件
批准此任务？(y/n): y

🤖 创建子 Agent: dev-001
⏳ 等待子 Agent 执行...
✅ 变更验证通过
✅ 任务完成，等待人类验收
```

### 方式 B：自动批准（谨慎使用）

```bash
@ai-dev-team start --auto-approve
```

⚠️ **注意**：自动批准会跳过人类确认，适合信任的小任务。

---

## Step 6: 验收任务

子 Agent 执行完成后，任务进入 `PENDING_HUMAN_TEST` 状态。

### 批准任务

```bash
@ai-dev-team approve --task-id=t-1234567890
```

**输出：**
```
✅ Git 提交：a1b2c3d - [AI-t-1234567890] chore: 创建 .gitignore 文件
✅ 任务 t-1234567890 已完成并提交
```

### 拒绝任务（返回重新分析）

```bash
@ai-dev-team approve --task-id=t-1234567890 --reject
```

---

## Step 7: 查看状态

```bash
@ai-dev-team status
```

**输出示例：**
```json
{
  "status": "success",
  "stats": {
    "total": 5,
    "completed": 2,
    "active": 1,
    "pending": 1,
    "escalated": 0
  },
  "tasks_by_state": {
    "C": [{"tid": "t-123", "title": "创建 .gitignore"}],
    "IP": [{"tid": "t-456", "title": "添加测试"}],
    "PA": [{"tid": "t-789", "title": "编写文档"}]
  }
}
```

---

## 完整工作流示例

```bash
# 1. 初始化
@ai-dev-team init

# 2. 分析项目
@ai-dev-team analyze

# 3. 生成规划
@ai-dev-team plan

# 4. 开始开发（手动批准）
@ai-dev-team start

# 5. 查看进度
@ai-dev-team status

# 6. 验收任务
@ai-dev-team approve --task-id=t-xxx

# 7. 继续开发循环
@ai-dev-team start
```

---

## 查看 Git 提交

```bash
# 查看所有 AI 提交
git log --grep="[AI-"

# 查看特定任务提交
git log --grep="AI-Task: t-xxx"

# 查看提交详情
git show <commit-hash>
```

---

## 常见问题

### Q: 子 Agent 执行失败怎么办？

A: 系统会自动重试（默认 3 次）。如果仍然失败，任务会进入 `ESCALATED` 状态，主 Agent 会生成上报报告等待人类决策。

### Q: 如何修改配置？

A: 编辑 `.ai-dev-team/config.json`：

```json
{
  "workflow": {
    "auto_approve": false,  // 改为 true 启用自动批准
    "max_retries": 5        // 增加重试次数
  }
}
```

### Q: 如何添加自定义任务？

A: 直接编辑 `.ai-dev-team/state.json`，或修改分析结果后重新运行 `plan`。

### Q: 子 Agent 在哪里运行？

A: 使用 OpenClaw 的 `sessions_spawn` 创建隔离会话。子 Agent 执行完成后自动销毁。

---

## 下一步

- 📚 阅读 [详细架构](../references/architecture.md)
- 🤖 了解 [Agent 角色](../references/agent-types.md)
- 🔧 查看 [配置选项](../README.md#配置)
- 📝 自定义 [报告模板](../assets/templates/)

---

*祝你使用愉快！遇到问题？查看 [故障排查](../references/troubleshooting.md)* ⚡
