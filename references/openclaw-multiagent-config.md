# OpenClaw 多 Agent 配置指南

> **重要:** 本技能需要使用 OpenClaw 的原生多 Agent 架构才能发挥完整功能。

---

## 📋 配置步骤

### 1. 添加 Agent 配置

在 `~/.openclaw/gateway.config.json` 或你的配置文件中添加：

```json5
{
  "agents": {
    "list": [
      {
        "id": "ai-dev-team-main",
        "name": "AI Dev Team CEO",
        "default": false,
        "workspace": "~/.openclaw/workspace-projects",
        "sandbox": {
          "mode": "off"  // 主 Agent 不需要沙箱
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
          "allow": ["read", "write", "edit", "apply_patch", "exec", "process"],
          "deny": ["gateway", "cron", "sessions_list", "sessions_history"]
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
          "deny": ["write", "edit", "apply_patch", "gateway", "cron"]
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
    ],
    "defaults": {
      "subagents": {
        "archiveAfterMinutes": 60,
        "model": "bailian/qwen3.5-plus",
        "thinking": "off"
      }
    }
  },
  "tools": {
    "subagents": {
      "tools": {
        "deny": ["gateway", "cron"]  // 子 Agent 禁止访问网关和定时任务
      }
    }
  },
  "bindings": [
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
  ]
}
```

---

## 🔧 配置说明

### 主 Agent (CEO)

```json5
{
  "id": "ai-dev-team-main",
  "workspace": "~/.openclaw/workspace-projects",  // 项目管理目录
  "subagents": {
    "allowAgents": ["ai-dev-team-developer", ...],  // 允许创建的子 Agent
    "maxConcurrent": 1,  // 同时只运行一个子 Agent
    "model": "bailian/qwen3.5-plus",  // 子 Agent 默认模型
    "thinking": "off"  // 关闭思考节省 token
  }
}
```

**职责:**

- 项目分析和规划
- 创建和指派子 Agent
- 验收和上报决策

**工具:** 全部可用（需要协调子 Agent）

---

### Developer Agent

```json5
{
  "id": "ai-dev-team-developer",
  "sandbox": {
    "mode": "all",  // 所有操作都在沙箱中
    "scope": "session"  // 每个会话一个沙箱
  },
  "tools": {
    "allow": ["read", "write", "edit", "apply_patch", "exec", "process"],
    "deny": ["gateway", "cron", "sessions_*"]  // 禁止访问网关和会话工具
  }
}
```

**职责:**

- 读取任务卡片
- 实现代码功能
- 运行测试
- 生成执行报告

**工具限制:**

- ✅ 允许：文件操作、命令执行
- ❌ 禁止：网关管理、定时任务、会话管理

---

### Tester Agent

```json5
{
  "id": "ai-dev-team-tester",
  "tools": {
    "allow": ["read", "exec", "process"],
    "deny": ["write", "edit", "apply_patch"]  // 禁止修改代码
  }
}
```

**职责:**

- 审查代码变更（git diff）
- 运行测试套件
- 检查执行报告
- 生成测试报告

**工具限制:**

- ✅ 允许：读取、执行测试
- ❌ 禁止：修改代码（保证测试客观性）

---

### Researcher Agent

```json5
{
  "id": "ai-dev-team-researcher",
  "tools": {
    "allow": ["read", "write", "web_search", "web_fetch"],
    "deny": ["exec", "edit", "apply_patch"]
  }
}
```

**职责:**

- 使用 Context7 收集文档
- 搜索网络资料
- 缓存技术文档
- 生成调研报告

**工具限制:**

- ✅ 允许：文件读取/写入、网络搜索
- ❌ 禁止：执行命令（不需要）

---

## 🚀 使用方式

### 1. 启动主 Agent

```bash
# 在 webchat 中直接使用
@ai-dev-team init
```

### 2. 监控子 Agent

```bash
# 查看当前子 Agent
/subagents list

# 查看子 Agent 日志
/subagents log <id>

# 查看子 Agent 信息
/subagents info <id>

# 停止子 Agent
/subagents kill <id>
```

### 3. 查看会话状态

```bash
/sessions list
```

---

## 📊 子 Agent 生命周期

