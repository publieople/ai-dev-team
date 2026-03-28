---
name: ai-dev-team
description: |
  AI 驱动的自主开发团队管理系统（v1.1.0 OpenClaw 原生多 Agent 架构）。

  架构：
  - 人类 = 甲方（验收决策）
  - 主 Agent = CEO（统筹规划，使用 sessions_spawn 创建子 Agent）
  - 子 Agent = 员工（Developer/Tester/Researcher，隔离会话执行）

  核心功能：
  1. 项目自动分析与任务发现
  2. 状态机驱动的任务生命周期管理（13 状态）
  3. OpenClaw sessions_spawn 创建隔离子 Agent
  4. Git 可追溯提交（带元数据）
  5. 分层上报与人类决策集成
  6. 完整报告系统（分析/执行/测试/调研）
  7. Context7 文档集成
  8. 自动化测试验证
  9. 子 Agent 监控（/subagents list/log）
  10. 沙箱隔离和工具策略

  使用场景：
  - 自主开发和维护 Git 仓库
  - 日常代码优化和重构
  - Bug 修复和新特性开发
  - 技术债务管理

  依赖技能：
  - context7 (可选，用于文档收集)

  配置需求：
  - 需要在 gateway.config.json 中配置 4 个 Agent
  - 详见 references/openclaw-multiagent-config.md
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
@ai-dev-team start              # 手动批准模式
@ai-dev-team start --auto-approve  # 自动批准模式
```

### 5. 验收任务

```bash
# 查看待验收任务
@ai-dev-team approve

# 批准任务
@ai-dev-team approve --task-id=t-123 --approved=true

# 拒绝任务
@ai-dev-team approve --task-id=t-123 --approved=false
```

## 命令参考

| 命令          | 说明         | 参数                                          |
| ------------- | ------------ | --------------------------------------------- |
| `init`        | 初始化项目   | `[--path=.]`                                  |
| `analyze`     | 分析项目     | `[--path=.]`                                  |
| `plan`        | 生成规划     | `[--path=.]`                                  |
| `start`       | 开始开发循环 | `[--path=.]`, `[--auto-approve]`              |
| `status`      | 查看状态     | `[--path=.]`                                  |
| `approve`     | 验收任务     | `[--path=.]`, `[--task-id=]`, `[--approved=]` |
| `escalations` | 查看上报     | `[--path=.]`                                  |
| `research`    | 文档调研     | `[--library=]`, `[--query=]`                  |

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
- 子 Agent 指派（Developer/Tester/Researcher）
- 验收决策、异常上报
- 开发循环管理

**实现:** `scripts/main_agent.py`

### Developer Agent (开发工程师)

- 读取任务卡片和相关代码
- 实现功能/修复 Bug
- 运行自测
- 生成执行报告

**实现:** `scripts/developer_agent.py`

### Tester Agent (测试工程师)

- 审查代码变更（git diff）
- 运行测试套件（pytest/npm test）
- 检查执行报告完整性
- 生成测试报告
- 检测敏感信息泄露

**实现:** `scripts/tester_agent.py`

### Researcher Agent (文档研究员)

- 使用 Context7 收集官方 API 文档
- 搜索本地文档缓存
- 缓存技术文档
- 生成调研报告

**实现:** `scripts/researcher_agent.py`

## 报告系统

- **项目分析报告** - 技术栈识别、任务发现
- **执行报告** - 任务完成情况
- **日报** - 每日开发总结
- **上报报告** - 需要人类决策的问题

## 目录结构

```
.ai-dev-team/
├── config.json       # 配置
├── state.json        # 状态机
├── tasks/            # 任务卡片
├── reports/          # 报告（分析/执行/测试/调研）
├── docs/             # 文档缓存（Context7 等）
├── logs/             # 日志
└── README.md         # 项目说明
```

### 技能目录

```
skills/ai-dev-team/
├── index.py          # 命令行入口
├── SKILL.md          # 技能说明
├── scripts/
│   ├── main_agent.py       # 主 Agent
│   ├── developer_agent.py  # 开发 Agent
│   ├── tester_agent.py     # 测试 Agent
│   ├── researcher_agent.py # 调研 Agent
│   ├── state_manager.py    # 状态管理
│   └── git_wrapper.py      # Git 封装
├── agents/           # Agent 角色定义 (SOUL.md)
├── assets/
│   ├── configs/      # 默认配置
│   └── templates/    # 报告模板
└── references/       # 参考文档
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
