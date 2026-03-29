# AI Dev Team - 配置与测试指南

> **v1.2.0** - 提示词驱动版本

---

## 📋 目标

完成本指南后，你将能够：
1. 配置 4 个 Agent
2. 初始化项目
3. 测试主 Agent 自主创建子 Agent

---

## 🔧 第一步：配置 Agent

### 1.1 编辑 gateway.config.json

找到你的配置文件：
- Windows: `~/.openclaw/gateway.config.json`
- 或 `~/.openclaw/openclaw.json`

### 1.2 添加 4 个 Agent

复制以下配置到 `agents.list` 数组中：

```json
{
  "id": "ai-dev-team-main",
  "name": "AI Dev Team CEO",
  "default": false,
  "workspace": "~/.openclaw/workspace-projects",
  "sandbox": {
    "mode": "off"
  },
  "subagents": {
    "allowAgents": [
      "ai-dev-team-developer",
      "ai-dev-team-tester",
      "ai-dev-team-researcher"
    ],
    "model": "bailian/qwen3.5-plus",
    "thinking": "off",
    "maxConcurrent": 1
  }
},
{
  "id": "ai-dev-team-developer",
  "name": "Developer Agent",
  "default": false,
  "workspace": "~/.openclaw/workspace-projects",
  "sandbox": {
    "mode": "all",
    "scope": "session"
  },
  "tools": {
    "allow": ["read", "write", "edit", "apply_patch", "exec", "process", "web_search", "web_fetch"],
    "deny": ["gateway", "cron", "sessions_list", "sessions_history", "sessions_send"]
  }
},
{
  "id": "ai-dev-team-tester",
  "name": "Tester Agent",
  "default": false,
  "workspace": "~/.openclaw/workspace-projects",
  "sandbox": {
    "mode": "all",
    "scope": "session"
  },
  "tools": {
    "allow": ["read", "exec", "process"],
    "deny": ["write", "edit", "apply_patch", "gateway", "cron", "sessions_list"]
  }
},
{
  "id": "ai-dev-team-researcher",
  "name": "Researcher Agent",
  "default": false,
  "workspace": "~/.openclaw/workspace-projects",
  "sandbox": {
    "mode": "all",
    "scope": "session"
  },
  "tools": {
    "allow": ["read", "write", "web_search", "web_fetch"],
    "deny": ["exec", "edit", "apply_patch", "gateway", "cron"]
  }
}
```

### 1.3 添加 Binding

在 `bindings` 数组中添加：

```json
{
  "agentId": "ai-dev-team-main",
  "match": {
    "provider": "webchat",
    "accountId": "*",
    "peer": {
      "kind": "direct"
    }
  }
}
```

### 1.4 添加工具策略（可选）

在 `tools` 对象中添加：

```json
"tools": {
  "subagents": {
    "tools": {
      "deny": ["gateway", "cron"]
    }
  }
}
```

### 1.5 添加定时验收（可选）

在 `cron.jobs` 数组中添加：

```json
{
  "id": "ai-dev-team-daily-review",
  "name": "AI Dev Team 每日验收",
  "schedule": {
    "kind": "cron",
    "expr": "0 20 * * *",
    "tz": "Asia/Shanghai"
  },
  "payload": {
    "kind": "systemEvent",
    "text": "【定时验收提醒】\n\nAI Dev Team 主 Agent，现在是每日验收时间（20:00）。\n\n请检查：\n1. 有待验收的任务吗？\n2. 有已完成的开发需要测试吗？\n3. 需要发送日报给人类吗？\n\n如有待验收任务，请生成验收报告并发送给人类。"
  },
  "sessionTarget": "main",
  "enabled": true
}
```

### 1.6 保存并重启

```bash
openclaw gateway restart
```

---

## 📁 第二步：准备测试项目

### 2.1 创建测试项目

```bash
# 创建工作目录
mkdir -p ~/.openclaw/workspace-projects/test-project
cd ~/.openclaw/workspace-projects/test-project

# 初始化 Git
git init

# 创建简单文件
echo "# Test Project" > README.md
echo "print('Hello, World!')" > main.py

# 提交
git add .
git commit -m "Initial commit"
```

### 2.2 切换到主 Agent

在 webchat 中发送：

```
切换到 ai-dev-team-main
```

或直接发送：

```
@ai-dev-team-main 初始化 AI Dev Team
```

---

## 🚀 第三步：初始化项目

### 3.1 发送初始化命令

在 webchat 中发送：

```
初始化 AI Dev Team
```

### 3.2 预期响应

主 Agent 应该：