```
1. Main Agent 调用 sessions_spawn
   ↓
2. OpenClaw 创建独立会话
   agent:ai-dev-team-developer:subagent:<uuid>
   ↓
3. 注入上下文（仅 AGENTS.md + TOOLS.md）
   ↓
4. 子 Agent 执行任务
   ↓
5. 完成后自动通告
   Status: success
   Result: 任务完成摘要
   Notes: sessionKey, runtime, tokens, cost
   ↓
6. 会话归档（60 分钟后）
```

---

## 🔐 安全配置

### 沙箱模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `off` | 无沙箱 | 主 Agent（需要完全访问） |
| `all` | 所有操作沙箱 | Developer/Tester/Researcher |
| `non-main` | 非主会话沙箱 | 一般场景 |

### 工具策略

**deny 优先原则:**

```json5
tools: {
  deny: ["gateway", "cron"],  // 这些工具永远不可用
  allow: ["read", "write"]     // 只允许这些工具（deny 优先）
}
```

### 认证隔离

每个 Agent 有独立的认证存储：

```
~/.openclaw/agents/ai-dev-team-main/agent/auth-profiles.json
~/.openclaw/agents/ai-dev-team-developer/agent/auth-profiles.json
```

**不要共享认证文件！**

---

## 💰 成本优化

### 模型配置

```json5
agents: {
  defaults: {
    subagents: {
      model: "bailian/qwen3.5-plus",  // 子 Agent 使用性价比模型
      thinking: "off"                  // 关闭思考节省 token
    }
  }
}
```

**建议:**

- 主 Agent: 高质量模型（如 `qwen3.5-plus`）
- 子 Agent: 性价比模型（如 `qwen3.5-plus` 或更便宜的）

### 并发控制

```json5
subagents: {
  maxConcurrent: 1  // 限制同时运行的子 Agent 数量
}
```

**原因:**

- 避免资源竞争
- 便于问题追溯
- 节省 token

### 自动归档

```json5
subagents: {
  archiveAfterMinutes: 60  // 60 分钟后自动归档
}
```

**好处:**

- 减少会话数量
- 节省存储空间
- 保持工作区整洁

---

## 🔍 监控和调试

### 查看子 Agent 状态

```bash
# 列出所有子 Agent
/subagents list

# 查看特定子 Agent 信息
/subagents info dev-001

# 查看日志
/subagents log dev-001 50  # 最后 50 行
/subagents log dev-001 50 --tools  # 包含工具调用
```

### 调试工具调用

如果子 Agent 的工具调用被阻止：

```bash
# 查看沙箱解释
openclaw sandbox explain <command>

# 检查工具策略
openclaw tools list --agent ai-dev-team-developer
```

### 查看会话历史

```bash
# 获取子 Agent 会话历史
sessions_history --sessionKey agent:ai-dev-team-developer:subagent:<uuid>
```

---

## ⚠️ 注意事项

### 1. 子 Agent 上下文限制

子 Agent **只注入**以下文件：

- ✅ `AGENTS.md`
- ✅ `TOOLS.md`

**不注入:**

- ❌ `SOUL.md`
- ❌ `IDENTITY.md`
- ❌ `USER.md`
- ❌ `HEARTBEAT.md`
- ❌ `BOOTSTRAP.md`

**原因:** 保持子 Agent 专注任务，避免不必要的上下文。

### 2. 子 Agent 不能生成子 Agent

```
Main Agent → Developer Agent ✅
Developer Agent → Sub-Sub-Agent ❌
```

**原因:** 避免嵌套扇出，难以控制。

### 3. 通告是尽力而为

如果 Gateway 重启，待处理的通告可能丢失。

**建议:** 重要结果写入文件（报告），不要仅依赖通告。

### 4. 认证不共享

每个 Agent 需要自己的认证配置。

**解决:** 复制 `auth-profiles.json` 到各 Agent 目录。

---

## 📖 参考文档

- [OpenClaw 子 Agent 文档](https://docs.openclaw.ai/zh-CN/tools/subagents)
- [多 Agent 沙箱配置](https://docs.openclaw.ai/zh-CN/tools/multi-agent-sandbox-tools)
- [沙箱隔离](https://docs.openclaw.ai/gateway/sandboxing)
- [工具策略](https://docs.openclaw.ai/gateway/tool-policy)

---

*AI Dev Team - 基于 OpenClaw 原生多 Agent 架构*
