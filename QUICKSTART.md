# AI Dev Team - 快速开始指南

> 5 分钟配置，让你的 AI 自主开发团队跑起来

---

## 📋 前置条件

- [ ] OpenClaw 已安装并运行
- [ ] 有一个 Git 项目（或准备创建）
- [ ] 了解基本的 OpenClaw 配置

---

## 🚀 第一步：配置 Agent（5 分钟）

### 1.1 复制配置示例

```bash
# 找到你的 gateway.config.json
# Windows: ~/.openclaw/gateway.config.json
# 或编辑 openclaw.json

# 复制 skills/ai-dev-team/references/gateway.config.example.json 的内容
```

### 1.2 添加 4 个 Agent

在配置文件中添加：

```json
{
  "agents": {
    "list": [
      {
        "id": "ai-dev-team-main",
        "name": "AI Dev Team CEO",
        "workspace": "~/.openclaw/workspace-projects",
        "subagents": {
          "allowAgents": ["ai-dev-team-developer", "ai-dev-team-tester", "ai-dev-team-researcher"],
          "maxConcurrent": 1
        }
      },
      {
        "id": "ai-dev-team-developer",
        "name": "Developer Agent",
        "workspace": "~/.openclaw/workspace-projects",
        "sandbox": {"mode": "all"},
        "tools": {
          "allow": ["read", "write", "edit", "exec"],
          "deny": ["gateway", "cron"]
        }
      },
      {
        "id": "ai-dev-team-tester",
        "name": "Tester Agent",
        "workspace": "~/.openclaw/workspace-projects",
        "sandbox": {"mode": "all"},
        "tools": {
          "allow": ["read", "exec"],
          "deny": ["write", "edit"]
        }
      },
      {
        "id": "ai-dev-team-researcher",
        "name": "Researcher Agent",
        "workspace": "~/.openclaw/workspace-projects",
        "sandbox": {"mode": "all"},
        "tools": {
          "allow": ["read", "write", "web_search"],
          "deny": ["exec"]
        }
      }
    ]
  },
  "bindings": [
    {
      "agentId": "ai-dev-team-main",
      "match": {"provider": "webchat", "accountId": "*"}
    }
  ]
}
```

### 1.3 重启 Gateway

```bash
openclaw gateway restart
```

---

## 📁 第二步：初始化项目（1 分钟）

### 2.1 进入项目目录

```bash
cd /path/to/your/project
```

### 2.2 确保是 Git 仓库

```bash
git init  # 如果还没有初始化
git add .
git commit -m "Initial commit"
```

### 2.3 初始化 AI Dev Team

在 webchat 中发送：

```
初始化 AI Dev Team
```

或者手动运行：

```bash
python ~/.openclaw/workspace/skills/ai-dev-team/scripts/init_project.py
```

### 2.4 检查目录结构

```
.ai-dev-team/
├── config.json    ✓
├── state.json     ✓
├── tasks/         ✓
├── reports/       ✓
├── docs/          ✓
└── logs/          ✓
```

---

## 🤖 第三步：开始开发（自动）

### 3.1 主 Agent 自动分析

主 Agent 会：
1. 扫描项目结构
2. 识别技术栈
3. 生成任务列表
4. 发送分析报告给你

### 3.2 审阅规划

你会收到类似消息：

```markdown
# 项目分析报告

**技术栈:** Python + FastAPI

## 发现的任务

1. 添加 .gitignore
2. 创建配置文件
3. 添加单元测试框架

## 开发规划

[详细规划]

请批准开始开发
```

### 3.3 批准规划

回复：

```
批准
```

或

```
✅
```

### 3.4 观察开发过程

主 Agent 会：
1. 创建 Developer Agent
2. 执行任务
3. 生成执行报告
4. 发送验收请求

---

## ✅ 第四步：验收任务

### 4.1 收到验收请求

```markdown
# 验收请求 - t-001

**任务:** 添加 .gitignore
**执行 Agent:** dev-001

## 变更
- 新增 `.gitignore`

## 执行报告
[详细内容]

请批准
```

### 4.2 批准提交

回复：

```
批准
```

主 Agent 会自动 Git 提交。

### 4.3 查看提交历史

```bash
git log --oneline
# [AI-t-001] chore: 添加 .gitignore
```

---

## ⏰ 第五步：配置定时验收（可选）

### 5.1 编辑 cron 配置

在 `gateway.config.json` 添加：

```json
{
  "cron": {
    "jobs": [
      {
        "id": "ai-dev-team-daily-review",
        "schedule": {
          "kind": "cron",
          "expr": "0 20 * * *"
        },
        "payload": {
          "kind": "systemEvent",
          "text": "【定时验收提醒】现在是每日验收时间（20:00），请检查有待验收的任务。"
        },
        "sessionTarget": "main"
      }
    ]
  }
}
```

### 5.2 重启 Gateway

```bash
openclaw gateway restart
```

---

## 🔍 监控和调试

### 查看子 Agent

```bash
# 列出运行中的子 Agent
/subagents list

# 查看日志
/subagents log dev-001

# 停止子 Agent
/subagents kill dev-001
```

### 查看项目状态

```bash
# 查看 state.json
cat .ai-dev-team/state.json

# 查看任务列表
ls .ai-dev-team/tasks/

# 查看报告
ls .ai-dev-team/reports/
```

### 常见问题

**Q: 子 Agent 没有创建？**
A: 检查 `gateway.config.json` 中 `subagents.allowAgents` 配置

**Q: 工具调用被拒绝？**
A: 检查子 Agent 的 `tools.deny` 配置

**Q: 验收提醒没有触发？**
A: 检查 cron 配置，确认 Gateway 已重启

---

## 📖 下一步

- 阅读 `references/architecture.md` 了解详细架构
- 阅读 `references/state-machine.md` 了解状态机
- 阅读 `SKILL.md` 了解完整功能

---

*AI Dev Team v1.1.0*