1. 检查 `.git` 目录存在
2. 创建 `.ai-dev-team/` 目录结构
3. 创建 `config.json` 和 `state.json`
4. 发送确认消息

```markdown
✅ AI Dev Team 已初始化

**项目:** test-project
**路径:** /path/to/test-project

下一步：我将分析项目并生成任务列表。
```

### 3.3 检查目录结构

```bash
ls -la .ai-dev-team/
# 应该看到：
# config.json
# state.json
# tasks/
# reports/
# docs/
# logs/
```

---

## 🔍 第四步：项目分析

### 4.1 触发分析

如果主 Agent 没有自动分析，发送：

```
分析这个项目
```

### 4.2 预期响应

主 Agent 应该：

1. 扫描项目结构
2. 识别技术栈（Python）
3. 生成分析报告
4. 发送任务列表请批准

```markdown
🔍 项目分析完成

**技术栈:** Python
**文件数:** 2

## 发现的任务

1. 添加 .gitignore
2. 添加配置文件
3. 添加单元测试

**请批准开始开发**
回复 `批准` 或 `✅`
```

### 4.3 批准规划

回复：

```
批准
```

---

## 🤖 第五步：创建子 Agent（关键测试）

### 5.1 主 Agent 应该做什么

批准后，主 Agent 应该：

1. 创建任务卡片 `.ai-dev-team/tasks/t-001.json`
2. 调用 `sessions_spawn` 创建 Developer Agent
3. 更新任务状态为 `IN_PROGRESS`

### 5.2 检查子 Agent 创建

在新消息中发送：

```
/subagents list
```

应该看到类似：

```
运行中的子 Agent:
- dev-001 (ai-dev-team-developer) - 运行中
```

### 5.3 查看子 Agent 日志

```
/subagents log dev-001
```

应该看到 Developer Agent 正在：
1. 读取任务卡片
2. 查看项目文件
3. 创建 .gitignore

---

## ✅ 第六步：验收流程

### 6.1 等待子 Agent 完成

Developer Agent 完成后会生成报告：
`.ai-dev-team/reports/execution-t-001.md`

### 6.2 主 Agent 审查

主 Agent 应该：
1. 读取执行报告
2. 审查变更

### 6.3 发送验收请求

主 Agent 发送：

```markdown
# 验收请求 - t-001

**任务:** 添加 .gitignore
**执行 Agent:** dev-001

## 变更
- 新增 `.gitignore`

## 执行报告
[详细内容]

## 请批准
回复 `批准` 或 `✅` 即可提交
```

### 6.4 批准提交

回复：

```
批准
```

### 6.5 检查 Git 提交

```bash
git log --oneline
# 应该看到：
# [AI-t-001] chore: 添加 .gitignore
```

---

## 🐛 故障排查

### 问题 1: 主 Agent 没有响应

**检查:**
- Agent ID 是否正确
- Binding 配置是否正确
- Gateway 是否重启

**解决:**
```bash
openclaw status
openclaw gateway restart
```

### 问题 2: sessions_spawn 失败

**错误:** `sessions_spawn is not available`

**检查:**
- 主 Agent 的 `subagents.allowAgents` 配置
- 子 Agent ID 是否在列表中

**解决:** 确认配置中有：
```json
"subagents": {
  "allowAgents": ["ai-dev-team-developer", "ai-dev-team-tester", "ai-dev-team-researcher"]
}
```

### 问题 3: 子 Agent 工具被拒绝

**错误:** `Tool exec is denied`

**检查:** 子 Agent 的 `tools.deny` 配置

**解决:** 确认 Developer Agent 的 `tools.allow` 包含 `exec`

### 问题 4: 主 Agent 不创建子 Agent

**可能原因:**
- 主 Agent 没有理解 SKILL.md
- `sessions_spawn` 调用格式错误

**解决:**
1. 检查主 Agent 是否读取了 SKILL.md
2. 手动提示：`请创建 Developer Agent 执行任务 t-001`

---

## 📊 成功标准

完成本指南后，应该能够：

- [x] 配置 4 个 Agent
- [x] 初始化项目
- [x] 主 Agent 自动分析项目
- [x] 主 Agent 创建子 Agent
- [x] 子 Agent 执行任务
- [x] 主 Agent 发送验收请求
- [x] 人类批准后 Git 提交

---

## 🎯 下一步

成功后：

1. **测试更多任务** - Bug 修复、新功能开发
2. **配置心跳** - 定期检查项目状态
3. **集成 Context7** - Researcher Agent 获取官方文档
4. **优化报告** - HTML/网页格式

---

*AI Dev Team v1.2.0 - 配置与测试指南*
