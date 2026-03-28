---
name: ai-dev-team
description: |
  AI 驱动的自主开发团队管理系统。模拟真实软件公司架构：
  - 人类 = 甲方（验收决策）
  - 主 Agent = CEO（统筹规划）
  - 子 Agent = 员工（执行开发）
  
  核心功能：
  1. 项目自动分析与任务发现
  2. 状态机驱动的任务生命周期管理
  3. 单任务单 Agent 指派机制
  4. Git 可追溯提交（带元数据）
  5. 分层上报与人类决策集成
  6. 完整报告系统（分析/执行/日报/上报）
  
  使用场景：
  - 自主开发和维护 Git 仓库
  - 日常代码优化和重构
  - Bug 修复和新特性开发
  - 技术债务管理
---

# AI Dev Team - 自主开发团队

> **AI 软件公司模拟系统** - 主 Agent 统筹，子 Agent 执行，人类最终验收

## 核心架构

```
人类（甲方）
    ↓ 需求对齐 / 验收确认 / 异常决策
主 Agent（CEO）- 单项目专注
    ├─ 项目分析 → 生成规划
    ├─ 任务拆分 → 状态机管理
    ├─ 指派子 Agent（单任务单 Agent）
    ├─ 验收评估 → Git 提交
    └─ 异常上报 → 人类决策
        ↓
    子 Agent（员工）- 执行后销毁
        ├─ Developer（开发）
        ├─ Tester（测试）
        └─ Researcher（文档）
```

## 快速开始

### 1. 初始化项目

```bash
# 在 Git 项目根目录执行
@ai-dev-team init
```

### 2. 分析项目

```bash
@ai-dev-team analyze
```

### 3. 生成规划

```bash
@ai-dev-team plan
```

### 4. 开始开发

```bash
@ai-dev-team start
```

### 5. 验收任务

```bash
@ai-dev-team approve --task-id=<id>
```

## 命令参考

| 命令 | 说明 | 参数 |
|------|------|------|
| `init` | 初始化项目 | `[路径]` |
| `analyze` | 分析项目 | - |
| `plan` | 生成规划 | - |
| `start` | 开始开发循环 | `--auto-approve` |
| `status` | 查看状态 | - |
| `approve` | 验收任务 | `--task-id=<id>`, `--reject` |

## 状态机

```
DISCOVERED → ANALYZING → PLANNING → PENDING_APPROVAL → ASSIGNED 
                                                              ↓
COMPLETED ← TESTING ← IN_PROGRESS ←←←←←←←←←←←←←←←←←←←←←←┘

异常：IN_PROGRESS → 重试超限 → ESCALATED → 人类决策
```

## 配置

`.ai-dev-team/config.json`：

```json
{
  "workflow": {
    "auto_approve": false,
    "require_human_test": true,
    "max_retries": 3
  },
  "git": {
    "auto_commit": true,
    "traceability": true
  }
}
```

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

## Agent 角色

### Main Agent (CEO)
- 项目分析、任务规划
- 子 Agent 指派
- 验收决策、异常上报

### Developer Agent
- 读取任务卡片
- 实现功能
- 生成执行报告

### Tester Agent
- 审查代码变更
- 运行测试
- 生成测试报告

### Researcher Agent
- 收集官方文档
- 编写技术文档

## 报告系统

- **项目分析报告** - 技术栈识别、任务发现
- **执行报告** - 任务完成情况
- **日报** - 每日开发总结
- **上报报告** - 需要人类决策的问题

## 目录结构

```
.ai-dev-team/
├── config.json    # 配置
├── state.json     # 状态机
├── tasks/         # 任务卡片
├── reports/       # 报告
└── logs/          # 日志
```

## 扩展

### 添加 Agent 类型

在 `agents/` 目录创建新角色 SOUL.md。

### 自定义模板

在 `assets/templates/` 添加报告模板。

### 集成工具

- Context7 - API 文档
- GitHub Actions - CI/CD
- 多模态模型 - UI 验证

## 文档

- [详细架构](references/architecture.md)
- [状态机](references/state-machine.md)
- [任务协议](references/task-protocol.md)
- [Agent 类型](references/agent-types.md)
- [MVP 实现](references/mvp-implementation.md)
- [故障排查](references/troubleshooting.md)

## License

GPL-3.0
