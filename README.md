# AI Dev Team - 自主开发团队

> **AI 软件公司模拟系统** - 主 Agent 统筹，子 Agent 执行，人类最终验收

## 快速开始

### 1. 配置 OpenClaw

确保 `~/.openclaw/openclaw.json` 中包含以下 Agent 配置：

```json5
{
  "agents": {
    "list": [
      {
        "id": "ai-dev-team-main",
        "name": "AI Dev Team CEO",
        "workspace": "~/.openclaw\\workspace-projects",
        "sandbox": { "mode": "off" },
        "subagents": {
          "allowAgents": ["ai-dev-team-developer", "ai-dev-team-tester", "ai-dev-team-researcher"],
          "model": "bailian/qwen3.5-plus",
          "thinking": "off",
          "maxConcurrent": 1
        }
      },
      {
        "id": "ai-dev-team-developer",
        "workspace": "~/.openclaw\\workspace-projects",
        "sandbox": { "mode": "all", "scope": "session" },
        "tools": {
          "allow": ["read", "write", "edit", "apply_patch", "exec", "process"],
          "deny": ["gateway", "cron", "sessions_*"]
        }
      },
      {
        "id": "ai-dev-team-tester",
        "workspace": "~/.openclaw\\workspace-projects",
        "sandbox": { "mode": "all", "scope": "session" },
        "tools": {
          "allow": ["read", "exec", "process"],
          "deny": ["write", "edit", "apply_patch"]
        }
      },
      {
        "id": "ai-dev-team-researcher",
        "workspace": "~/.openclaw\\workspace-projects",
        "sandbox": { "mode": "all", "scope": "session" },
        "tools": {
          "allow": ["read", "write", "web_search", "web_fetch"],
          "deny": ["exec", "edit", "apply_patch"]
        }
      }
    ],
    "defaults": {
      "subagents": {
        "model": "bailian/qwen3.5-plus",
        "thinking": "off",
        "archiveAfterMinutes": 60
      }
    }
  },
  "bindings": [
    {
      "agentId": "ai-dev-team-main",
      "match": {
        "provider": "webchat",
        "peer": { "kind": "direct" }
      }
    }
  ],
  "cron": {
    "jobs": [
      {
        "id": "ai-dev-team-daily-review",
        "name": "每日验收提醒",
        "schedule": {
          "kind": "cron",
          "expr": "0 20 * * *",
          "tz": "Asia/Shanghai"
        },
        "payload": {
          "kind": "systemEvent",
          "text": "📋 AI Dev Team 每日验收提醒：请检查 .ai-dev-team/reports/ 中的最新验收报告"
        },
        "sessionTarget": "main",
        "enabled": true
      }
    ]
  }
}
```

### 2. 初始化项目

在 Git 项目根目录运行：

```bash
# 通过聊天命令
@ai-dev-team init

# 或通过 Python 脚本
cd skills/ai-dev-team
python index.py init --path=/path/to/your/project
```

### 3. 分析项目

```bash
@ai-dev-team analyze
```

这会：
- 扫描项目结构
- 识别技术栈
- 发现潜在任务（测试、文档、配置等）
- 生成《项目分析报告》

### 4. 生成规划

```bash
@ai-dev-team plan
```

这会：
- 读取分析报告
- 生成开发规划
- 将任务状态改为 `PENDING_APPROVAL`

### 5. 开始开发

```bash
# 手动批准模式（推荐）
@ai-dev-team start

# 自动批准模式
@ai-dev-team start --auto-approve
```

开发流程：
1. 主 Agent 批准任务
2. 判断是否需要文档调研 → 创建 Researcher Agent
3. 创建 Developer Agent 执行开发
4. 创建 Tester Agent 验证
5. 等待人类验收

### 6. 验收任务

```bash
# 查看待验收任务
@ai-dev-team approve

# 批准任务
@ai-dev-team approve --task-id=t-123 --approved=true

# 拒绝任务
@ai-dev-team approve --task-id=t-123 --approved=false
```

### 7. 查看状态

```bash
@ai-dev-team status
```

---

## 命令参考

| 命令 | 说明 | 参数 |
|------|------|------|
| `init` | 初始化项目 | `[--path=.]` |
| `analyze` | 分析项目 | `[--path=.]` |
| `plan` | 生成规划 | `[--path=.]` |
| `start` | 开始开发循环 | `[--path=.]`, `[--auto-approve]` |
| `status` | 查看状态 | `[--path=.]` |
| `approve` | 验收任务 | `[--path=.]`, `[--task-id=]`, `[--approved=]` |
| `escalations` | 查看上报 | `[--path=.]` |
| `research` | 文档调研 | `[--library=]`, `[--query=]` |

---

## 状态机

```
DISCOVERED → ANALYZING → PLANNING → PENDING_APPROVAL → ASSIGNED
                                                              ↓
COMPLETED ← TESTING ← IN_PROGRESS ←←←←←←←←←←←←←←←←←←←←←←┘

异常：IN_PROGRESS → 重试超限 → ESCALATED → 人类决策
```

### 状态说明

| 状态 | 代码 | 说明 |
|------|------|------|
| DISCOVERED | `D` | 刚发现的任务 |
| ANALYZING | `A` | 正在分析 |
| PLANNING | `P` | 正在规划 |
| PENDING_APPROVAL | `PA` | 等待人类批准 |
| ASSIGNED | `AS` | 已指派给子 Agent |
| IN_PROGRESS | `IP` | 正在执行 |
| TESTING | `T` | 正在测试 |
| PENDING_HUMAN_TEST | `PHT` | 等待人类验收 |
| ESCALATED | `E` | 已上报（需要主 Agent 决策） |
| HUMAN_ESCALATION | `HE` | 已上报人类 |
| COMPLETED | `C` | 已完成 |
| CANCELLED | `X` | 已取消 |
| REASSIGNING | `R` | 重新指派中 |

