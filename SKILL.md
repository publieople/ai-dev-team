---
name: ai-dev-team
description: AI 驱动的自主开发团队（v1.2.0 提示词驱动）。主 Agent 统筹规划，使用 sessions_spawn 创建子 Agent（Developer/Tester/Researcher）执行具体任务。支持项目分析、任务发现、自主开发、人类验收、Git 可追溯提交。
metadata:
  version: 1.2.0
  tags: ["autonomous-development", "multi-agent", "project-management", "ai-dev"]
---

# AI Dev Team

AI 驱动的自主开发团队管理系统（v1.2.0 提示词驱动）。

**架构：**
- 人类 = 甲方（验收决策）
- 主 Agent = CEO（统筹规划，使用 sessions_spawn 创建子 Agent）
- 子 Agent = 员工（Developer/Tester/Researcher，隔离会话执行）

## 快速开始

### 1. 配置 Agent

在 `gateway.config.json` 添加 4 个 Agent（参考 `references/gateway.config.example.json`）：

```json
{
  "agents": {
    "list": [
      {
        "id": "ai-dev-team-main",
        "subagents": {
          "allowAgents": ["ai-dev-team-developer", "ai-dev-team-tester", "ai-dev-team-researcher"],
          "maxConcurrent": 1
        }
      },
      // ... 其他 3 个 Agent
    ]
  }
}
```

### 2. 初始化项目

在 webchat 中发送：

```
初始化 AI Dev Team
```

主 Agent 会自动：
1. 检查 Git 项目
2. 创建 `.ai-dev-team/` 目录
3. 分析项目并生成任务列表
4. 等待批准后开始开发

## 核心功能

### 项目分析

主 Agent 自动扫描项目：
- 识别技术栈（Python/JavaScript/TypeScript 等）
- 统计文件数量和类型
- 查找配置文件
- 发现潜在任务（优化/修复/新功能）

### 任务管理

13 状态任务生命周期：

```
DISCOVERED → ANALYZING → PLANNING → PENDING_APPROVAL → ASSIGNED
                                                              ↓
COMPLETED ← TESTING ← IN_PROGRESS ←←←←←←←←←←←←←←←←←←←←←←┘
```

### 子 Agent 创建

主 Agent 使用 `sessions_spawn` 创建子 Agent：

```
sessions_spawn(
  agentId: "ai-dev-team-developer",
  task: "你是一个 Developer Agent，负责...",
  label: "dev-t-123",
  runTimeoutSeconds: 7200,
  mode: "run"
)
```

**子 Agent 类型：**

| 类型 | 职责 | 工具 |
|------|------|------|
| Developer | 写代码、修复 Bug | read/write/edit/exec |
| Tester | 运行测试、审查代码 | read/exec（禁止写） |
| Researcher | 收集文档、写报告 | read/write/web_search |

### 人类验收

关键节点等待人类批准：
- 项目规划
- 任务完成
- 架构级修改

**验收请求格式：**

```markdown
# 验收请求 - t-123

**任务:** 添加用户登录功能
**执行 Agent:** dev-001

## 变更
- 新增 `src/auth.py`

## 请批准
回复 `批准` 或 `✅` 即可提交
```

### Git 可追溯

所有提交带 AI 元数据：

```
[AI-t-123] feat: 添加用户登录功能

AI-Task: t-123
AI-Agent: dev-001
AI-Time: 2026-03-29T14:30:00+08:00
```

## 使用场景

- **自主开发和维护 Git 仓库** - AI 主动发现并执行任务
- **日常代码优化和重构** - 自动识别优化点
- **Bug 修复和新特性开发** - 子 Agent 执行具体开发
- **技术债务管理** - 持续改进代码质量

## 配置

### 项目配置

`.ai-dev-team/config.json`：

```json
{
  "workflow": {
    "auto_approve": false,
    "require_human_test": true,
    "max_retries": 3
  },
  "review": {
    "schedule": "0 20 * * *",
    "timezone": "Asia/Shanghai"
  }
}
```

### 定时验收

在 `gateway.config.json` 添加 cron 任务：

```json
{
  "cron": {
    "jobs": [
      {
        "id": "ai-dev-team-daily-review",
        "schedule": {
          "kind": "cron",
          "expr": "0 20 * * *",
          "tz": "Asia/Shanghai"
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

## 目录结构

```
.ai-dev-team/
├── config.json    # 配置
├── state.json     # 状态机
├── tasks/         # 任务卡片
├── reports/       # 报告
├── docs/          # 文档缓存
└── logs/          # 日志
```

## 决策边界

### 自主决定（不需要问人类）

- ✅ 代码重构和优化
- ✅ Bug 修复
- ✅ 添加/更新测试
- ✅ 文档更新
- ✅ 小版本依赖升级

### 需要人类批准

- ⚠️ 新功能开发规划
- ⚠️ 架构级修改
- ⚠️ 大重构
- ⚠️ 删除代码/数据

### 必须上报

- ❗ 任务连续失败 3 次
- ❗ 发现严重安全漏洞
- ❗ 需要外部 API 密钥
- ❗ 涉及敏感数据操作

## 监控子 Agent

```bash
# 查看运行中的子 Agent
/subagents list

# 查看日志
/subagents log dev-001

# 停止子 Agent
/subagents kill dev-001
```

## 最佳实践

### 项目初始化

确保项目是 Git 仓库：

```bash
git init
git add .
git commit -m "Initial commit"
```

### 任务审批

及时审批任务，避免阻塞：
- 收到验收请求后尽快回复
- 拒绝时说明具体原因
- 批准后可查看 Git 提交

### 干涉开发

随时可以干涉：

```
暂停当前任务，先修复 XXX Bug
```

### 查看进度

```
当前项目状态如何？
```

## 故障排查

### 子 Agent 没有创建

检查 `gateway.config.json`：
- `subagents.allowAgents` 是否包含子 Agent ID
- `bindings` 配置是否正确

### 工具调用被拒绝

检查子 Agent 的 `tools.deny` 配置

### 验收提醒没有触发

检查 cron 配置，确认 Gateway 已重启

## 文档

| 文档 | 说明 |
|------|------|
| [docs/QUICKSTART.md](docs/QUICKSTART.md) | 5 分钟快速开始 |
| [docs/SETUP_AND_TEST.md](docs/SETUP_AND_TEST.md) | 配置与测试指南 |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | 更新日志 |
| [references/architecture.md](references/architecture.md) | 详细架构设计 |
| [references/gateway.config.example.json](references/gateway.config.example.json) | 配置示例 |

## License

GPL-3.0