---

## 目录结构

```
.ai-dev-team/
├── config.json       # 配置
├── state.json        # 状态机（TOON 格式）
├── tasks/            # 任务卡片
│   ├── t-xxx.json
│   └── t-yyy.json
├── reports/          # 报告
│   ├── project-analysis-*.md  # 项目分析报告
│   ├── development-plan-*.md  # 开发规划
│   ├── execution-t-xxx.md     # 执行报告
│   ├── research-t-xxx.md      # 调研报告
│   ├── test-t-xxx.md          # 测试报告
│   └── daily-*.md             # 日报
├── docs/             # 文档缓存
└── logs/             # Agent 日志
```

---

## Agent 角色

### 主 Agent (CEO)

**职责:**
- 项目分析和规划
- 创建和指派子 Agent
- 验收决策、异常上报
- 开发循环管理

**工具:** 全部可用

---

### Developer Agent (开发工程师)

**职责:**
- 读取任务卡片和相关代码
- 实现功能/修复 Bug
- 运行自测
- 生成执行报告

**工具:**
- ✅ 允许：`read`, `write`, `edit`, `apply_patch`, `exec`, `process`
- ❌ 禁止：`gateway`, `cron`, `sessions_*`

---

### Tester Agent (测试工程师)

**职责:**
- 审查代码变更（git diff）
- 运行测试套件
- 检查执行报告完整性
- 生成测试报告

**工具:**
- ✅ 允许：`read`, `exec`, `process`
- ❌ 禁止：`write`, `edit`, `apply_patch`（保证测试客观性）

---

### Researcher Agent (文档研究员)

**职责:**
- 使用 web_search/web_fetch 收集文档
- 缓存技术文档
- 生成调研报告

**工具:**
- ✅ 允许：`read`, `write`, `web_search`, `web_fetch`
- ❌ 禁止：`exec`, `edit`, `apply_patch`

---

## Git 可追溯

所有 AI 提交包含元数据：

```
[AI-t-123] feat: 添加功能

AI-Task: t-123
AI-Agent: dev-001
AI-Time: 2026-03-28T21:00:00
```

查询：
```bash
git log --grep="[AI-"
```

---

## 定时验收

默认每天 20:00 发送验收提醒。可在配置中修改：

```json5
{
  "cron": {
    "jobs": [
      {
        "id": "ai-dev-team-daily-review",
        "schedule": {
          "kind": "cron",
          "expr": "0 20 * * *",  // 每天 20:00
          "tz": "Asia/Shanghai"
        }
      }
    ]
  }
}
```

---

## 监控子 Agent

```bash
# 查看当前子 Agent
/subagents list

# 查看子 Agent 日志
/subagents log <id> 50

# 查看子 Agent 信息
/subagents info <id>

# 停止子 Agent
/subagents kill <id>
```

---

## 配置说明

### `.ai-dev-team/config.json`

```json
{
  "workflow": {
    "auto_approve": false,      // 是否自动批准任务
    "require_human_test": true, // 是否需要人类测试
    "max_retries": 3            // 最大重试次数
  },
  "escalation": {
    "threshold": 3              // 上报阈值（重试次数）
  },
  "git": {
    "auto_commit": true,        // 自动 Git 提交
    "traceability": true        // 可追溯元数据
  },
  "review": {
    "schedule": "0 20 * * *",   // 验收时间（cron 表达式）
    "timezone": "Asia/Shanghai"
  }
}
```

---

## 上报机制

### 上报条件

1. 重试次数达到阈值（默认 3 次）
2. 需要人类权限的操作
3. 重大决策（架构变更、依赖升级）
4. 未知问题无法解决

### 上报报告格式

```markdown
# 问题上报

**任务 ID:** t-123
**问题:** 依赖冲突无法解决
**影响:** 无法继续开发
**建议方案:**
1. 降级依赖版本
2. 等待上游修复
3. 寻找替代方案

**请甲方决策:** [选择方案/提供新指示]
```

---

## 最佳实践

### 1. 任务拆分

- 保持任务小而专注
- 每个任务应该有明确的交付物
- 避免跨多个模块的大任务

### 2. 文档优先

- 开发前先收集文档
- 使用 Researcher Agent 调研
- 缓存文档到 `.ai-dev-team/docs/`

### 3. 测试验证

- 每个任务都应该有测试
- Tester Agent 独立验证
- 人类最终验收

### 4. Git 提交

- 每次提交都可追溯
- 使用语义化提交信息
- 保留完整元数据

---

## 故障排查

### 子 Agent 无法创建

检查：
1. Agent 配置是否正确
2. `bindings` 是否匹配当前渠道
3. 工具策略是否允许

### 任务卡在 PENDING_APPROVAL

运行：
```bash
@ai-dev-team start --auto-approve
```

### 上报过多

检查：
1. 任务是否过大
2. 是否缺少必要文档
3. 是否需要调整配置

---

## 扩展

### 添加新的 Agent 类型

在 `agents/` 目录创建新角色：

```
agents/
└── specialist/
    └── SOUL.md
```

### 自定义报告模板

在 `assets/templates/` 添加模板。

### 集成工具

- Context7 - API 文档
- GitHub Actions - CI/CD
- 多模态模型 - UI 验证

---

## License

GPL-3.0

---

*AI Dev Team - 基于 OpenClaw 原生多 Agent 架构*
